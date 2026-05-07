# MCP Primitives

MCP servers expose three different primitive types. Keeping the boundaries clear makes servers easier to use and easier to review.

## Tools

Tools are model-controlled capabilities. Use a tool when the model should decide whether to call a function to compute, validate, transform, or act.

Good tool candidates:

- Review a capability manifest.
- Classify a proposed primitive.
- Generate a small implementation plan.

Avoid broad tools that hide multiple unrelated actions behind one name.

## Resources

Resources are client/app-controlled data. Use a resource when the server exposes readable context such as local docs, examples, or generated notes.

Good resource candidates:

- `fastmcp-builder://docs/tool-design`
- `fastmcp-builder://examples/minimal_server.py`

Resources should have stable URI patterns and predictable MIME types.

## Prompts

Prompts are user-triggered workflows. Use a prompt when a user intentionally starts a reusable sequence such as designing a server or reviewing a manifest.

Prompts should name their arguments and make the workflow boundaries explicit.
