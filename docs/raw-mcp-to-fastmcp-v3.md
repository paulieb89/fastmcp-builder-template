# Raw MCP to FastMCP v3

Anthropic MCP course examples teach protocol-level MCP concepts and lower-level SDK patterns.
Those concepts remain valid. This template implements them using the standalone FastMCP v3
package, which provides a higher-level decorator interface.

---

## Correct imports (standalone FastMCP v3)

```python
from fastmcp import FastMCP
from fastmcp import Context
```

## Forbidden imports (old bundled SDK path)

```python
# DO NOT USE — these are from the old mcp.server.fastmcp bundle, not standalone FastMCP v3
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context
```

---

## Concept mapping

| Raw MCP / protocol concept    | FastMCP v3 pattern              |
|-------------------------------|---------------------------------|
| MCP server                    | `mcp = FastMCP("Name")`         |
| Tool                          | `@mcp.tool`                     |
| Resource                      | `@mcp.resource("scheme://...")`  |
| Prompt                        | `@mcp.prompt`                   |
| Context injection             | `from fastmcp import Context`   |
| Server for Claude Code        | expose `mcp` object             |
| Local Claude Code config      | root `.mcp.json`                |

---

## Notes

- Anthropic course material uses `mcp.server.fastmcp` — this was the bundled path in older SDK
  versions. The concepts (tools, resources, prompts) are identical; only the import path differs.
- When building a FastMCP v3 server, always use the standalone package imports above, even when
  reference material shows the old bundled path.
- Course code examples are still useful for understanding MCP primitive design — translate the
  import path, keep the logic.
