from fastmcp_builder.review import review_fastmcp_manifest_data


def test_valid_manifest_passes_without_high_findings():
    manifest = {
        "name": "valid_server",
        "primitives": [
            {
                "kind": "tool",
                "name": "review_manifest",
                "description": "Review a manifest and return deterministic findings by severity.",
                "parameters": {"type": "object", "properties": {}},
            },
            {
                "kind": "resource",
                "name": "docs_index",
                "description": "Expose local curated documentation notes for client-controlled reads.",
                "uri": "example://docs",
            },
        ],
    }

    result = review_fastmcp_manifest_data(manifest)

    assert result.passed is True
    assert not [finding for finding in result.findings if finding.severity == "high"]


def test_invalid_manifest_reports_high_findings():
    result = review_fastmcp_manifest_data(
        {
            "name": "Bad Name",
            "primitives": [
                {
                    "kind": "resource",
                    "name": "doc",
                    "description": "Too short.",
                }
            ],
        }
    )

    assert result.passed is False
    assert any(finding.code == "resource.missing_uri" for finding in result.findings)


def test_tool_accepts_inputSchema_alias():
    """Real FastMCP servers emit inputSchema (MCP wire format), not parameters."""
    result = review_fastmcp_manifest_data(
        {
            "name": "wire_format_server",
            "primitives": [
                {
                    "kind": "tool",
                    "name": "search_items",
                    "description": "Search items in the catalogue by a free-text query.",
                    "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}},
                }
            ],
        }
    )

    assert result.passed is True
    assert not any(f.code == "tool.missing_parameters" for f in result.findings)


def test_tool_accepts_input_schema_snake_case_alias():
    """Python-side manifest authors often use input_schema (snake_case)."""
    result = review_fastmcp_manifest_data(
        {
            "name": "py_authored_server",
            "primitives": [
                {
                    "kind": "tool",
                    "name": "search_items",
                    "description": "Search items in the catalogue by a free-text query.",
                    "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}},
                }
            ],
        }
    )

    assert result.passed is True
    assert not any(f.code == "tool.missing_parameters" for f in result.findings)


def test_resource_name_does_not_require_snake_case():
    """Resource.name is a human-readable label in FastMCP; the URI is the identifier."""
    result = review_fastmcp_manifest_data(
        {
            "name": "display_label_resources",
            "primitives": [
                {
                    "kind": "resource",
                    "name": "GOV.UK content — metadata header",
                    "description": "Read the metadata header for a single GOV.UK content item by slug.",
                    "uri": "govuk://content/{slug}/header",
                }
            ],
        }
    )

    assert result.passed is True
    assert not any(f.code == "primitive.name_format" for f in result.findings)


def test_tool_and_prompt_names_still_require_snake_case():
    """Tools and prompts use their name as the model-facing identifier — snake_case stays enforced."""
    result = review_fastmcp_manifest_data(
        {
            "name": "mixed_case_server",
            "primitives": [
                {
                    "kind": "tool",
                    "name": "SearchItems",
                    "description": "Search items in the catalogue by a free-text query.",
                    "parameters": {"type": "object", "properties": {}},
                },
                {
                    "kind": "prompt",
                    "name": "Draft Request",
                    "description": "Draft a narrow request suitable for downstream consumption.",
                    "arguments": [],
                },
            ],
        }
    )

    name_format_findings = [f for f in result.findings if f.code == "primitive.name_format"]
    assert len(name_format_findings) == 2
    assert {f.path for f in name_format_findings} == {
        "$.primitives[0].name",
        "$.primitives[1].name",
    }


def test_resource_accepts_uriTemplate_alias():
    """Templated resources use uriTemplate in MCP wire format, not uri."""
    result = review_fastmcp_manifest_data(
        {
            "name": "templated_resource_server",
            "primitives": [
                {
                    "kind": "resource",
                    "name": "User profile by slug",
                    "description": "Read a user profile by URL slug as JSON.",
                    "uriTemplate": "example://users/{slug}",
                }
            ],
        }
    )

    assert result.passed is True
    assert not any(f.code == "resource.missing_uri" for f in result.findings)


