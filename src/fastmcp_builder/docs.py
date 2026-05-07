from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = Path(os.environ.get("FASTMCP_BUILDER_DOCS_DIR", ROOT / "docs")).resolve()
EXAMPLES_DIR = Path(os.environ.get("FASTMCP_BUILDER_EXAMPLES_DIR", ROOT / "examples")).resolve()


def list_markdown_docs() -> list[str]:
    return sorted(path.stem for path in DOCS_DIR.glob("*.md"))


def list_examples() -> list[str]:
    return sorted(path.name for path in EXAMPLES_DIR.iterdir() if path.is_file())


def read_doc(slug: str) -> str:
    path = _safe_child(DOCS_DIR, f"{slug}.md")
    return path.read_text(encoding="utf-8")


def read_example(name: str) -> str:
    path = _safe_child(EXAMPLES_DIR, name)
    return path.read_text(encoding="utf-8")


def _safe_child(base: Path, relative_name: str) -> Path:
    path = (base / relative_name).resolve()
    if base not in path.parents and path != base:
        raise ValueError("Path escapes configured content directory.")
    if not path.is_file():
        raise FileNotFoundError(path.name)
    return path
