from fastmcp_builder.docs import list_examples, list_markdown_docs, read_doc, read_example
from fastmcp_builder.server import mcp


def test_server_object_exists():
    assert mcp is not None


def test_docs_resources_resolve():
    assert "tool-design" in list_markdown_docs()
    assert "Tools should be narrow" in read_doc("tool-design")


def test_examples_resources_resolve():
    assert "minimal_server.py" in list_examples()
    assert "from fastmcp import FastMCP" in read_example("minimal_server.py")
