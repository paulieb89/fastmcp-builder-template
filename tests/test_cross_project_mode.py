"""
Mode 2 (Cross-Project Advisory Use) invariants.

When the builder server is launched from a foreign project via
  uv --directory /path/to/fastmcp-builder-template run fastmcp run ...
the process CWD is the caller's project, not the template root.
These tests verify that docs, examples, and advisory tools remain
functional regardless of where CWD points.
"""

import importlib

import fastmcp_builder.docs as docs_mod
import pytest
from fastmcp_builder.docs import DOCS_DIR, EXAMPLES_DIR, ROOT, list_examples, list_markdown_docs, read_doc, read_example
from fastmcp_builder.server import (
    check_tool_name_format,
    check_uri_stability,
    classify_mcp_primitive,
    suggest_prompt_contract,
    suggest_resource_contract,
    suggest_tool_contract,
)


# ---------------------------------------------------------------------------
# ROOT derivation
# ---------------------------------------------------------------------------


def test_root_is_not_cwd_when_they_differ(tmp_path, monkeypatch):
    """ROOT is __file__-relative and must not equal an arbitrary CWD."""
    monkeypatch.chdir(tmp_path)
    assert ROOT != tmp_path
    assert ROOT.is_dir()


def test_docs_dir_is_not_under_foreign_cwd(tmp_path, monkeypatch):
    """DOCS_DIR must not be a child of an arbitrary CWD."""
    monkeypatch.chdir(tmp_path)
    assert not DOCS_DIR.is_relative_to(tmp_path)


def test_examples_dir_is_not_under_foreign_cwd(tmp_path, monkeypatch):
    """EXAMPLES_DIR must not be a child of an arbitrary CWD."""
    monkeypatch.chdir(tmp_path)
    assert not EXAMPLES_DIR.is_relative_to(tmp_path)


# ---------------------------------------------------------------------------
# Doc resolution from foreign CWD
# ---------------------------------------------------------------------------


def test_list_markdown_docs_works_when_cwd_has_no_docs_folder(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert not (tmp_path / "docs").exists()
    assert "tool-design" in list_markdown_docs()


def test_read_doc_works_when_cwd_has_no_docs_folder(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    content = read_doc("tool-design")
    assert "tool" in content.lower()


def test_read_doc_raises_on_missing_slug(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError):
        read_doc("no-such-doc")


# ---------------------------------------------------------------------------
# Example resolution from foreign CWD
# ---------------------------------------------------------------------------


def test_list_examples_works_when_cwd_has_no_examples_folder(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert not (tmp_path / "examples").exists()
    assert "minimal_server.py" in list_examples()


def test_read_example_works_when_cwd_has_no_examples_folder(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    content = read_example("minimal_server.py")
    assert "FastMCP" in content


def test_read_example_raises_on_missing_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError):
        read_example("no_such_file.py")


# ---------------------------------------------------------------------------
# DOCS_DIR / EXAMPLES_DIR module attribute is respected at call time
# (these test that list_* functions read the module attribute, not a snapshot)
# ---------------------------------------------------------------------------


def test_list_markdown_docs_respects_docs_dir_attribute(tmp_path, monkeypatch):
    custom = tmp_path / "custom_docs"
    custom.mkdir()
    (custom / "custom-guide.md").write_text("# Custom Guide")

    monkeypatch.setattr(docs_mod, "DOCS_DIR", custom)

    slugs = docs_mod.list_markdown_docs()
    assert "custom-guide" in slugs
    assert "tool-design" not in slugs


def test_list_examples_respects_examples_dir_attribute(tmp_path, monkeypatch):
    custom = tmp_path / "custom_examples"
    custom.mkdir()
    (custom / "my_server.py").write_text("# placeholder")

    monkeypatch.setattr(docs_mod, "EXAMPLES_DIR", custom)

    names = docs_mod.list_examples()
    assert "my_server.py" in names
    assert "minimal_server.py" not in names


# ---------------------------------------------------------------------------
# Env-var wiring: FASTMCP_BUILDER_DOCS_DIR / EXAMPLES_DIR read at import time
# ---------------------------------------------------------------------------


def test_fastmcp_builder_docs_dir_env_var_is_read_at_import(tmp_path, monkeypatch):
    """FASTMCP_BUILDER_DOCS_DIR is evaluated when the module is imported."""
    custom = tmp_path / "env_docs"
    custom.mkdir()
    original = docs_mod.DOCS_DIR

    monkeypatch.setenv("FASTMCP_BUILDER_DOCS_DIR", str(custom))
    importlib.reload(docs_mod)
    try:
        assert docs_mod.DOCS_DIR == custom
    finally:
        monkeypatch.delenv("FASTMCP_BUILDER_DOCS_DIR", raising=False)
        importlib.reload(docs_mod)
        assert docs_mod.DOCS_DIR == original


def test_fastmcp_builder_examples_dir_env_var_is_read_at_import(tmp_path, monkeypatch):
    """FASTMCP_BUILDER_EXAMPLES_DIR is evaluated when the module is imported."""
    custom = tmp_path / "env_examples"
    custom.mkdir()
    original = docs_mod.EXAMPLES_DIR

    monkeypatch.setenv("FASTMCP_BUILDER_EXAMPLES_DIR", str(custom))
    importlib.reload(docs_mod)
    try:
        assert docs_mod.EXAMPLES_DIR == custom
    finally:
        monkeypatch.delenv("FASTMCP_BUILDER_EXAMPLES_DIR", raising=False)
        importlib.reload(docs_mod)
        assert docs_mod.EXAMPLES_DIR == original


# ---------------------------------------------------------------------------
# Advisory tools are stateless and CWD-independent
# ---------------------------------------------------------------------------


def test_classify_mcp_primitive_works_from_foreign_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = classify_mcp_primitive("expose local project docs to the client")
    assert result.recommendation is not None


def test_suggest_tool_contract_works_from_foreign_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = suggest_tool_contract("validate email addresses")
    assert result.name


def test_suggest_resource_contract_works_from_foreign_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = suggest_resource_contract("local project changelog")
    assert result.uri_pattern.startswith("fastmcp-builder://")


def test_suggest_prompt_contract_works_from_foreign_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = suggest_prompt_contract("design a local MCP server")
    assert result.name


def test_check_tool_name_format_works_from_foreign_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = check_tool_name_format("validate_email")
    assert result.passed


def test_check_uri_stability_works_from_foreign_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = check_uri_stability("fastmcp-builder://docs/tool-design")
    assert result.passed


# ---------------------------------------------------------------------------
# No writes to the calling project's CWD
# ---------------------------------------------------------------------------


def test_advisory_tools_make_no_writes_to_cwd(tmp_path, monkeypatch):
    """Calling all advisory tools from a foreign project must leave that project's CWD clean."""
    monkeypatch.chdir(tmp_path)
    before = set(tmp_path.iterdir())

    classify_mcp_primitive("expose docs")
    suggest_tool_contract("validate input")
    suggest_resource_contract("project notes")
    suggest_prompt_contract("design server")
    check_tool_name_format("validate_email")
    check_uri_stability("fastmcp-builder://docs/guide")
    list_markdown_docs()
    list_examples()

    assert set(tmp_path.iterdir()) == before
