# Claude Code Workflow

This repository supports two usage modes.

## Mode 1: Use as an Installed Plugin (Cross-Project)

Install the plugin in any project you want builder assistance in:

```bash
/plugin install https://github.com/paulieb89/fastmcp-builder-template
```

After install:

- The `fastmcp-builder` MCP server starts automatically and surfaces its
  tools under `mcp__plugin_fastmcp-builder_srv__*`.
- Slash commands `/design-fastmcp`, `/add-tool`, and `/review-manifest`
  become available.
- Skills (`mcp-primitive-classification`, `fastmcp-design-review`,
  `fastmcp-scaffold-author`, `fastmcp-build-loop`) activate automatically
  when their descriptions match the conversation.

The server reads its own bundled docs and examples from
`${CLAUDE_PLUGIN_ROOT}/docs` and `${CLAUDE_PLUGIN_ROOT}/examples`. It does
not write into the host project.

## Mode 2: Develop the Template Itself (In-Repo)

When working on this repository, the plugin server is not auto-loaded
(there is no project-scoped `.mcp.json`). Run the server directly to test
your changes:

```bash
uv sync
uv run fastmcp run src/fastmcp_builder/server.py:mcp
```

Recommended development pattern:

1. Explore the relevant files.
2. Classify primitives before implementation.
3. Plan the smallest useful change.
4. Add tests with the code.
5. Run `uv run pytest`.
6. For resources: verify `mime_type` is declared on every `@mcp.resource`
   decorator.

To verify your in-progress changes work as a plugin, install the plugin
from your local checkout into a separate test project:

```bash
/plugin install /absolute/path/to/fastmcp-builder-template
```

Restart Claude Code in the test project and run `/mcp` to confirm the
server registered.
