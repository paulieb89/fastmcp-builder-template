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
