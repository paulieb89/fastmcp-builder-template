# Changelog

All notable changes to this template will be documented in this file.

## Unreleased

## 0.3.0

- Wire the repository as an installable Claude Code plugin. Skills and commands
  move from `.claude/` to plugin-root `skills/` and `commands/` for plugin
  auto-discovery. The MCP server is declared inline in
  `.claude-plugin/plugin.json` via `mcpServers.srv` using
  `${CLAUDE_PLUGIN_ROOT}` for portable paths.
- Remove root `.mcp.json` (replaced by the plugin manifest). In-repo
  contributors run the server directly with
  `uv run fastmcp run src/fastmcp_builder/server.py:mcp` when needed.
- Align `pyproject.toml` version with `plugin.json` (both now 0.3.0).

## 0.2.0

- Add `check_uri_stability` tool — deterministic URI stability checks.
- Add `check_tool_name_format` tool — snake_case, length, generic name validation.
- Add `check_prompt_name_format` tool — snake_case, length, `_prompt` suffix validation.
- Add `raw-mcp-to-fastmcp-v3` translation doc — maps course material to standalone FastMCP v3.
- Bump FastMCP dependency to 3.2.4.
- Add GitHub Actions CI workflow (`uv sync` + `uv run pytest` on push/PR).
- Add project-scoped skills: `fastmcp-build-loop`, `fastmcp-design-review`,
  `fastmcp-scaffold-author`, `mcp-primitive-classification`.

## 0.1.1

- Add MIT license.
- Add contribution rules for conservative local-first changes.
- Add Claude Code usage and fresh-clone verification notes.
- Fix review quality regression (description_quality heuristic).
- Add git workflow documentation.

## 0.1.0

- Initial local-first FastMCP builder template.
- Add project-scoped Claude Code MCP configuration.
- Add FastMCP tools, resources, prompts, docs, examples, and tests.
