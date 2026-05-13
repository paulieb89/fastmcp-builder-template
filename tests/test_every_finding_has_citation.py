"""End-to-end Success Criterion test for the mcp-compliance-checks spec.

Spec section: "Every ReviewFinding produced by the plugin carries a non-empty
`spec_source` and `spec_section` (or explicit 'opinion' tag)."

Strategy: feed a deliberately broken server fixture into every check the
design-review skill auto-fires (Layer 2 of SKILL.md). Each check is expected
to produce findings — assert every finding has `spec_source is not None`.

The bundled `examples/notes_server.py` is intentionally clean so it'd give a
vacuously-true assertion; this fixture exists specifically to surface findings.
"""

from pathlib import Path

import pytest

from fastmcp_builder.checks import (
    check_prompt_argument_descriptions,
    check_resource_mime_type_declared,
    check_silent_error_returns,
    check_tool_annotations_declared,
)
from fastmcp_builder.extract import extract_manifest_from_source
from fastmcp_builder.review import review_fastmcp_manifest_data


_BROKEN_SERVER = '''
"""A deliberately broken FastMCP server. Triggers each of the auto-fired Layer 2
checks at least once so every finding code's citation is exercised."""
from fastmcp import FastMCP

mcp = FastMCP("BadName With Spaces")


# Bare @mcp.resource (no mime_type, no parens) — check_resource_mime_type_declared.
@mcp.resource("demo://a")
async def res_a() -> str:
    """A."""
    return ""


# @mcp.tool with no annotations= kwarg AND returns an error sentinel.
# Triggers check_tool_annotations_declared AND check_silent_error_returns.
@mcp.tool
def write_thing(name: str) -> dict:
    """Write."""
    if not name:
        return {"error": "name required"}
    return {"ok": True}


# @mcp.prompt with no Args block and bare typed parameters.
# Triggers check_prompt_argument_descriptions.
@mcp.prompt
def draft(slug: str, topic: str) -> str:
    """Draft."""
    return ""
'''


@pytest.fixture(scope="module")
def broken_server(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("broken") / "server.py"
    path.write_text(_BROKEN_SERVER)
    return path


def test_manifest_review_findings_all_have_citations(broken_server: Path) -> None:
    """review_fastmcp_manifest is the structural check — every finding it emits
    must carry a citation."""
    manifest = extract_manifest_from_source(str(broken_server))
    result = review_fastmcp_manifest_data(manifest)
    assert result.findings, "Expected the broken server to produce manifest findings."
    for f in result.findings:
        assert f.spec_source is not None, (
            f"Finding code='{f.code}' has no spec_source — citation missing."
        )


def test_silent_error_findings_all_have_citations(broken_server: Path) -> None:
    result = check_silent_error_returns(str(broken_server))
    assert result.findings, "Expected the broken server to produce silent-error findings."
    for f in result.findings:
        assert f.spec_source == "FastMCP"
        assert f.spec_section and "tools" in f.spec_section.lower()


def test_resource_mime_type_findings_all_have_citations(broken_server: Path) -> None:
    result = check_resource_mime_type_declared(str(broken_server))
    assert result.findings, "Expected the broken server to produce mime_type findings."
    for f in result.findings:
        assert f.spec_source == "FastMCP"
        assert f.spec_section and "resources" in f.spec_section.lower()


def test_prompt_arg_description_findings_all_have_citations(broken_server: Path) -> None:
    result = check_prompt_argument_descriptions(str(broken_server))
    assert result.findings, "Expected the broken server to produce prompt-arg findings."
    for f in result.findings:
        assert f.spec_source == "MCP"
        assert f.spec_section and "prompt" in f.spec_section.lower()


def test_tool_annotations_findings_all_have_citations(broken_server: Path) -> None:
    result = check_tool_annotations_declared(str(broken_server))
    assert result.findings, "Expected the broken server to produce annotation findings."
    for f in result.findings:
        assert f.spec_source == "MCP"
        assert f.spec_section and "annotations" in f.spec_section.lower()


def test_clean_bundled_example_passes_every_check() -> None:
    """The bundled examples/notes_server.py is the reference clean implementation
    — it should pass every auto-fired check. If it doesn't, either the example
    is buggy or a check has a false positive."""
    example = Path(__file__).parent.parent / "examples" / "notes_server.py"
    assert example.exists()

    manifest = extract_manifest_from_source(str(example))
    m_review = review_fastmcp_manifest_data(manifest)
    high_findings = [f for f in m_review.findings if f.severity == "high"]
    assert not high_findings, f"Unexpected HIGH findings on clean example: {high_findings}"

    for label, check_fn in [
        ("silent_error_returns", check_silent_error_returns),
        ("resource_mime_type", check_resource_mime_type_declared),
        ("prompt_arg_descriptions", check_prompt_argument_descriptions),
        ("tool_annotations", check_tool_annotations_declared),
    ]:
        r = check_fn(str(example))
        assert r.passed, f"{label}: {[f.message for f in r.findings]}"
