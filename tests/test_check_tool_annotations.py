"""Tests for check_tool_annotations_declared.

Spec source: MCP — `ToolAnnotations` field on Tool. Severity MEDIUM
(MCP says optional but recommended; hosts use these hints to render
the tool, ask for confirmation on destructive ones, etc.).
"""

from pathlib import Path

from fastmcp_builder.checks import check_tool_annotations_declared
from fastmcp_builder.models import Severity


_HEADER = '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")
'''


def _write_server(tmp_path: Path, body: str) -> Path:
    f = tmp_path / "server.py"
    f.write_text(_HEADER + body)
    return f


def test_tool_with_full_annotations_passes(tmp_path: Path) -> None:
    path = _write_server(
        tmp_path,
        '''
@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def lookup(q: str) -> str:
    """Lookup."""
    return ""
''',
    )
    report = check_tool_annotations_declared(str(path))
    assert report.passed is True
    assert report.findings == []


def test_tool_with_no_annotations_kwarg_is_flagged(tmp_path: Path) -> None:
    path = _write_server(
        tmp_path,
        '''
@mcp.tool
def lookup(q: str) -> str:
    """Lookup."""
    return ""
''',
    )
    report = check_tool_annotations_declared(str(path))
    assert report.passed is False
    assert len(report.findings) == 1
    f = report.findings[0]
    assert f.severity == Severity.MEDIUM
    assert f.code == "tool.missing_annotations"
    assert f.path == "$.primitives.lookup"
    assert f.spec_source == "MCP"
    assert "annotations" in f.spec_section.lower()


def test_tool_with_partial_annotations_is_flagged(tmp_path: Path) -> None:
    """A tool that sets some but not all four standard hints — flag with the
    missing list so the author knows what to add."""
    path = _write_server(
        tmp_path,
        '''
@mcp.tool(annotations={"readOnlyHint": True})
def lookup(q: str) -> str:
    """Lookup."""
    return ""
''',
    )
    report = check_tool_annotations_declared(str(path))
    assert report.passed is False
    assert len(report.findings) == 1
    msg = report.findings[0].message
    # Names the missing hints.
    assert "destructiveHint" in msg
    assert "idempotentHint" in msg
    assert "openWorldHint" in msg


def test_tool_with_non_constant_annotations_passes(tmp_path: Path) -> None:
    """A non-literal annotations value (e.g. a constant defined elsewhere)
    can't be analysed statically — give it the benefit of the doubt."""
    path = _write_server(
        tmp_path,
        '''
STD_ANNOTATIONS = {"readOnlyHint": True}

@mcp.tool(annotations=STD_ANNOTATIONS)
def lookup(q: str) -> str:
    """Lookup."""
    return ""
''',
    )
    report = check_tool_annotations_declared(str(path))
    assert report.passed is True


def test_resources_and_prompts_ignored(tmp_path: Path) -> None:
    """The check is tool-only — annotations are a Tool concept in MCP."""
    path = _write_server(
        tmp_path,
        '''
@mcp.resource("demo://thing", mime_type="text/plain")
async def r() -> str:
    """R."""
    return ""

@mcp.prompt
def p(q: str) -> str:
    """P."""
    return q
''',
    )
    report = check_tool_annotations_declared(str(path))
    assert report.passed is True
    assert report.findings == []
