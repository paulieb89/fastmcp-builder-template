# FastMCP Builder Template

A local-first FastMCP v3 starter template for building, reviewing, and teaching MCP server design. It gives Claude Code a project-scoped MCP server with tools, resources, prompts, skills, and explicit slash-command workflows.

## Quick Start

```bash
uv sync
uv run fastmcp version
uv run pytest
```

Run the server locally with STDIO:

```bash
uv run fastmcp run src/fastmcp_builder/server.py:mcp
```

Claude Code can discover this project server from the root `.mcp.json`.

## What This Template Teaches

- Tools are model-controlled capabilities.
- Resources are client/app-controlled data.
- Prompts are user-triggered workflows.
- FastMCP v3 exposes those primitives with `@mcp.tool`, `@mcp.resource`, and `@mcp.prompt`.

## Included Builder Capabilities

- Classify whether a use case should be a tool, resource, or prompt.
- Review a small capability manifest for deterministic design findings.
- Suggest tool, resource, and prompt contracts.
- Generate a minimal FastMCP server implementation plan.
- Expose local docs and examples as MCP resources.

## Local Boundaries

This template intentionally excludes runtime network calls, arbitrary shell execution, databases, auth, hosted UIs, crawlers, scrapers, and background jobs.
