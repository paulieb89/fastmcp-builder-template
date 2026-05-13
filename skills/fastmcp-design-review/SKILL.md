---
name: fastmcp-design-review
description: Audit a FastMCP server or manifest for correct tool/resource/prompt boundaries, local-first scope, and test coverage. Use when the user says "review my MCP server", "check my FastMCP design", or shares an mcp.json or server module for critique.
---

# FastMCP Design Review

Use this skill when reviewing a proposed FastMCP server.

If the user provides a manifest (e.g., the structured capability listing from a `plugin.json` or a hand-written spec), call the `review_fastmcp_manifest` tool first — it returns deterministic findings keyed to manifest paths. Then layer the checks below on top.

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
