---
name: mcp-primitive-classification
description: Decide whether an MCP capability should be a tool, resource, or prompt. Use when the user asks "is this a tool or a resource?", "should this be a prompt?", or is choosing the right MCP primitive for a FastMCP server.
---

# MCP Primitive Classification

Use this skill before implementing a new capability.

Classification rules:

- Choose a tool when the model decides whether to invoke a typed capability.
- Choose a resource when the client reads server-provided data or context.
- Choose a prompt when the user intentionally starts a reusable workflow.

Output:

- Recommended primitive.
- Rationale.
- One alternative if the boundary is ambiguous.
- Any safety concern that affects the design.
