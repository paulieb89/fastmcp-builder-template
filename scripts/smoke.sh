#!/usr/bin/env bash
set -euo pipefail

uv run fastmcp version
uv run pytest
