# FastMCP Builder Template

[![CI](https://github.com/paulieb89/fastmcp-builder-template/actions/workflows/ci.yml/badge.svg)](https://github.com/paulieb89/fastmcp-builder-template/actions/workflows/ci.yml)

A Claude Code plugin **and** a learning template for [FastMCP v3](https://gofastmcp.com).
Same repository, two consumers. The plugin **audits** existing FastMCP servers
against the MCP protocol and FastMCP framework specs; the template gives a
worked example to learn from.

## How to read this README

Pick the use case that matches what you're trying to do.

- **I want to install it as a plugin so Claude Code can audit my FastMCP servers** → [Install as a plugin](#install-as-a-plugin)
- **I'm starting a new FastMCP server and want a worked example** → [Use as a learning template](#use-as-a-learning-template)
- **I want to contribute to this repo** → [Contributing](CONTRIBUTING.md)

---

## What the plugin can do

When installed, the plugin gives Claude Code five **automatic** deterministic
checks on every FastMCP server review, plus a set of **on-demand** helpers
for authoring new primitives.

### Automatic checks (every review)

Each finding cites the MCP/FastMCP spec section it enforces. Severity follows
the source: HIGH = protocol non-compliance; MEDIUM = framework recommendation.

| Check | What it catches | Severity | Spec source |
|---|---|---|---|
| `review_fastmcp_manifest` | Missing names, malformed URIs, bad input schemas, duplicate primitive names, opaque descriptions | HIGH / MEDIUM | MCP + FastMCP |
| `check_silent_error_returns` | `@mcp.tool` functions that return `{"error": ...}` or `"Error: ..."` instead of raising | HIGH | FastMCP `servers/tools.md#error-handling` |
| `check_resource_mime_type_declared` | `@mcp.resource` decorators without `mime_type=` | MEDIUM | FastMCP `servers/resources.md` |
| `check_prompt_argument_descriptions` | `@mcp.prompt` arguments with no description (in docstring `Args:` block or `Annotated[..., Field(...)]`) | MEDIUM | MCP `server/prompts` |
| `check_tool_annotations_declared` | `@mcp.tool` decorators missing the four standard `ToolAnnotations` hints | MEDIUM | MCP `server/tools#annotations` |

### On-demand tools (call them when designing a new primitive)

These don't auto-fire; the plugin exposes them as MCP tools you can invoke
explicitly when authoring or reviewing one specific name/URI/description.

- `classify_mcp_primitive` — should this capability be a tool, resource, or prompt?
- `suggest_tool_contract` / `suggest_resource_contract` / `suggest_prompt_contract` — generate a starter contract from a description
- `generate_minimal_server_plan` — scaffold a minimal FastMCP server plan
- `check_tool_name_format` / `check_prompt_name_format` — validate a single name
- `check_uri_stability` — check one URI pattern for volatile tokens
- `check_tool_description_quality` — review one description
- `check_error_response_design` — categorize a tool's failure modes (opinion-class, not a spec rule)
- `extract_manifest_from_source` — parse a `.py` file → manifest dict (used internally by the design review skill)

### Slash commands

- `/design-fastmcp` — design a new FastMCP server before writing code
- `/add-tool` — add one tool to an existing server with a typed contract
- `/review-manifest` — review a manifest JSON against the spec

### Skills (auto-activated when matching prompts)

- `fastmcp-design-review` — audit an existing server (runs the automatic checks above)
- `fastmcp-scaffold-author` — start a new FastMCP server from scratch
- `fastmcp-build-loop` — implement a server from a spec file, one section at a time
- `mcp-primitive-classification` — decide tool / resource / prompt for a new capability

### Bundled learning material (resources)

The plugin exposes its bundled docs as MCP resources at `fastmcp-builder://docs/{slug}`:

`mcp-primitives` · `tool-design` · `resource-design` · `prompt-design` ·
`fastmcp-patterns` · `safety-boundaries` · `claude-code-workflow` ·
`raw-mcp-to-fastmcp-v3`

Plus a snapshot of the official FastMCP topic index at `docs/upstream/fastmcp-llms.md`
(35 KB, refresh with `bash scripts/refresh-fastmcp-docs.sh` before tagging a release).

---

## What the plugin can't do

Honest list of out-of-scope items so you know when to reach for something else.

- **Doesn't run target servers.** Pure static AST analysis. Won't catch runtime
  bugs, env-var misconfiguration, network errors, or anything that only
  appears at execution time. If you need runtime checks, install the target
  server and exercise it.
- **Doesn't apply fixes.** Reports findings only. Claude (or you) reads the
  report and edits the source. There is no `--fix` mode.
- **FastMCP-specific.** Doesn't audit raw `mcp` SDK code, TypeScript MCP
  servers, or other frameworks. The decorator patterns (`@mcp.tool`,
  `@mcp.resource`, `@mcp.prompt`) and the `from fastmcp import FastMCP`
  import path are baked into the AST walker.
- **One server at a time.** No fleet/batch mode. Reviewing 12 servers means
  invoking the skill 12 times.
- **No fleet/personal conventions.** Checks are grounded in MCP/FastMCP spec
  citations only. Style preferences (snake_case prefixes, single-input-model
  patterns, pagination shapes) aren't enforced.
- **AST limits.** Can't see through dynamic constructs — a `mime_type=` whose
  value is a constant defined elsewhere in the module gets the benefit of
  the doubt; a docstring built at runtime won't be analysed.
- **Citation URLs are spec-section approximations.** They point at the
  relevant page+anchor on `gofastmcp.com` / `modelcontextprotocol.io`, but
  exact wording can shift between spec versions. Refresh the bundled
  snapshot to validate.
- **Bundled docs go stale.** The snapshot at `docs/upstream/fastmcp-llms.md`
  is a point-in-time copy. The skill body instructs Claude to WebFetch the
  live URL when the snapshot doesn't cover a topic.
- **Doesn't deploy, monitor, or test.** Design-layer only. Use your existing
  ops tooling for hosting and observability.

---

## Install as a plugin

Two install paths — pick whichever fits your Claude Code setup.

**Via marketplace tab:**

```text
https://github.com/paulieb89/fastmcp-builder-template
```

Paste into the Marketplaces tab → Add. Then install the `fastmcp-builder`
plugin from the Plugins tab.

**Via slash command:**

```text
/plugin install https://github.com/paulieb89/fastmcp-builder-template
```

**Prerequisites:** `uv` on `$PATH`. The plugin runs its MCP server with
`uv run --project ${CLAUDE_PLUGIN_ROOT} …`.

**Verify it loaded:**

```text
/mcp
```

You should see a server named `plugin:fastmcp-builder:srv` with ~15 tools.
Skill triggers like "review my MCP server" will activate
`fastmcp-design-review` automatically.

---

## Use as a learning template

The repo also functions as a clonable starter. Nothing about the plugin
prevents you from treating it as a reference implementation.

**To learn the patterns:**

1. Clone the repo.
2. Read `examples/notes_server.py` — a complete, passing-every-check FastMCP
   server (~120 lines: two resources, one tool, one prompt).
3. Read `docs/mcp-primitives.md` and `docs/tool-design.md` for the
   primitive-design rationale.
4. Adapt `notes_server.py` into your own server module.

**To start fresh:**

1. `uv sync` to install deps (`fastmcp==3.2.4`, `pydantic>=2.7`).
2. Write your server module.
3. Run it: `uv run fastmcp run path/to/your_server.py:mcp`.
4. If you want the plugin's audit on your work, install it as a plugin
   (above) and ask Claude Code: *"review the FastMCP design of `<your-server.py>`"*.

---

## How the two views share the repo

| Path | Plugin uses | Template uses |
|---|---|---|
| `src/fastmcp_builder/` | ✅ (Python source — the MCP server) | ❌ |
| `.claude-plugin/` | ✅ (manifest + marketplace entry) | ❌ |
| `skills/`, `commands/` | ✅ (auto-discovered) | ❌ |
| `examples/notes_server.py` | ✅ (test fixture + resource exposed via `fastmcp-builder://examples/`) | ✅ (clone-and-adapt reference) |
| `docs/*.md` | ✅ (curated learning material, served as MCP resources) | ✅ (read directly) |
| `docs/upstream/fastmcp-llms.md` | ✅ (spec snapshot for the design-review skill) | ✅ (FastMCP topic index) |
| `tests/`, `pyproject.toml`, `.github/` | ❌ | ❌ |

The single integration test `tests/test_every_finding_has_citation.py` keeps
the two honest: it asserts every plugin check produces findings with non-None
`spec_source`, AND that the bundled `notes_server.py` example passes every
auto-fired check. If you change either side, the other has to follow.

---

## Local boundaries (out of scope, by design)

This template excludes:

- Runtime network calls in the plugin's own code paths
- Arbitrary shell execution tools
- Databases, auth systems, hosted UIs
- Crawlers, scrapers, vector databases, background jobs

The plugin's MCP server runs locally via STDIO. The only network call it
makes is the optional WebFetch the design-review skill does against
`gofastmcp.com` when the bundled snapshot doesn't cover a topic.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, scope rules,
release checklist, and PR guidelines. The repo has CI (pytest + ruff) on
every PR.
