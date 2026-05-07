# Tool Design

Tools should be narrow, typed, and model-readable.

Good tool descriptions explain:

- When the model should call the tool.
- What input is required.
- What the tool returns.
- What the tool will not do.

Good:

```text
Review a FastMCP capability manifest and return deterministic findings by severity.
```

Weak:

```text
Checks stuff.
```

Avoid tools that execute arbitrary shell commands, perform hidden network work, or combine unrelated responsibilities.
