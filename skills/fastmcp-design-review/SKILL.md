---
name: fastmcp-design-review
description: Audit a FastMCP server or manifest for correct tool/resource/prompt boundaries, local-first scope, and test coverage. Use when the user says "review my MCP server", "check my FastMCP design", "audit this server's design", or points at a repo / server module / manifest for critique.
metadata:
  docs:
    - "https://gofastmcp.com/llms.txt"
    - "https://gofastmcp.com/llms-full.txt"
  bundled_snapshot: "docs/upstream/fastmcp-llms.md"
  refresh_script: "scripts/refresh-fastmcp-docs.sh"
---

# FastMCP Design Review

Use this skill when reviewing a FastMCP server. The review has three layers:

1. **Build the manifest from source** (grep + read).
2. **Run deterministic checks** via the `review_fastmcp_manifest` tool.
3. **Layer judgment checks** on top (the checklist below).

Never ask the user to construct a manifest by hand. The skill does it.

## Source of FastMCP truth

When a judgment call needs current FastMCP behaviour (a decorator's exact kwargs, a middleware ordering rule, a new pattern shipped in the last few weeks), consult sources in this order:

1. **Bundled snapshot** at `${CLAUDE_PLUGIN_ROOT}/docs/upstream/fastmcp-llms.md` — an index of every documented FastMCP topic with its URL. Fast, offline, current as of plugin release.
2. **Live docs**, via WebFetch against the URLs listed in the bundled snapshot (or the `docs:` URLs in this skill's frontmatter). Use this when the snapshot's index lists a topic but you need its full content, or when a behaviour seems newer than the snapshot.

Do not assume an external FastMCP MCP server is installed under any particular name — those vary across harnesses (`mcp__claude_ai_fastmcp__*`, `mcp__fastmcp__*`, etc.). Use the bundled snapshot + WebFetch instead.

To regenerate the bundled snapshot (contributor-facing): `bash scripts/refresh-fastmcp-docs.sh`.

---

## Layer 1 — Build the manifest from source

Use the `extract_manifest_from_source` tool. Point it at the server module path:

```
extract_manifest_from_source(path="<repo-path>/<server_module>.py")
```

It returns a manifest dict ready for Layer 2 — deterministically, by walking the AST. No hand-construction, no grep+reshape iterations.

Locate the server module first if it isn't obvious:

```bash
# Find the FastMCP entry point.
grep -rn "FastMCP(" --include="*.py" <repo-path> | head -5
```

If the server is split across multiple files (e.g. a `server.py` plus a `resources.py` that registers extra `@mcp.resource` decorators via a helper), call `extract_manifest_from_source` on each file and merge the `primitives` lists — keep the server name from the file that declares `FastMCP(...)`.

Field-name notes (the reviewer accepts all of these — `extract_manifest_from_source` uses the first column):

- Tool input schema: `input_schema` (also accepted: `inputSchema`, `parameters`)
- Resource URI: `uri_template` (also accepted: `uriTemplate`, `uri`)

---

## Layer 2 — Run the deterministic reviews

Run these tools in the **automatic** path — they emit findings with spec citations (`spec_source` = "MCP" or "FastMCP"). Each finding carries the spec section it enforces; report it verbatim.

**Manifest-level (one call per server):**

1. **`review_fastmcp_manifest(manifest)`** — checks manifest shape, primitive names, tool input schemas, resource URIs, prompt arguments. Multiple MCP/FastMCP rules.

**Source-level (run on every file that contains `@mcp.*` decorators — same files you fed to `extract_manifest_from_source`):**

2. **`check_silent_error_returns(path)`** — flags `@mcp.tool` functions that return `{"error": ...}` or `"Error: …"` instead of raising. **FastMCP** `servers/tools.md#error-handling`. HIGH severity.
3. **`check_resource_mime_type_declared(path)`** — flags `@mcp.resource` decorators without `mime_type=`. **FastMCP** `servers/resources.md#mime_type`. MEDIUM severity.
4. **`check_prompt_argument_descriptions(path)`** — flags `@mcp.prompt` arguments without descriptions (either via `Annotated[X, Field(description=...)]` or a docstring `Args:` block). **MCP** `server/prompts#argument-description`. MEDIUM severity.
5. **`check_tool_annotations_declared(path)`** — flags `@mcp.tool` decorators missing the four standard ToolAnnotations hints (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`). **MCP** `server/tools#annotations`. MEDIUM severity.

Merge the findings from all five tools and report them grouped by `spec_source` (see "Report format" below).

**On-demand only — not auto-fired** (see `docs/check-audit.md`):

- `check_error_response_design(tool_behavior, failure_modes)` — opinion-class categorisation helper for designing new error responses. No single spec rule.
- `check_tool_name_format(name)` / `check_prompt_name_format(name)` / `check_uri_stability(uri_pattern)` / `check_tool_description_quality(...)` — single-value helpers exposed for ad-hoc use while authoring new primitives. The manifest review (#1 above) already runs the equivalent rules across an entire server, so the skill doesn't double up on them.

Findings carry `severity`, `code`, `path`, and `spec_source` / `spec_section`. Quote the citation in the report so the reader can verify the rule. If `spec_source == "opinion"`, label the finding clearly so it isn't mistaken for a protocol violation.

If the manifest review surfaces findings about the **manifest shape itself** (missing fields, wrong key names), that's a manifest-construction error in this skill — fix it and re-run, don't report it back to the user.

---

## Layer 3 — Judgment checks (human review)

Apply these on top of the deterministic findings:

- Tools are model-controlled capabilities (the model decides when to call).
- Resources are client/app-controlled data (the host decides when to fetch).
- Prompts are user-triggered workflows (the user picks them from a menu).
- The server uses `from fastmcp import FastMCP` (not the deprecated `mcp.server.fastmcp` path).
- The server exposes a real `mcp` object at module top-level.
- Local-first operation remains the default. Network calls, if any, are explicit and documented.
- No arbitrary shell execution tools are added.
- No databases, auth flows, crawlers, hosted UI, or background jobs are added.
- Tests cover the behavior being introduced — both happy path and at least one failure mode per tool.

Anti-patterns to flag specifically:

- A tool that returns `{"error": "..."}` on failure instead of raising — silent failure conversion.
- A resource URI with volatile tokens (`{timestamp}`, `{session_id}`, query strings).
- A tool description under ~30 characters or one that doesn't mention when to use the tool.
- A `@mcp.resource` without `mime_type` declared.
- A server that mixes proxy/aggregator behavior (`create_proxy`, `mcp.mount`) with locally-defined primitives — pick one architecture.

---

## Report format

Group findings by **spec source first**, then by severity within each group. This makes the grounding visible — a "HIGH" labelled MCP shows that hosts may refuse the server; a "HIGH" labelled opinion is style, not a protocol violation.

```
Summary: <pass | fail> — N high, N medium, N low (S spec, O opinion)

### MCP protocol findings
- [HIGH] code · path · message · MCP §spec/section
- [MEDIUM] ...

### FastMCP framework findings
- [HIGH] code · path · message · FastMCP §spec/section
- [MEDIUM] ...

### Opinion-class findings (informational)
- [LOW] code · path · message  (no spec citation — judgment-class)

### Layer 3 — judgment notes
- Free-form judgment-layer observations from the checklist below.
- These are not deterministic findings; flag clearly as opinions.

### Recommended next PRs
1. Highest-impact fix first.
2. ...
```

For every finding, quote `finding.spec_source` and `finding.spec_section` verbatim — that's how the reader can verify the rule against the source spec without trusting the skill.

Quote file paths with line numbers when pointing at specific code (e.g. `server.py:142`).
