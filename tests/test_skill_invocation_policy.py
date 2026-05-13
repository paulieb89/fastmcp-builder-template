"""Tests for the design-review skill body — what it auto-invokes, what it doesn't.

Unit 3 (`drop_or_demote_unsourced_checks`) of mcp-compliance-checks spec
demoted `check_error_response_design` from the deterministic Layer 2 auto-path.
These tests assert the skill body reflects that choice so a future contributor
doesn't silently re-add an opinion-class check to the automatic invocation.
"""

from pathlib import Path

import pytest

SKILL_PATH = Path(__file__).parent.parent / "skills" / "fastmcp-design-review" / "SKILL.md"


@pytest.fixture(scope="module")
def skill_body() -> str:
    return SKILL_PATH.read_text()


def test_layer_2_lists_only_spec_grounded_checks(skill_body: str) -> None:
    """The Layer 2 automatic-path list contains only spec-grounded checks
    (MCP / FastMCP). Opinion-class and ad-hoc-helper tools belong below the
    'On-demand only' heading so the skill doesn't auto-fire them."""
    _, _, rest = skill_body.partition("## Layer 2")
    layer_2_section, _, _ = rest.partition("## Layer 3")
    auto_path, _, on_demand = layer_2_section.partition("On-demand only")

    # All five spec-grounded checks belong in the auto path.
    for tool in (
        "review_fastmcp_manifest",
        "check_silent_error_returns",
        "check_resource_mime_type_declared",
        "check_prompt_argument_descriptions",
        "check_tool_annotations_declared",
    ):
        assert tool in auto_path, f"{tool} should be in the Layer 2 auto path"

    # Opinion-class and single-value helpers must NOT be in the auto path.
    for tool in (
        "check_error_response_design",
        "check_tool_name_format",
        "check_uri_stability",
    ):
        assert tool not in auto_path, f"{tool} should be on-demand only, not auto-fired"
        assert tool in on_demand, f"{tool} should be listed under 'On-demand only'"


def test_layer_2_mentions_spec_citation_in_findings(skill_body: str) -> None:
    """The skill body instructs the reader to quote the spec citation per finding —
    that's how grounding stays visible to the human."""
    assert "spec_source" in skill_body
    assert "spec_section" in skill_body


def test_report_format_groups_by_spec_source(skill_body: str) -> None:
    """Unit 4 — the report template groups findings under MCP / FastMCP / Opinion
    headers so the reader can immediately see protocol violations vs judgment-class
    findings. Without this grouping the audit's grounding work is invisible to the
    end user."""
    _, _, report_section = skill_body.partition("## Report format")
    assert "MCP protocol findings" in report_section
    assert "FastMCP framework findings" in report_section
    assert "Opinion-class findings" in report_section
