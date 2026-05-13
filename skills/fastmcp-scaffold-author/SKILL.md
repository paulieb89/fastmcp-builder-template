---
name: fastmcp-scaffold-author
description: Scaffold a new FastMCP server from scratch — server module, mcp object, first tool/resource/prompt, and pytest setup. Use when the user says "build an MCP server for X", "start a new FastMCP project", or needs a local-first STDIO server skeleton.
---

# FastMCP Scaffold Author

Use this skill when creating or extending a local FastMCP scaffold.

Requirements:

- Import `FastMCP` from `fastmcp`.
- Define `mcp = FastMCP(...)` in the server module.
- Use `@mcp.tool`, `@mcp.resource`, and `@mcp.prompt` for primitives.
- Keep the scaffold deterministic and local.
- Add pytest coverage for new logic.
- Keep examples minimal and readable.
