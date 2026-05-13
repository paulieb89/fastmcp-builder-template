"""Tests for check_resource_mime_type_declared.

Spec source: FastMCP — `servers/resources.md` (the `mime_type=` kwarg lets
the client display the resource correctly without guessing). Severity MEDIUM
(FastMCP-recommended, not MCP-mandatory).
"""

from pathlib import Path

from fastmcp_builder.checks import check_resource_mime_type_declared
from fastmcp_builder.models import Severity


_HEADER = '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")
'''


def _write_server(tmp_path: Path, body: str) -> Path:
    f = tmp_path / "server.py"
    f.write_text(_HEADER + body)
    return f


def test_resource_with_mime_type_passes(tmp_path: Path) -> None:
    path = _write_server(
        tmp_path,
        '''
@mcp.resource("demo://thing", mime_type="application/json")
async def get_thing() -> str:
    """Get."""
    return "{}"
''',
    )
    report = check_resource_mime_type_declared(str(path))
    assert report.passed is True
    assert report.findings == []


def test_resource_without_mime_type_is_flagged(tmp_path: Path) -> None:
    """The common omission — relies on FastMCP's inferred type, which is brittle."""
    path = _write_server(
        tmp_path,
        '''
@mcp.resource("demo://thing")
async def get_thing() -> str:
    """Get."""
    return "{}"
''',
    )
    report = check_resource_mime_type_declared(str(path))
    assert report.passed is False
    assert len(report.findings) == 1
    f = report.findings[0]
    assert f.severity == Severity.MEDIUM
    assert f.code == "resource.missing_mime_type"
    assert f.path == "$.primitives.get_thing"
    assert f.spec_source == "FastMCP"
    assert f.spec_section and "resources" in f.spec_section


def test_resource_with_non_constant_mime_type_still_passes(tmp_path: Path) -> None:
    """We don't validate the value statically — only that the kwarg is present."""
    path = _write_server(
        tmp_path,
        '''
DYNAMIC = "application/json"

@mcp.resource("demo://thing", mime_type=DYNAMIC)
async def get_thing() -> str:
    """Get."""
    return "{}"
''',
    )
    report = check_resource_mime_type_declared(str(path))
    assert report.passed is True


def test_bare_decorator_without_call_is_flagged(tmp_path: Path) -> None:
    """`@mcp.resource` with no parens means no kwargs — mime_type can't be set."""
    path = _write_server(
        tmp_path,
        '''
@mcp.resource
async def get_thing() -> str:
    """Get."""
    return "{}"
''',
    )
    report = check_resource_mime_type_declared(str(path))
    assert report.passed is False
    assert len(report.findings) == 1
    assert report.findings[0].code == "resource.missing_mime_type"


def test_tools_and_prompts_ignored(tmp_path: Path) -> None:
    """The check is resource-only; tools and prompts are unaffected."""
    path = _write_server(
        tmp_path,
        '''
@mcp.tool
def t(x: str) -> str:
    """Tool."""
    return x

@mcp.prompt
def p(q: str) -> str:
    """Prompt."""
    return q
''',
    )
    report = check_resource_mime_type_declared(str(path))
    assert report.passed is True
    assert report.findings == []


def test_multiple_resources_mixed(tmp_path: Path) -> None:
    """One declared, one not — only the bare one is flagged."""
    path = _write_server(
        tmp_path,
        '''
@mcp.resource("demo://a", mime_type="application/json")
async def a() -> str:
    """A."""
    return "{}"

@mcp.resource("demo://b")
async def b() -> str:
    """B."""
    return "{}"
''',
    )
    report = check_resource_mime_type_declared(str(path))
    assert report.passed is False
    assert len(report.findings) == 1
    assert "b" in report.findings[0].path
