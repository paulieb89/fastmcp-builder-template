# FastMCP Patterns

Use the standalone FastMCP SDK:

```python
from fastmcp import FastMCP

mcp = FastMCP("Example")
```

Expose primitives with decorators:

- `@mcp.tool` for model-controlled capabilities.
- `@mcp.resource("scheme://path")` for client-readable data.
- `@mcp.prompt` for reusable user-triggered workflows.

Keep local starter servers small. Prefer clear contracts, structured returns, and deterministic tests before adding infrastructure.
