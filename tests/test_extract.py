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


def test_detects_server_name_from_FastMCP_name_kwarg(tmp_path: Path) -> None:
    """FastMCP(name="...") — keyword arg form, no positional name."""
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP

mcp = FastMCP(name="My Awesome Server", instructions="Do useful things.")
''',
    )
    manifest = extract_manifest_from_source(str(path))
    assert manifest["name"] == "my_awesome_server"


def test_detects_server_name_from_multiline_FastMCP_call(tmp_path: Path) -> None:
    """FastMCP("Name", instructions=...) — positional name plus multi-line kwargs.

    Real fleet servers (whatdotheyknow-mcp, uk-business-mcp) use this shape;
    the constructor spans several lines because `instructions` is multi-line.
    """
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP

mcp = FastMCP(
    "WhatDoTheyKnow MCP",
    instructions=(
        "Read WhatDoTheyKnow public JSON, Atom feeds, and CSV exports. "
        "Optionally call the experimental write API if configured."
    ),
)
''',
    )
    manifest = extract_manifest_from_source(str(path))
    assert manifest["name"] == "whatdotheyknow_mcp"


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


def test_optional_int_unwraps_to_integer(tmp_path: Path) -> None:
    """Optional[int] must return 'integer' — not the 'string' fallback.

    Before the type-mapping fix, Optional[int] would extract as 'string'
    because Optional's outer Subscript name was unknown to the type map.
    """
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP
from typing import Optional

mcp = FastMCP("Demo")

@mcp.tool
def search(query: str, limit: Optional[int] = None) -> str:
    """Search."""
    return ""
''',
    )
    manifest = extract_manifest_from_source(str(path))
    tool = manifest["primitives"][0]
    assert tool["input_schema"]["properties"]["limit"]["type"] == "integer"


def test_union_int_or_none_unwraps_to_integer(tmp_path: Path) -> None:
    """PEP 604 `int | None` must return 'integer', not 'string'."""
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP

mcp = FastMCP("Demo")

@mcp.tool
def search(query: str, limit: int | None = None) -> str:
    """Search."""
    return ""
''',
    )
    manifest = extract_manifest_from_source(str(path))
    tool = manifest["primitives"][0]
    assert tool["input_schema"]["properties"]["limit"]["type"] == "integer"


def test_literal_surfaces_enum(tmp_path: Path) -> None:
    """Literal['a','b','c'] should expose the allowed values to the model."""
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP
from typing import Literal

mcp = FastMCP("Demo")

@mcp.tool
def update_state(request_id: int, state: Literal["waiting", "rejected", "successful"]) -> str:
    """Update."""
    return ""
''',
    )
    manifest = extract_manifest_from_source(str(path))
    state_prop = manifest["primitives"][0]["input_schema"]["properties"]["state"]
    assert state_prop["type"] == "string"
    assert state_prop["enum"] == ["waiting", "rejected", "successful"]


def test_optional_literal_combines_unwrap_and_enum(tmp_path: Path) -> None:
    """Optional[Literal[...]] = string enum + not required."""
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP
from typing import Literal, Optional

mcp = FastMCP("Demo")

@mcp.tool
def fetch(slug: str, mode: Optional[Literal["fast", "slow"]] = None) -> str:
    """Fetch."""
    return ""
''',
    )
    manifest = extract_manifest_from_source(str(path))
    mode_prop = manifest["primitives"][0]["input_schema"]["properties"]["mode"]
    assert mode_prop["type"] == "string"
    assert mode_prop["enum"] == ["fast", "slow"]


def test_pydantic_basemodel_param_expands_to_inline_schema(tmp_path: Path) -> None:
    """The bailii pattern: tool takes `params: SearchInput` where SearchInput
    is a Pydantic BaseModel. The extractor should expand the model's fields
    into the input schema so the model can see what to put inside `params`.
    """
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("Demo")

class SearchInput(BaseModel):
    query: str = Field(description="What to search for", min_length=2, max_length=500)
    limit: int = Field(default=10, ge=1, le=30, description="Max results")

@mcp.tool
def search(params: SearchInput) -> str:
    """Search."""
    return ""
''',
    )
    manifest = extract_manifest_from_source(str(path))
    tool = manifest["primitives"][0]
    params_prop = tool["input_schema"]["properties"]["params"]

    # The wrapping params field is an object whose properties mirror SearchInput.
    assert params_prop["type"] == "object"
    fields = params_prop["properties"]
    assert fields["query"]["type"] == "string"
    assert fields["query"]["description"] == "What to search for"
    assert fields["query"]["minLength"] == 2
    assert fields["query"]["maxLength"] == 500
    assert fields["limit"]["type"] == "integer"
    assert fields["limit"]["minimum"] == 1
    assert fields["limit"]["maximum"] == 30
    # Required fields = those without a default value.
    assert params_prop["required"] == ["query"]


def test_unknown_class_falls_back_to_string(tmp_path: Path) -> None:
    """A custom class with no matching definition in the module shouldn't crash
    the extractor — it falls back to 'string' as before."""
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP
from somewhere_external import ExternalThing

mcp = FastMCP("Demo")

@mcp.tool
def use_it(thing: ExternalThing) -> str:
    """Use it."""
    return ""
''',
    )
    manifest = extract_manifest_from_source(str(path))
    assert manifest["primitives"][0]["input_schema"]["properties"]["thing"]["type"] == "string"


def test_annotated_field_surfaces_description_and_bounds(tmp_path: Path) -> None:
    """Annotated[int, Field(ge=1, le=100, description='...')] surfaces metadata."""
    path = _write(
        tmp_path,
        '''
from fastmcp import FastMCP
from typing import Annotated
from pydantic import Field

mcp = FastMCP("Demo")

@mcp.tool
def search(
    query: Annotated[str, Field(description="What to search for", min_length=2, max_length=500)],
    limit: Annotated[int, Field(ge=1, le=30, description="Maximum results")] = 10,
) -> str:
    """Search."""
    return ""
''',
    )
    manifest = extract_manifest_from_source(str(path))
    props = manifest["primitives"][0]["input_schema"]["properties"]

    assert props["query"]["type"] == "string"
    assert props["query"]["description"] == "What to search for"
    assert props["query"]["minLength"] == 2
    assert props["query"]["maxLength"] == 500

    assert props["limit"]["type"] == "integer"
    assert props["limit"]["minimum"] == 1
    assert props["limit"]["maximum"] == 30
    assert props["limit"]["description"] == "Maximum results"


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
