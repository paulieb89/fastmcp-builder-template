# Claude Code Workflow

This template is designed for project-scoped Claude Code use.

The root `.mcp.json` wires the local builder server with:

```bash
uv run fastmcp run src/fastmcp_builder/server.py:mcp
```

Recommended working pattern:

1. Explore the relevant files.
2. Classify primitives before implementation.
3. Plan the smallest useful change.
4. Add tests with the code.
5. Run `uv run pytest`.

Use `.claude/skills` for reusable teaching instructions and `.claude/commands` for explicit slash-command workflows.
