"""Sanity checks for the bundled FastMCP docs snapshot.

The snapshot is committed to git and refreshed via
scripts/refresh-fastmcp-docs.sh. These tests catch the obvious failure
modes — file missing, file empty, file truncated — before they ship.
"""

from pathlib import Path


SNAPSHOT = Path(__file__).parent.parent / "docs" / "upstream" / "fastmcp-llms.md"


def test_snapshot_exists() -> None:
    assert SNAPSHOT.exists(), (
        f"Expected bundled FastMCP snapshot at {SNAPSHOT}. "
        f"Run scripts/refresh-fastmcp-docs.sh to fetch it."
    )


def test_snapshot_is_non_trivial() -> None:
    """The snapshot should be more than a partial download or empty file.

    The published llms.txt at the time of bundling was ~35KB / 363 lines.
    A snapshot smaller than 5KB almost certainly indicates a fetch failure.
    """
    size = SNAPSHOT.stat().st_size
    assert size > 5_000, (
        f"Snapshot at {SNAPSHOT} is only {size} bytes — looks truncated. "
        f"Re-run scripts/refresh-fastmcp-docs.sh."
    )


def test_snapshot_mentions_fastmcp() -> None:
    """If 'FastMCP' isn't in the snapshot, we fetched the wrong document."""
    content = SNAPSHOT.read_text()
    assert "FastMCP" in content, (
        f"Snapshot at {SNAPSHOT} does not mention 'FastMCP'. "
        f"Did the upstream URL change?"
    )
