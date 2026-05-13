# AGENTS.md

This repository is a local-first FastMCP builder template. These instructions apply to the whole repository.

## Operating Rules

- Prefer Python, uv, Pydantic, pytest, and standalone FastMCP v3.
- Use `from fastmcp import FastMCP`.
- Keep the MCP server local-first, STDIO-based, and deterministic.
- Do not add arbitrary shell-command tools.
- Do not add runtime network calls unless explicitly approved.
- Do not add auth, hosted services, databases, crawlers, scrapers, vector DBs, or background jobs.
- Preserve `.claude-plugin/plugin.json` — it wires the MCP server, skills, and commands for the plugin.
- Treat MCP primitives correctly:
  - Tools are model-controlled capabilities.
  - Resources are client/app-controlled data.
  - Prompts are user-triggered workflows.
- For code changes, add or update tests.

## Preferred Workflow

1. Explore relevant files before editing.
2. Produce a plan for broad changes.
3. Implement small, testable changes.
4. Run `uv run pytest`.
5. Summarize changed files and verification results.

## Verification

Before considering a change complete, run:

```bash
uv run pytest
```

For changes affecting project startup or MCP wiring, also run:

```bash
uv run fastmcp version
uv run fastmcp run src/fastmcp_builder/server.py:mcp
```

## Branch Policy

All changes — including docs and config — require a feature branch and PR:

```bash
git checkout -b feat/<short-description>
```

Open a PR to `main` when tests pass. Merge to `main` after approval. No direct commits to `main`.
