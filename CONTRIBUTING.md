# Contributing

This repository is a conservative teaching template for local-first FastMCP server design.

## Scope

Good contributions:

- Improve examples without making them larger than necessary.
- Improve concise original docs.
- Improve deterministic review logic.
- Add focused tests for existing behavior.
- Fix compatibility issues with the pinned FastMCP version.

Out of scope for the template:

- Arbitrary shell execution tools.
- Runtime network calls.
- Databases, auth systems, hosted UIs, crawlers, scrapers, vector databases, or background jobs.
- Large framework additions.
- Vendor documentation copied wholesale into this repo.

## Development

Run checks before opening a pull request:

```bash
uv sync
uv run fastmcp version
uv run pytest
```

Keep pull requests small and explain which MCP primitive boundary the change affects.

## CI

GitHub Actions runs `uv sync` and `uv run pytest` on every push and pull request to `main`. A PR cannot be considered ready until the CI badge is green. The workflow is at [.github/workflows/ci.yml](.github/workflows/ci.yml).

## Release Verification

Before tagging a release that bumps the plugin version, verify both
in-repo and plugin install paths.

### In-repo verification

```bash
git clone https://github.com/paulieb89/fastmcp-builder-template.git /tmp/fastmcp-builder-template-check
cd /tmp/fastmcp-builder-template-check
uv sync
uv run fastmcp version
uv run pytest
uv run fastmcp run src/fastmcp_builder/server.py:mcp
```

### Plugin install verification

In a clean test project (any directory), run:

```text
/plugin install /tmp/fastmcp-builder-template-check
/mcp
```

Expected: a server named `fastmcp-builder` (server key `srv`) appears, and
its tools surface as `mcp__plugin_fastmcp-builder_srv__<tool_name>`. Run
one tool (for example `classify_mcp_primitive`) and confirm the response
shape matches the Pydantic models in `src/fastmcp_builder/models.py`.
