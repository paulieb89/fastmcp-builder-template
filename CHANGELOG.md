# Changelog

All notable changes to this template will be documented in this file.

## Unreleased

- **Spec-grounded compliance audit** (`specs/mcp-compliance-checks.md`,
  shipped via the `fastmcp-build-loop` skill across 7 work units).

  - `ReviewFinding` gains optional `spec_source` + `spec_section` fields
    so every plugin finding cites the MCP/FastMCP rule it enforces.
  - All existing manifest-review findings audited against MCP/FastMCP/opinion
    and tagged in `docs/check-audit.md`. Citations applied via a single
    `_finding()` helper + central `_CITATIONS` table.
  - `check_silent_error_returns` cites `FastMCP/servers/tools.md#error-handling`.
  - `check_error_response_design` reclassified as opinion-class — still callable
    on demand, removed from the design-review skill's automatic Layer 2 path.
  - Skill report format groups findings by spec source (MCP protocol /
    FastMCP framework / Opinion-class) so the grounding is visible at the
    output layer.
  - **New tool `check_resource_mime_type_declared(path)`** — flags
    `@mcp.resource` decorators without `mime_type=`. FastMCP-recommended,
    MEDIUM severity.
  - **New tool `check_prompt_argument_descriptions(path)`** — flags
    `@mcp.prompt` arguments without descriptions (either via
    `Annotated[X, Field(description=...)]` or a docstring Args block).
    MCP-recommended, MEDIUM severity.
  - **New tool `check_tool_annotations_declared(path)`** — flags
    `@mcp.tool` decorators that don't declare the four standard
    ToolAnnotations hints (readOnlyHint, destructiveHint, idempotentHint,
    openWorldHint). MCP-recommended, MEDIUM severity.
  - Generic `CheckReport` model added for new spec-grounded checks (same
    shape as `ManifestReview` / `SilentErrorReport` so the design-review
    skill can merge findings uniformly by severity).
- `extract_manifest_from_source` now produces accurate JSON schemas for the
  full FastMCP idiom set instead of falling back to `"type": "string"`:
    - `Optional[X]` / `Union[X, None]` / `X | None` unwrap to the inner type.
    - `Literal["a", "b", "c"]` surfaces as `{"type": "string", "enum": [...]}`
      so the model sees the allowed values.
    - `Annotated[X, Field(description=..., ge=..., le=..., min_length=..., ...)]`
      surfaces Field metadata as JSON Schema properties (description, minimum,
      maximum, exclusiveMinimum, exclusiveMaximum, minLength, maxLength, pattern).
    - Same-module Pydantic `BaseModel` parameters expand inline — a tool
      with `params: SearchInput` now exposes the SearchInput fields with
      their types, descriptions, bounds, and required markers. Closes
      the "wrapper input models hide the schema" false positive that the
      design-review skill flagged against bailii-mcp.
- New tool `check_silent_error_returns(path)` AST-scans a FastMCP server
  source for the silent-failure-conversion anti-pattern — any `@mcp.tool`
  function that returns `{"error": ...}`, `"Error: ..."`, or `f"Error: ..."`
  instead of raising. Catches the pattern that came up in 3/3 of the first
  fleet-server reviews (govuk, wdtk, bailii). Also follows one level of
  indirection: a tool that returns `_handle_error(e)` is flagged when
  `_handle_error` itself returns error sentinels (the bailii-mcp pattern).
- `fastmcp-design-review` skill now invokes `check_silent_error_returns`
  alongside `review_fastmcp_manifest` in Layer 2, so the silent-error
  pattern is caught deterministically across every reviewed server
  without relying on judgment to remember it.
- Bundle a FastMCP docs snapshot at `docs/upstream/fastmcp-llms.md` (the
  topic index from `https://gofastmcp.com/llms.txt`, ~35KB). The
  `fastmcp-design-review` skill now consults the snapshot first and
  WebFetches deeper pages on demand, instead of hard-coding any external
  FastMCP MCP server name. Refresh with `scripts/refresh-fastmcp-docs.sh`
  before tagging a release. Skill frontmatter now declares `docs:` URLs
  as formal metadata.
