# Resource Design

Resources expose data to the client. They should be readable, stable, and low surprise.

Good resources:

- Local markdown notes.
- Small examples.
- Static capability manifests.

Design checklist:

- Use stable URI patterns.
- Return a clear MIME type when the SDK supports it.
- Avoid mutation.
- Avoid runtime network calls.
- Prevent path traversal for file-backed resources.
