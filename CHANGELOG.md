# Changelog

All notable changes to this template will be documented in this file.

## Unreleased

- Add `check_uri_stability` tool — deterministic URI stability checks.
- Add `check_tool_name_format` tool — snake_case, length, generic name validation.
- Add `check_prompt_name_format` tool — snake_case, length, `_prompt` suffix validation.
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
