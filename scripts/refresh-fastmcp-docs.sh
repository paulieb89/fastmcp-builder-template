#!/usr/bin/env bash
# Refresh the bundled FastMCP docs index from gofastmcp.com.
#
# Run this before tagging a release so the snapshot stays current.
# Run it any other time you want to pull the latest topic catalogue —
# the file is committed to git, so review the diff after running.
#
# The snapshot is an index (one URL per FastMCP topic page) — Claude
# uses it to know what's available, then WebFetches specific pages when
# deeper detail is needed. We deliberately do NOT bundle the full
# llms-full.txt (2.2MB) to keep the plugin lean.

set -euo pipefail

SOURCE_URL="${FASTMCP_DOCS_URL:-https://gofastmcp.com/llms.txt}"
TARGET_PATH="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}/docs/upstream/fastmcp-llms.md"

echo "Fetching ${SOURCE_URL} ..."
mkdir -p "$(dirname "$TARGET_PATH")"
curl -fsSL --max-time 30 -o "$TARGET_PATH" "$SOURCE_URL"

BYTES=$(wc -c < "$TARGET_PATH")
LINES=$(wc -l < "$TARGET_PATH")
echo "Wrote ${TARGET_PATH}"
echo "  ${BYTES} bytes, ${LINES} lines"

if [ "$BYTES" -lt 1000 ]; then
    echo "ERROR: snapshot is suspiciously small (<1KB). Aborting." >&2
    exit 1
fi
