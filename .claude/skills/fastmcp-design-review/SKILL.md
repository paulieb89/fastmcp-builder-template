---
name: fastmcp-design-review
description: Review FastMCP server designs for primitive boundaries, local-first scope, and deterministic tests.
---

# FastMCP Design Review

Use this skill when reviewing a proposed FastMCP server.

Check:

- Tools are model-controlled capabilities.
- Resources are client/app-controlled data.
- Prompts are user-triggered workflows.
- The server uses `from fastmcp import FastMCP`.
- The server exposes a real `mcp` object.
- Local-first operation remains the default.
- No arbitrary shell execution tools are added.
- No runtime network calls, databases, auth, crawlers, hosted UI, or background jobs are added.
- Tests cover the behavior being introduced.
