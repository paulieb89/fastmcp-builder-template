---
name: mcp-primitive-classification
description: Classify proposed MCP capabilities as tools, resources, or prompts.
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
