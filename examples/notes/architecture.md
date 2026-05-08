# Architecture

The notes server is a local-first FastMCP v3 server with three primitives.

## Resources

Each markdown file in the configured notes directory is exposed as a resource at `notes://{name}`. An index resource at `notes://index` lists all available note names.

## Tools

The `summarise_note` tool reads a note by name and returns its headings and opening paragraph as a compact summary. It performs no network calls and is fully deterministic.

## Design Principles

- All content is read from the local filesystem.
- Path traversal is blocked by resolving and bounding all paths.
- The notes directory is configurable via the `NOTES_DIR` environment variable.
