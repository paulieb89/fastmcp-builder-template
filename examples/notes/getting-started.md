# Getting Started

Welcome to the notes server. This example shows how to expose local markdown files as MCP resources and summarise them with a tool.

## Prerequisites

- Python 3.11 or later
- uv for dependency management
- fastmcp installed

## Running the Server

Start the server in STDIO mode:

```bash
uv run python examples/notes_server.py
```

Set `NOTES_DIR` to point at a different directory of markdown files if needed.

## Next Steps

Read the architecture note for a design overview.
