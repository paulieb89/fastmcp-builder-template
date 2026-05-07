# CLAUDE.md

This repository is a local-first FastMCP builder template.

## Operating Rules

- Prefer Python, uv, Pydantic, pytest, and standalone FastMCP v3.
- Use `from fastmcp import FastMCP`.
- Keep the MCP server local-first, STDIO-based, and deterministic.
- Do not add arbitrary shell-command tools.
- Do not add runtime network calls unless explicitly approved.
- Do not add auth, hosted services, databases, crawlers, scrapers, vector DBs, or background jobs.
- Preserve project-scoped `.mcp.json`.
- Treat MCP primitives correctly:
  - Tools are model-controlled capabilities.
  - Resources are client/app-controlled data.
  - Prompts are user-triggered workflows.
- For code changes, add or update tests.

## Preferred Workflow

1. Explore relevant files.
2. Produce a plan for broad changes.
3. Implement small, testable changes.
4. Run `uv run pytest`.
5. Summarize changed files and verification results.

## Skills

Use these project-scoped skills — invoke with `/skill-name`:

| When you want to...                          | Use                         |
|----------------------------------------------|-----------------------------|
| Decide if something is a tool/resource/prompt | `/mcp-primitive-classification` |
| Review an existing or proposed server design  | `/fastmcp-design-review`    |
| Create a new FastMCP server from scratch      | `/fastmcp-scaffold-author`  |
| Add tools/resources/prompts from a spec file  | `/fastmcp-build-loop`       |

## Branch policy

Work on a feature branch for every non-trivial change:

```bash
git checkout -b feat/<short-description>
```

Open a PR to `main` when tests pass. Direct commits to `main` are only for docs and config.
