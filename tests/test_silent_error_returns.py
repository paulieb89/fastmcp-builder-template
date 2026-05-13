"""Tests for the silent-error-returns AST scanner.

A FastMCP tool that converts a failure into a "successful" response
shaped like an error (return {"error": ...}, return f"Error: ...")
defeats the model's ability to distinguish a real result from a
failure. The convention is to raise (e.g. ToolError) so the
protocol surfaces a proper error response.

These tests drive the scanner that catches the pattern in source.
"""

from pathlib import Path

import pytest

from fastmcp_builder.checks import check_silent_error_returns


def _write(tmp_path: Path, source: str) -> Path:
    f = tmp_path / "server.py"
    f.write_text(source)
    return f


def test_tool_returning_error_dict_is_flagged(tmp_path: Path) -> None:
    """The exact pattern from govuk and wdtk: `return {"error": "..."}`."""
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")

@mcp.tool
def create_item(name: str) -> dict:
    """Create an item via the API."""
    if not _has_api_key():
        return {"error": "API key not configured."}
    return {"ok": True}
''',
    )
    report = check_silent_error_returns(str(path))
    assert report["passed"] is False
    findings = report["findings"]
    assert len(findings) == 1
    assert findings[0]["tool"] == "create_item"
    assert "error" in findings[0]["pattern"].lower()


def test_tool_returning_error_string_is_flagged(tmp_path: Path) -> None:
    """The bailii pattern: `return "Error: ..."` from a helper, used inside a tool."""
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")

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
    assert report["passed"] is False
    assert len(report["findings"]) == 1
    assert report["findings"][0]["tool"] == "search_things"
    assert "error" in report["findings"][0]["pattern"].lower()


def test_tool_returning_error_fstring_is_flagged(tmp_path: Path) -> None:
    """Error sentinels often interpolate the exception, e.g. f'Error: {e}'."""
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")

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
    assert report["passed"] is False
    assert len(report["findings"]) == 1
    assert "f-string" in report["findings"][0]["pattern"]


def test_clean_tool_that_raises_is_not_flagged(tmp_path: Path) -> None:
    """A tool that raises on failure is the correct shape and must not fire."""
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

mcp = FastMCP("Demo")

@mcp.tool
def create_item(name: str) -> dict:
    """Create an item via the API."""
    if not _has_api_key():
        raise ToolError("API key not configured.")
    return {"ok": True, "name": name}
''',
    )
    report = check_silent_error_returns(str(path))
    assert report["passed"] is True
    assert report["findings"] == []


def test_non_tool_function_is_not_scanned(tmp_path: Path) -> None:
    """A plain helper function (no @mcp.tool decorator) returning an error dict
    is a private implementation detail, not a tool contract — leave it alone."""
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")

def _internal_helper(reason: str) -> dict:
    """A private helper. Returning an error dict here is fine — it's
    not what the model sees."""
    return {"error": reason}

@mcp.tool
def healthy(name: str) -> dict:
    """A clean tool that delegates to the helper but raises if needed."""
    result = _internal_helper(name)
    if "error" in result:
        raise RuntimeError(result["error"])
    return result
''',
    )
    report = check_silent_error_returns(str(path))
    assert report["passed"] is True


def test_finding_reports_line_number(tmp_path: Path) -> None:
    """Line numbers are useful for pointing at the offending return."""
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")

@mcp.tool
def x() -> dict:
    """Tool."""
    return {"error": "boom"}
''',
    )
    report = check_silent_error_returns(str(path))
    assert report["findings"][0]["line"] == 9


def test_tool_returning_via_error_helper_is_flagged(tmp_path: Path) -> None:
    """The bailii pattern: tool delegates to a same-module helper that itself
    returns error-shaped sentinels. The tool body has only `return _handle_error(e)`
    but the model still sees the error string."""
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")


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
    assert report["passed"] is False
    assert len(report["findings"]) == 1
    finding = report["findings"][0]
    assert finding["tool"] == "fetch_thing"
    assert "via" in finding["pattern"].lower() or "helper" in finding["pattern"].lower()


def test_indirect_call_to_clean_helper_is_not_flagged(tmp_path: Path) -> None:
    """A helper that returns plain data (no error sentinels) should not trigger."""
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")


def _format_result(data):
    return {"ok": True, "data": data}


@mcp.tool
def get_thing(slug: str) -> dict:
    """Get."""
    return _format_result(_fetch(slug))
''',
    )
    report = check_silent_error_returns(str(path))
    assert report["passed"] is True


def test_multiple_findings_in_same_file(tmp_path: Path) -> None:
    """Reports one finding per offending return — two error returns = two findings."""
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")

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
    assert len(report["findings"]) == 2
    tools = {f["tool"] for f in report["findings"]}
    assert tools == {"tool_a", "tool_b"}
