# Resource Design

Resources expose data to the client. They should be readable, stable, and low surprise.

Good resources:

- Local markdown notes.
- Small examples.
- Static capability manifests.

Design checklist:

- Use stable URI patterns.
- Always declare `mime_type` on `@mcp.resource` (e.g. `"application/json"` or `"text/markdown"`). Without it the client has no hint for deserialization.
- Avoid mutation.
- Avoid runtime network calls.
- Prevent path traversal for file-backed resources.
