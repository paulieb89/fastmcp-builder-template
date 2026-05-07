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