def test_resource_accepts_uri_template_snake_case_alias():
    """Python-side manifest authors often use uri_template (snake_case)."""
    result = review_fastmcp_manifest_data(
        {
            "name": "py_authored_resource_server",
            "primitives": [
                {
                    "kind": "resource",
                    "name": "User profile by slug",
                    "description": "Read a user profile by URL slug as JSON.",
                    "uri_template": "example://users/{slug}",
                }
            ],
        }
    )

    assert result.passed is True
    assert not any(f.code == "resource.missing_uri" for f in result.findings)


def test_resource_with_no_uri_still_fails():
    """Removing all three aliases must still fail — this is a structural error."""
    result = review_fastmcp_manifest_data(
        {
            "name": "broken_resource_server",
            "primitives": [
                {
                    "kind": "resource",
                    "name": "Some resource",
                    "description": "A resource with no URI declared at all.",
                }
            ],
        }
    )

    assert result.passed is False
    assert any(f.code == "resource.missing_uri" and f.severity == "high" for f in result.findings)


def test_every_manifest_review_finding_carries_a_citation():
    """Snapshot — feed a deliberately broken manifest, assert every finding
    emitted by review_fastmcp_manifest_data carries a non-None spec_source.

    Codes audited in docs/check-audit.md must round-trip their citations
    through the review function. This guards against future code paths that
    construct ReviewFinding directly instead of via the _finding helper.
    """
    broken_manifest = {
        # name missing on purpose → manifest.missing_name
        "primitives": [
            # Each primitive triggers a different finding code.
            {"kind": "unknown", "name": "x", "description": "a" * 30, "parameters": {}},  # invalid_kind
            {"kind": "tool", "name": "MixedCase", "description": "a" * 30, "parameters": {}},  # name_format
            {"kind": "tool", "name": "ok_tool", "description": "short", "parameters": {}},  # description_too_short
            {"kind": "tool", "name": "no_schema", "description": "a" * 30},  # tool.missing_parameters
            {"kind": "resource", "name": "no_uri", "description": "a" * 30},  # resource.missing_uri
            {"kind": "prompt", "name": "no_args", "description": "a" * 30},  # prompt.missing_arguments (opinion)
        ],
    }
    result = review_fastmcp_manifest_data(broken_manifest)

    assert result.findings, "Expected the broken manifest to produce findings."
    for f in result.findings:
        assert f.spec_source is not None, (
            f"Finding code='{f.code}' has no spec_source — citation missing. "
            "Add it to _CITATIONS in src/fastmcp_builder/review.py."
        )

    # Spot-check specific citations against the audit doc.
    by_code = {f.code: f for f in result.findings}
    assert by_code["manifest.missing_name"].spec_source == "MCP"
    assert by_code["resource.missing_uri"].spec_source == "MCP"
    assert by_code["prompt.missing_arguments"].spec_source == "opinion"


def test_review_finding_accepts_spec_citation_fields():
    """ReviewFinding gains optional spec_source / spec_section fields so the
    design-review skill can group findings by their MCP/FastMCP citation."""
    from fastmcp_builder.models import ReviewFinding, Severity

    f = ReviewFinding(
        severity=Severity.HIGH,
        code="tool.silent_error_return",
        message="Tool 'x' returns error sentinel at line 42 instead of raising.",
        path="$.primitives.x",
        spec_source="FastMCP",
        spec_section="servers/tools.md#error-handling",
    )

    dumped = f.model_dump()
    assert dumped["spec_source"] == "FastMCP"
    assert dumped["spec_section"] == "servers/tools.md#error-handling"


def test_review_finding_without_citation_still_valid():
    """Backward compatibility: existing call sites that omit spec fields work."""
    from fastmcp_builder.models import ReviewFinding, Severity

    f = ReviewFinding(
        severity=Severity.MEDIUM,
        code="primitive.name_format",
        message="...",
        path="$.primitives[0].name",
    )

    assert f.spec_source is None
    assert f.spec_section is None


def test_missing_name_is_high_severity():
    """A primitive with no name at all is a structural error, not just a format issue."""
    result = review_fastmcp_manifest_data(
        {
            "name": "no_name_server",
            "primitives": [
                {
                    "kind": "tool",
                    "description": "A tool with no name field at all.",
                    "parameters": {"type": "object", "properties": {}},
                }
            ],
        }
    )

    assert result.passed is False
    assert any(
        f.code == "primitive.missing_name" and f.severity == "high"
        for f in result.findings
    )
