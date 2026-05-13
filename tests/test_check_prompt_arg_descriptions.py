"""Tests for check_prompt_argument_descriptions.

Spec source: MCP — `PromptArgument.description` field. Severity MEDIUM
(MCP says SHOULD, not MUST). Descriptions can come from either:

  - `Annotated[X, Field(description="...")]` on the parameter, or
  - A docstring `Args:` block (Google/NumPy style) naming the parameter.
"""

from pathlib import Path

from fastmcp_builder.checks import check_prompt_argument_descriptions
from fastmcp_builder.models import Severity


_HEADER = '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")
'''


def _write_server(tmp_path: Path, body: str) -> Path:
    f = tmp_path / "server.py"
    f.write_text(_HEADER + body)
    return f


def test_prompt_with_docstring_args_block_passes(tmp_path: Path) -> None:
    path = _write_server(
        tmp_path,
        '''
@mcp.prompt
def draft(slug: str, topic: str) -> str:
    """Draft.

    Args:
        slug: The authority slug.
        topic: What the request is about.
    """
    return ""
''',
    )
    report = check_prompt_argument_descriptions(str(path))
    assert report.passed is True
    assert report.findings == []


def test_prompt_with_annotated_field_descriptions_passes(tmp_path: Path) -> None:
    path = _write_server(
        tmp_path,
        '''
from typing import Annotated
from pydantic import Field

@mcp.prompt
def draft(
    slug: Annotated[str, Field(description="The authority slug.")],
    topic: Annotated[str, Field(description="What the request is about.")],
) -> str:
    """Draft."""
    return ""
''',
    )
    report = check_prompt_argument_descriptions(str(path))
    assert report.passed is True


def test_prompt_with_no_arg_descriptions_is_flagged(tmp_path: Path) -> None:
    """The wdtk pattern — one-line docstring, bare types, no descriptions."""
    path = _write_server(
        tmp_path,
        '''
@mcp.prompt
def draft(slug: str, topic: str, facts: str = "") -> str:
    """Draft a narrow request."""
    return ""
''',
    )
    report = check_prompt_argument_descriptions(str(path))
    assert report.passed is False
    # One finding per undescribed argument.
    assert len(report.findings) == 3
    for f in report.findings:
        assert f.severity == Severity.MEDIUM
        assert f.code == "prompt.argument_missing_description"
        assert f.spec_source == "MCP"
        assert "prompt" in f.spec_section.lower()
    # Argument names appear in the messages.
    messages = " ".join(f.message for f in report.findings)
    assert "slug" in messages
    assert "topic" in messages
    assert "facts" in messages


def test_partial_docstring_coverage_flags_only_undocumented(tmp_path: Path) -> None:
    """Docstring covers slug; topic is left undocumented → one finding."""
    path = _write_server(
        tmp_path,
        '''
@mcp.prompt
def draft(slug: str, topic: str) -> str:
    """Draft.

    Args:
        slug: The authority slug.
    """
    return ""
''',
    )
    report = check_prompt_argument_descriptions(str(path))
    assert report.passed is False
    assert len(report.findings) == 1
    assert "topic" in report.findings[0].message


def test_ctx_and_context_args_ignored(tmp_path: Path) -> None:
    """FastMCP injects ctx — it isn't a prompt argument from the model's POV."""
    path = _write_server(
        tmp_path,
        '''
from fastmcp import Context

@mcp.prompt
def draft(slug: str, ctx: Context) -> str:
    """Draft.

    Args:
        slug: The authority slug.
    """
    return ""
''',
    )
    report = check_prompt_argument_descriptions(str(path))
    assert report.passed is True


def test_tools_and_resources_ignored(tmp_path: Path) -> None:
    """The check is prompt-only."""
    path = _write_server(
        tmp_path,
        '''
@mcp.tool
def t(x: str) -> str:
    """One-liner."""
    return x

@mcp.resource("demo://r", mime_type="text/plain")
async def r() -> str:
    """One-liner."""
    return ""
''',
    )
    report = check_prompt_argument_descriptions(str(path))
    assert report.passed is True
    assert report.findings == []
