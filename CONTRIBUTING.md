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
