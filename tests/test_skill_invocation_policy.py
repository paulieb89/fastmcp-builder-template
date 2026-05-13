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
    """The Layer 2 automatic invocation list contains only the two spec-grounded
    checks. Opinion-class tools (`check_error_response_design`) belong below the
    'Available but NOT in the automatic path' heading."""
    head, _, rest = skill_body.partition("## Layer 2")
    layer_2_section, _, _ = rest.partition("## Layer 3")
    auto_path, _, on_demand = layer_2_section.partition("Available but NOT in the automatic path")

    # Spec-grounded checks belong in the auto path.
    assert "review_fastmcp_manifest" in auto_path
    assert "check_silent_error_returns" in auto_path
    # Opinion-class check belongs in the on-demand section.
    assert "check_error_response_design" not in auto_path
    assert "check_error_response_design" in on_demand


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
