"""Tests for the silent-error-returns AST scanner.

A FastMCP tool that converts a failure into a "successful" response
shaped like an error (return {"error": ...}, return "Error: ...") defeats
the model's ability to distinguish a real result from a failure. The
convention is to raise (e.g. ToolError) so the protocol surfaces a
proper error response.
"""

from pathlib import Path

from fastmcp_builder.checks import (
    PATTERN_ERROR_DICT,
    PATTERN_ERROR_FSTRING,
    PATTERN_ERROR_STRING,
    check_silent_error_returns,
)
from fastmcp_builder.models import Severity


_HEADER = '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")
'''


def _write_server(tmp_path: Path, body: str) -> Path:
    """Write a server module with the standard FastMCP("Demo") header."""
    f = tmp_path / "server.py"
    f.write_text(_HEADER + body)
    return f


def test_tool_returning_error_dict_is_flagged(tmp_path: Path) -> None:
    """The exact pattern from govuk and wdtk: `return {"error": "..."}`."""
    path = _write_server(
        tmp_path,
        '''
@mcp.tool
def create_item(name: str) -> dict:
    """Create an item via the API."""
    if not _has_api_key():
        return {"error": "API key not configured."}
    return {"ok": True}
''',
    )
    report = check_silent_error_returns(str(path))

    assert report.passed is False
    assert len(report.findings) == 1
    finding = report.findings[0]
    assert finding.severity == Severity.HIGH
    assert finding.code == "tool.silent_error_return"
    assert finding.path == "$.primitives.create_item"
    assert PATTERN_ERROR_DICT in finding.message


def test_tool_returning_error_string_is_flagged(tmp_path: Path) -> None:
    """The bailii pattern: `return "Error: ..."` from inside a tool body."""
    path = _write_server(
        tmp_path,
        '''
@mcp.tool
async def search_things(query: str) -> str:
    """Search the upstream."""
    try:
        return await _fetch(query)
    except Exception:
        return "Error: upstream unavailable"
''',
    )
    report = check_silent_error_returns(str(path))

    assert report.passed is False
    assert len(report.findings) == 1
    finding = report.findings[0]
    assert finding.path == "$.primitives.search_things"
    assert PATTERN_ERROR_STRING in finding.message


def test_tool_returning_error_fstring_is_flagged(tmp_path: Path) -> None:
    """Error sentinels often interpolate the exception, e.g. f'Error: {e}'."""
    path = _write_server(
        tmp_path,
        '''
@mcp.tool
def get_item(id: int) -> str:
    """Get an item by id."""
    try:
        return _lookup(id)
    except KeyError as e:
        return f"Error: not found ({e})"
''',
    )
    report = check_silent_error_returns(str(path))

    assert report.passed is False
    assert len(report.findings) == 1
    assert PATTERN_ERROR_FSTRING in report.findings[0].message


def test_clean_tool_that_raises_is_not_flagged(tmp_path: Path) -> None:
    """A tool that raises on failure is the correct shape and must not fire."""
    path = _write_server(
        tmp_path,
        '''
from fastmcp.exceptions import ToolError

@mcp.tool
def create_item(name: str) -> dict:
    """Create an item via the API."""
    if not _has_api_key():
        raise ToolError("API key not configured.")
    return {"ok": True, "name": name}
''',
    )
    report = check_silent_error_returns(str(path))

    assert report.passed is True
    assert report.findings == []


def test_non_tool_function_is_not_scanned(tmp_path: Path) -> None:
    """A plain helper function returning an error dict is a private
    implementation detail — only @mcp.tool functions matter to the model."""
    path = _write_server(
        tmp_path,
        '''
def _internal_helper(reason: str) -> dict:
    """Returning an error dict in a private helper is fine."""
    return {"error": reason}

@mcp.tool
def healthy(name: str) -> dict:
    """Delegates to the helper but raises on error."""
    result = _internal_helper(name)
    if "error" in result:
        raise RuntimeError(result["error"])
    return result
''',
    )
    report = check_silent_error_returns(str(path))

    assert report.passed is True


def test_finding_reports_line_number(tmp_path: Path) -> None:
    """The offending source line is embedded in the finding message."""
    path = _write_server(
        tmp_path,
        '''
@mcp.tool
def x() -> dict:
    """Tool."""
    return {"error": "boom"}
''',
    )
    report = check_silent_error_returns(str(path))

    # _HEADER is 4 lines (blank, import, blank, mcp = ...) — the offending
    # return lands at line 9 of the assembled file.
    assert "line 9" in report.findings[0].message


def test_tool_returning_via_error_helper_is_flagged(tmp_path: Path) -> None:
    """The bailii pattern: tool delegates to a same-module helper that itself
    returns error-shaped sentinels."""
    path = _write_server(
        tmp_path,
        '''
def _handle_error(e):
    if isinstance(e, TimeoutError):
        return "Error: Request timed out."
    return f"Error: {type(e).__name__}: {e}"

@mcp.tool
async def fetch_thing(slug: str) -> str:
    """Fetch a thing."""
    try:
        return await _fetch(slug)
    except Exception as e:
        return _handle_error(e)
''',
    )
    report = check_silent_error_returns(str(path))

    assert report.passed is False
    assert len(report.findings) == 1
    finding = report.findings[0]
    assert finding.path == "$.primitives.fetch_thing"
    # Indirect-helper label names the helper.
    assert "_handle_error" in finding.message


def test_indirect_call_to_clean_helper_is_not_flagged(tmp_path: Path) -> None:
    """A helper that returns plain data (no error sentinels) should not trigger."""
    path = _write_server(
        tmp_path,
        '''
def _format_result(data):
    return {"ok": True, "data": data}

@mcp.tool
def get_thing(slug: str) -> dict:
    """Get."""
    return _format_result(_fetch(slug))
''',
    )
    report = check_silent_error_returns(str(path))

    assert report.passed is True


def test_multiple_findings_in_same_file(tmp_path: Path) -> None:
    """One finding per offending return — two error returns = two findings."""
    path = _write_server(
        tmp_path,
        '''
@mcp.tool
def tool_a() -> dict:
    """A."""
    return {"error": "boom"}

@mcp.tool
def tool_b() -> str:
    """B."""
    return "Error: also boom"
''',
    )
    report = check_silent_error_returns(str(path))

    assert len(report.findings) == 2
    paths = {f.path for f in report.findings}
    assert paths == {"$.primitives.tool_a", "$.primitives.tool_b"}