- New tool `extract_manifest_from_source(path)` parses a FastMCP server's
  Python source via `ast` and returns a manifest dict ready for
  `review_fastmcp_manifest`. Replaces the previous manual grep-and-reshape
  workflow in the `fastmcp-design-review` skill — point the tool at a
  server module and the manifest comes back deterministically. Detects
  the server name from `FastMCP("…")`, the primitives from `@mcp.tool`,
  `@mcp.resource`, and `@mcp.prompt` decorators (both `@dec` and `@dec(...)`
  call forms), and the tool input schema from typed function signatures.
- `review_fastmcp_manifest` now accepts `uriTemplate` and `uri_template` as
  aliases for the resource `uri` field. Templated resources in MCP wire
  format declare `uriTemplate`, not `uri`; rejecting it produced
  false-positive `resource.missing_uri` findings on every templated
  resource. A resource with none of `uri` / `uriTemplate` / `uri_template`
  is still flagged as a HIGH-severity structural error.
- `review_fastmcp_manifest` now accepts `inputSchema` and `input_schema` as
  aliases for the tool input-schema field (was: only `parameters`). Real
  FastMCP servers emit `inputSchema` at runtime per the MCP wire format;
  rejecting it produced false-positive `tool.missing_parameters` findings.
- `review_fastmcp_manifest` no longer enforces snake_case on resource names.
  In FastMCP, `Resource.name` is a human-readable label and the URI is the
  identifier — applying tool/prompt naming rules to resources produced
  false-positive `primitive.name_format` findings on display-style labels
  like "GOV.UK content — metadata header". Tools and prompts still require
  snake_case names.
- A primitive missing the `name` field entirely is now a HIGH-severity
  `primitive.missing_name` finding (was conflated with the medium-severity
  format-violation case).
- Adds a marketplace manifest at `.claude-plugin/marketplace.json` so the
  repo can be added from Claude Code's Marketplaces tab as well as the
  Plugins tab.

## 0.3.0

- Wire the repository as an installable Claude Code plugin. Skills and commands
  move from `.claude/` to plugin-root `skills/` and `commands/` for plugin
  auto-discovery. The MCP server is declared inline in
  `.claude-plugin/plugin.json` via `mcpServers.srv` using
  `${CLAUDE_PLUGIN_ROOT}` for portable paths.
- Remove root `.mcp.json` (replaced by the plugin manifest). In-repo
  contributors run the server directly with
  `uv run fastmcp run src/fastmcp_builder/server.py:mcp` when needed.
- Align `pyproject.toml` version with `plugin.json` (both now 0.3.0).

## 0.2.0

- Add `check_uri_stability` tool — deterministic URI stability checks.
- Add `check_tool_name_format` tool — snake_case, length, generic name validation.
- Add `check_prompt_name_format` tool — snake_case, length, `_prompt` suffix validation.
- Add `raw-mcp-to-fastmcp-v3` translation doc — maps course material to standalone FastMCP v3.
- Bump FastMCP dependency to 3.2.4.
- Add GitHub Actions CI workflow (`uv sync` + `uv run pytest` on push/PR).
- Add project-scoped skills: `fastmcp-build-loop`, `fastmcp-design-review`,
  `fastmcp-scaffold-author`, `mcp-primitive-classification`.

## 0.1.1

- Add MIT license.
- Add contribution rules for conservative local-first changes.
- Add Claude Code usage and fresh-clone verification notes.
- Fix review quality regression (description_quality heuristic).
- Add git workflow documentation.

## 0.1.0

- Initial local-first FastMCP builder template.
- Add project-scoped Claude Code MCP configuration.
- Add FastMCP tools, resources, prompts, docs, examples, and tests.
