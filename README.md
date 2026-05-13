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
```

Run the server locally with STDIO:

```bash
uv run fastmcp run src/fastmcp_builder/server.py:mcp
```

## Install as a Claude Code Plugin

Install this repository as a Claude Code plugin to make the FastMCP Builder
tools, resources, prompts, skills, and slash commands available in any
project:

```bash
/plugin install https://github.com/paulieb89/fastmcp-builder-template
```

Prerequisites:

- `uv` must be installed and on `$PATH`. The plugin runs the MCP server with
  `uv run --project ${CLAUDE_PLUGIN_ROOT} …`, so `uv` is a hard requirement.

After install, confirm the server registered:

```text
/mcp
```

Expected: a server named `fastmcp-builder` (server key `srv`) appears.
Tools surface as `mcp__plugin_fastmcp-builder_srv__<tool_name>` (for example
`mcp__plugin_fastmcp-builder_srv__classify_mcp_primitive`).

Skills and slash commands auto-discover from the plugin:

- Slash commands: `/design-fastmcp`, `/add-tool`, `/review-manifest`
- Skills (loaded by Claude on matching prompts): see the table below

### In-Repo Development

When working **on** this template, you don't need the plugin server running.
Run the MCP server directly to test changes:

```bash
uv sync
uv run fastmcp run src/fastmcp_builder/server.py:mcp
```

To exercise the plugin end-to-end while developing, install it from your
local checkout in a separate test project (see
[docs/claude-code-workflow.md](docs/claude-code-workflow.md)).

## What This Template Teaches

- Tools are model-controlled capabilities.
- Resources are client/app-controlled data.
- Prompts are user-triggered workflows.
- FastMCP v3 exposes those primitives with `@mcp.tool`, `@mcp.resource`, and `@mcp.prompt`.

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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, scope rules, and PR guidelines.
