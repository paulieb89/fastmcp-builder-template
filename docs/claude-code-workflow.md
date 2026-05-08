# Claude Code Workflow

This repository supports two usage modes.

## Mode 1: In-Repo Learning and Template Development

Clone this repository, open Claude Code inside it, and study or modify the template itself. The root `.mcp.json` wires the local builder server:

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

## Mode 2: Cross-Project Advisory Use

You can also use this repository as a read-only FastMCP design advisor while working in a separate target project.

In the target project, add a project-scoped `.mcp.json` that points to this builder repo:

```json
{
  "mcpServers": {
    "fastmcp-builder": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/fastmcp-builder-template",
        "run",
        "fastmcp",
        "run",
        "src/fastmcp_builder/server.py:mcp"
      ]
    }
  }
}
```

Then open Claude Code from the target project:

```bash
cd /path/to/my-new-mcp-project
claude
```

In this mode:

- Claude Code edits files in the target project.
- The builder server reads its own bundled docs and examples.
- The builder server returns design advice, review results, resources, and prompts.
- The builder server does not write files into the target project.

Use this mode when you want the builder to guide a new FastMCP server implementation without copying this whole template.
