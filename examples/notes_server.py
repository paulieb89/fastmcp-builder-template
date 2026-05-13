"""Notes MCP server.

Exposes a directory of local markdown files as resources and provides a tool
to return a compact summary (headings + opening paragraph) of any note.

Configuration
-------------
NOTES_DIR : path
    Directory containing .md files. Defaults to examples/notes/ relative to
    this file. Override with the NOTES_DIR environment variable.

Primitives
----------
resources:
    notes://index         — list all note names (without .md)
    notes://{name}        — read a note by name
tools:
    summarise_note(name)  — return headings + opening paragraph
"""

from __future__ import annotations

import os
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("Notes")

_SCRIPT_DIR = Path(__file__).resolve().parent
NOTES_DIR: Path = Path(os.environ.get("NOTES_DIR", _SCRIPT_DIR / "notes")).resolve()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _safe_note_path(name: str) -> Path:
    """Resolve *name* to an absolute .md path inside NOTES_DIR.

    Raises
    ------
    ValueError
        If the resolved path escapes NOTES_DIR (path traversal).
    FileNotFoundError
        If the .md file does not exist.
    """
    resolved = (NOTES_DIR / f"{name}.md").resolve()
    if NOTES_DIR not in resolved.parents:
        raise ValueError(f"Note name {name!r} escapes the notes directory.")
    if not resolved.is_file():
        raise FileNotFoundError(f"Note '{name}' not found.")
    return resolved


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


@mcp.resource("notes://index", mime_type="text/plain")
def notes_index() -> str:
    """List all available notes by name (without the .md extension)."""
    names = sorted(p.stem for p in NOTES_DIR.glob("*.md") if p.is_file())
    return "\n".join(names) if names else "(no notes found)"


@mcp.resource("notes://{name}", mime_type="text/markdown")
def note_by_name(name: str) -> str:
    """Read a markdown note by name (omit the .md extension)."""
    return _safe_note_path(name).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def summarise_note(name: str) -> str:
    """Return a compact summary of a note: its headings and opening paragraph.

    The summary is built locally from the markdown source without any network
    calls. Headings are lines that start with ``#``. The opening paragraph is
    the first contiguous block of non-heading, non-blank lines.

    Parameters
    ----------
    name:
        Note name without the .md extension (e.g. ``"getting-started"``).
    """
    content = _safe_note_path(name).read_text(encoding="utf-8")
    lines = content.splitlines()

    headings = [line for line in lines if line.startswith("#")]

    first_para: list[str] = []
    for line in lines:
        if line.startswith("#"):
            if first_para:
                break
            continue
        if line.strip():
            first_para.append(line.strip())
        elif first_para:
            break

    parts: list[str] = []
    if headings:
        parts.append("## Headings\n" + "\n".join(headings))
    if first_para:
        parts.append("## Opening paragraph\n" + " ".join(first_para))
    return "\n\n".join(parts) if parts else "(empty note)"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
