---
name: fastmcp-scaffold-author
description: Author small local-first FastMCP server scaffolds with tests.
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
