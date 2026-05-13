"""Tests for fastmcp_builder.extract — parse Python sources for FastMCP primitives."""

from pathlib import Path

import pytest

from fastmcp_builder.extract import extract_manifest_from_source
from fastmcp_builder.review import review_fastmcp_manifest_data


def _write(tmp_path: Path, source: str) -> Path:
    f = tmp_path / "server.py"
    f.write_text(source)
    return f


def test_empty_file_yields_empty_primitives(tmp_path: Path) -> None:
    path = _write(tmp_path, "")
    manifest = extract_manifest_from_source(str(path))
    assert manifest == {"name": "unknown", "primitives": []}


def test_extracts_mcp_tool_with_docstring_and_params(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")

@mcp.tool
def search_items(query: str, limit: int = 10) -> list:
    """Search the catalogue for items matching the query string."""
    return []
''',
    )
    manifest = extract_manifest_from_source(str(path))

    tools = [p for p in manifest["primitives"] if p["kind"] == "tool"]
    assert len(tools) == 1
    tool = tools[0]
    assert tool["name"] == "search_items"
    assert "catalogue" in tool["description"]
    assert tool["input_schema"]["type"] == "object"
    assert "query" in tool["input_schema"]["properties"]
    assert "limit" in tool["input_schema"]["properties"]
    assert tool["input_schema"]["required"] == ["query"]  # `limit` has a default


def test_extracts_mcp_tool_with_decorator_call_form(tmp_path: Path) -> None:
    """@mcp.tool(annotations=...) — decorator called with kwargs."""
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")

@mcp.tool(tags={"public"})
def list_items() -> list:
    """List every item in the catalogue."""
    return []
''',
    )
    manifest = extract_manifest_from_source(str(path))

    tools = [p for p in manifest["primitives"] if p["kind"] == "tool"]
    assert len(tools) == 1
    assert tools[0]["name"] == "list_items"


def test_extracts_mcp_resource_with_uri_and_name_kwarg(tmp_path: Path) -> None:
    """@mcp.resource('uri', name='label', description='...') — positional URI + kwargs."""
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")

@mcp.resource(
    "wdtk://authorities/{slug}",
    name="WDTK authority by slug",
    description="Read a public authority as JSON.",
    mime_type="application/json",
)
async def authority_json(slug: str) -> str:
    return "{}"
''',
    )
    manifest = extract_manifest_from_source(str(path))

    resources = [p for p in manifest["primitives"] if p["kind"] == "resource"]
    assert len(resources) == 1
    r = resources[0]
    assert r["uri_template"] == "wdtk://authorities/{slug}"
    assert r["name"] == "WDTK authority by slug"
    assert "authority" in r["description"].lower()


def test_extracts_mcp_prompt(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")

@mcp.prompt
def draft_foi_request(authority_slug: str, topic: str) -> str:
    """Draft a narrow, specific FOI request suitable for WhatDoTheyKnow."""
    return ""
''',
    )
    manifest = extract_manifest_from_source(str(path))

    prompts = [p for p in manifest["primitives"] if p["kind"] == "prompt"]
    assert len(prompts) == 1
    p = prompts[0]
    assert p["name"] == "draft_foi_request"
    assert "FOI request" in p["description"]
    # Arguments derived from signature (sans ctx)
    assert [a["name"] for a in p["arguments"]] == ["authority_slug", "topic"]


def test_detects_server_name_from_FastMCP_constructor(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP

mcp = FastMCP("My Awesome Server")
''',
    )
    manifest = extract_manifest_from_source(str(path))
    # The manifest name should be a snake_case slug derived from the FastMCP name.
    assert manifest["name"] == "my_awesome_server"


def test_extracted_manifest_passes_review_for_real_example() -> None:
    """End-to-end: parse the bundled notes_server example, feed the manifest
    into the reviewer, expect zero HIGH-severity findings.

    This is the integration test the design-review skill relies on — if the
    extractor produces a manifest that the reviewer can't read, the whole
    'review a server from source' workflow is broken.
    """
    example_path = Path(__file__).parent.parent / "examples" / "notes_server.py"
    assert example_path.exists(), f"Expected bundled example at {example_path}"

    manifest = extract_manifest_from_source(str(example_path))

    # The extractor should have found at least one primitive.
    assert manifest["primitives"], "Expected the notes_server example to expose primitives"

    # And the manifest shape should clear the reviewer's structural checks.
    result = review_fastmcp_manifest_data(manifest)
    high_findings = [f for f in result.findings if f.severity == "high"]
    assert not high_findings, (
        f"Expected no high-severity findings for the bundled example. "
        f"Got: {[(f.code, f.path) for f in high_findings]}"
    )


def test_resource_without_name_kwarg_falls_back_to_function_name(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")

@mcp.resource("wdtk://feed")
async def feed_xml() -> str:
    """Read the feed as raw XML."""
    return ""
''',
    )
    manifest = extract_manifest_from_source(str(path))

    resources = [p for p in manifest["primitives"] if p["kind"] == "resource"]
    assert len(resources) == 1
    assert resources[0]["name"] == "feed_xml"
    assert resources[0]["uri_template"] == "wdtk://feed"
    assert "feed" in resources[0]["description"].lower()
