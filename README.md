# FastMCP Builder Template

[![CI](https://github.com/paulieb89/fastmcp-builder-template/actions/workflows/ci.yml/badge.svg)](https://github.com/paulieb89/fastmcp-builder-template/actions/workflows/ci.yml)

A local-first FastMCP v3 starter template for building, reviewing, and teaching MCP server design. It gives Claude Code a project-scoped MCP server with tools, resources, prompts, skills, and explicit slash-command workflows.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (package manager)

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

## Using With Claude Code

Open Claude Code from the repository root after installing dependencies:

```bash
uv sync
claude
```

The root `.mcp.json` configures a project-scoped MCP server named `fastmcp-builder`:

```bash
uv run fastmcp run src/fastmcp_builder/server.py:mcp
```

In Claude Code, run:

```text
/mcp
```

Expected result: `fastmcp-builder` appears as a project-scoped MCP server. Claude can then use the builder tools, resources, and prompts from this repository while working on the project.

## What This Template Teaches

- Tools are model-controlled capabilities.
- Resources are client/app-controlled data.
- Prompts are user-triggered workflows.
- FastMCP v3 exposes those primitives with `@mcp.tool`, `@mcp.resource`, and `@mcp.prompt`.

## Project Workflow

This repo uses a small branch-and-PR workflow for template changes. See [docs/git-workflow.md](docs/git-workflow.md) for the current `main` versus polish branch state and merge/tag steps.

## Included Builder Capabilities

### Tools

- Classify whether a use case should be a tool, resource, or prompt.
- Review a capability manifest for deterministic design findings.
- Suggest tool, resource, and prompt contracts.
- Generate a minimal FastMCP server implementation plan.
- Check tool and prompt name format (snake_case, length, generic name validation).
- Check resource URI stability (volatile tokens, query strings, live HTTP URLs).
- Check tool description quality for model-controlled use.
- Classify tool failure modes into validation, transient, permission, and business errors.
- Expose local docs and examples as MCP resources.

### Project-Scoped Skills

Invoke these from Claude Code with the listed slash command:

| Skill | Command | Purpose |
|-------|---------|---------|
| mcp-primitive-classification | `/mcp-primitive-classification` | Decide tool vs resource vs prompt |
| fastmcp-design-review | `/fastmcp-design-review` | Review an existing or proposed server |
| fastmcp-scaffold-author | `/fastmcp-scaffold-author` | Create a new FastMCP server from scratch |
| fastmcp-build-loop | `/fastmcp-build-loop` | Add tools/resources/prompts from a spec file |

### Learning Docs

Available as MCP resources at `fastmcp-builder://docs/{slug}`:

- `mcp-primitives` — tool vs resource vs prompt decision guide
- `tool-design` — tool contract patterns
- `resource-design` — resource URI and read-behavior patterns
- `prompt-design` — reusable workflow prompt patterns
- `fastmcp-patterns` — common FastMCP v3 code patterns
- `safety-boundaries` — local-first boundaries and what to exclude
- `claude-code-workflow` — explore → plan → implement → verify workflow
- `raw-mcp-to-fastmcp-v3` — translating raw MCP SDK code to standalone FastMCP v3

## Local Boundaries

This template intentionally excludes runtime network calls, arbitrary shell execution, databases, auth, hosted UIs, crawlers, scrapers, and background jobs.

## Fresh-Clone Verification

Before publishing or tagging a release, verify the template from a clean clone:

```bash
git clone https://github.com/paulieb89/fastmcp-builder-template.git /tmp/fastmcp-builder-template-check
cd /tmp/fastmcp-builder-template-check
uv sync
uv run fastmcp version
uv run pytest
uv run fastmcp run src/fastmcp_builder/server.py:mcp
```

Then open Claude Code from the repository root and run:

```text
/mcp
```

Expected result: `fastmcp-builder` appears as a project-scoped MCP server.
