import pytest

from fastmcp_builder.docs import list_examples, list_markdown_docs, read_doc, read_example
from fastmcp_builder.review import description_quality
from fastmcp_builder.server import mcp


def test_server_object_exists():
    assert mcp is not None


def test_docs_resources_resolve():
    assert "tool-design" in list_markdown_docs()
    assert "Tools should be narrow" in read_doc("tool-design")


def test_examples_resources_resolve():
    assert "minimal_server.py" in list_examples()
    assert "from fastmcp import FastMCP" in read_example("minimal_server.py")


def test_read_doc_raises_for_missing_slug():
    with pytest.raises(FileNotFoundError):
        read_doc("nonexistent_slug")


def test_read_doc_raises_for_path_traversal():
    with pytest.raises(ValueError):
        read_doc("../../etc/passwd")


def test_read_example_raises_for_path_traversal():
    with pytest.raises(ValueError):
        read_example("../../etc/passwd")


def test_description_quality_passes_for_natural_language():
    warnings = description_quality(
        "classify_mcp_primitive",
        "Classify a capability as an MCP tool, resource, or prompt.",
        {"type": "object", "properties": {"use_case": {}}},
    )
    assert not any("connect to the tool name" in w for w in warnings)
