# Spec: MCP-Compliance Checks

Written using the spec-driven-development methodology. Each work unit below is
consumable by `/fastmcp-builder:fastmcp-build-loop` — one `## <Capability>`
section per buildable unit, processed in order, marked `[done]` as they ship.
SDD context sections are marked `[skip]` so the loop ignores them.

---

## Objective [skip]

Make every check the plugin ships **grounded in a verbatim spec citation**:
either the MCP protocol spec at `modelcontextprotocol.io` or the FastMCP
framework docs at `gofastmcp.com`. A check that can't cite either source is
either reclassified as opinion-class or dropped. Plugin output displays the
citation alongside the finding so the user knows where the rule comes from.

This closes the "vibing and guessing" gap: when the design-review skill
flags something, the reader can verify the rule independently against the
source spec.

## Tech Stack [skip]

- Python 3.11+, FastMCP v3.2.4 (already pinned)
- Pydantic v2 for model definitions
- pytest for tests
- AST-based static analysis only (no runtime introspection of target servers)

## Commands [skip]

- Build/install: `uv sync`
- Test: `uv run pytest`
- Run server (in-repo dev): `uv run fastmcp run src/fastmcp_builder/server.py:mcp`
- Refresh upstream FastMCP snapshot: `bash scripts/refresh-fastmcp-docs.sh`

## Project Structure [skip]

```
src/fastmcp_builder/
├── checks.py        ← AST-based deterministic checks
├── extract.py       ← AST → manifest
├── review.py        ← manifest review + name/URI/description checks
├── models.py        ← Pydantic report types (ReviewFinding, ManifestReview, etc.)
├── server.py        ← MCP tool wrappers
docs/upstream/
└── fastmcp-llms.md  ← Bundled FastMCP docs snapshot
```

## Code Style [skip]

Findings always carry a `severity` (Severity enum) and now a citation. Example
finding produced by a check:

```python
ReviewFinding(
    severity=Severity.HIGH,
    code="tool.silent_error_return",
    message="Tool 'foo' returns error sentinel at line 42 instead of raising.",
    path="$.primitives.foo",
    spec_source="FastMCP",
    spec_section="servers/tools.md#error-handling",
)
```

## Boundaries [skip]

**Always:**
- Cite spec source on every finding (work unit 1 makes the fields available).
- Run `uv run pytest` after each work unit before marking it `[done]`.
- TDD: red-green per behaviour change.
- Real-world validation: re-run the check against `wdtk`, `bailii`, `govuk`
  after building it, confirm the findings match what manual review found.

**Ask first:**
- Adding any check without a clean spec citation. (Default answer: don't.)
- Changing severity defaults across the existing check suite.
- Removing an existing check entirely (vs demoting its severity).

**Never:**
- Encode personal/fleet conventions as checks. The 6 conventions dropped
  upstream of this spec (dead_input_models, name_consistency, etc.) stay
  dropped.
- Ship a HIGH-severity finding without a "MUST" or "REQUIRED" citation
  in the source spec. HIGH means protocol-level non-compliance.

## Severity by spec source [skip]

| Spec source | Default severity | Rationale |
|---|---|---|
| MCP protocol (MUST/REQUIRED) | HIGH | Wire-level non-compliance; hosts may refuse the server |
| MCP protocol (SHOULD/RECOMMENDED) | MEDIUM | Server works but breaks host expectations |
| FastMCP (explicit doc rule like "raise, don't return") | HIGH | Framework idiom violation; common bug source |
| FastMCP (kwarg available but optional) | MEDIUM | Suboptimal, not wrong |
| No citation possible | drop or demote to opinion-class | "vibing" — not in scope |

## Success Criteria [skip]

- Every `ReviewFinding` produced by the plugin carries a non-empty
  `spec_source` and `spec_section` (or explicit "opinion" tag).
- Re-running `/fastmcp-builder:fastmcp-design-review` against `wdtk-mcp`
  produces identical High/Medium findings to today, plus citations.
- `fastmcp-build-loop` walks this spec end-to-end without manual intervention.
- The skill body in `skills/fastmcp-design-review/SKILL.md` instructs the
  output to group findings by spec source.

## Open Questions [skip]

1. Should `check_prompt_name_format`'s snake_case rule survive the audit?
   Pure FastMCP-Python convention (the decorator binds `__name__` as the
   prompt name). Probably stays but at MEDIUM not HIGH.
2. Should `check_error_response_design` survive? It categorises failures
   but doesn't enforce a single rule. Likely demoted to "brainstorming
   helper" — kept as a tool, removed from the deterministic review path.
3. The three P2 new checks (mime_type / prompt arg descriptions / tool
   annotations) ship at MEDIUM. Confirm before building?

---

## add_spec_source_to_ReviewFinding [done]

**Spec source:** Infrastructure — enables every subsequent unit.

Add two optional string fields to `ReviewFinding` in `models.py`:

```python
class ReviewFinding(BaseModel):
    severity: Severity
    code: str
    message: str
    path: str
    spec_source: str | None = None     # "MCP" | "FastMCP" | "opinion" | None
    spec_section: str | None = None    # e.g. "servers/tools.md#error-handling"
```

Existing code that constructs `ReviewFinding` without these fields continues
to work (both default to None). Update `check_silent_error_returns` to set
both — it's the only check already citing a spec by name. All other findings
keep `spec_source=None` until audited.

**Tests:**
- `ReviewFinding(...)` without the new fields still validates (backward compat).
- `ReviewFinding(spec_source="FastMCP", spec_section="...")` round-trips
  through `.model_dump()`.
- `check_silent_error_returns` findings now have `spec_source="FastMCP"` and
  a non-empty `spec_section`.

**Done when:** All 110+ existing tests pass; new tests pass; a manual
extraction of `check_silent_error_returns` output against wdtk shows the
new fields populated.

---

## audit_existing_checks_for_citations [done]

**Spec source:** Self-referential — this is the SDD audit.

Walk every check the plugin currently exposes and assign a verdict per the
"Severity by spec source" table above. For each existing check, the audit
produces a row:

| Check | Currently fires at | Cited spec source/section | Verdict |
|---|---|---|---|

Produce the table as a markdown file at `docs/check-audit.md` (committed),
**before** any code change.

For each check, add `spec_source` and `spec_section` to the findings the
check emits. Where no clean citation exists, set `spec_source="opinion"`
and demote `severity` to MEDIUM (or LOW).

**Specific verdicts to confirm during the audit (these are my proposals,
re-check during build):**

- `review_fastmcp_manifest` → MCP — primitive name/URI/schema requirements
- `check_tool_name_format` → MCP — naming spec
- `check_uri_stability` → MCP — resource URI stability spec
- `check_tool_description_quality` → MCP — tool descriptions help model select
- `check_prompt_name_format` → FastMCP — Python decorator binding, not MCP
- `check_error_response_design` → opinion — no single spec rule; demote or
  remove from deterministic path

**Tests:**
- Snapshot test on a known-good server (the bundled `notes_server.py`)
  asserting every produced finding has a non-None `spec_source`.

**Done when:** `docs/check-audit.md` exists with one row per check;
every check's findings carry citations; the snapshot test passes.

---

## drop_or_demote_unsourced_checks [done]

**Spec source:** Output of the audit above.

For each check the audit classified as `opinion`:
- If it's only invoked from the `fastmcp-design-review` skill: demote its
  default severity to MEDIUM, leave the tool callable for users who want it.
- If it's never invoked at all (dead code): delete it.

This is the work unit where checks actually leave the deterministic review
path. Specific changes expected:

- `check_error_response_design` — likely demoted; keep callable but skill
  body removes it from automatic invocation.
- Anything else surfaced by the audit.

**Tests:**
- The `fastmcp-design-review` skill body no longer references demoted checks.
- The MCP tool wrappers still exist (they're callable on demand).
- Existing tests for these checks still pass (we don't break the tools, we
  remove them from the auto-fired set).

**Done when:** `skills/fastmcp-design-review/SKILL.md` Layer 2 lists only
checks with `spec_source != "opinion"`.

---

## add_finding_grouping_to_skill_output [done]

**Spec source:** Skill UX.

Update `skills/fastmcp-design-review/SKILL.md` so the output report groups
findings by `spec_source`:

```
### High severity (MCP protocol)
- finding 1 [MCP §tools/error]
- finding 2 [MCP §...]

### High severity (FastMCP framework)
- finding 3 [FastMCP servers/tools.md#error-handling]

### Medium severity
- ...

### Opinion-class findings (informational)
- ...
```

This makes the grounding visible to the user. Anyone reading the report can
follow each citation back to the source spec.

**Tests:**
- A unit test exercising the example output format (just a markdown-level
  snapshot — no code change needed in the checks).
- Manual: run the skill against `wdtk` and confirm the report shape.

**Done when:** SKILL.md describes the grouped output format; design-review
output on wdtk visibly groups by spec source.

---

## check_resource_mime_type_declared [done]

**Spec source:** FastMCP — `https://gofastmcp.com/servers/resources.md`
(the `mime_type=` kwarg is the documented way to declare a content type).
Severity: MEDIUM (FastMCP-recommended, not MCP-required).

AST scan: for every `@mcp.resource(...)` decorator, check that `mime_type=`
is among the keyword arguments. Without it, FastMCP infers from the return
type — often badly.

**Cited rule (verbatim from FastMCP docs):**
> "Declaring a MIME type with `mime_type=...` lets the client display the
> resource correctly without guessing." *(WebFetch the actual page during
> implementation to lock in the exact quote.)*

**Tests:**
- Resource with `mime_type="application/json"` declared → no finding.
- Resource without `mime_type=` → MEDIUM finding citing the FastMCP page.
- Resource where `mime_type=` is set to a non-constant expression → no
  finding (we can't statically verify the value, but the kwarg is present).

**Done when:** running the check against `wdtk-mcp` (which declares
`mime_type` on every resource) returns 0 findings; running it against a
test fixture with a missing `mime_type=` returns the expected MEDIUM.

---

## check_prompt_argument_descriptions [done]

**Spec source:** MCP — `PromptArgument.description` field
(`modelcontextprotocol.io/specification/server/prompts`). Severity: MEDIUM
(MCP says SHOULD, not MUST).

AST scan: for every `@mcp.prompt` decorated function, check that each
function argument has a description — either in the docstring `Args:`
section or as `Annotated[..., Field(description=...)]`. FastMCP picks both
up automatically.

**Cited rule (verbatim from MCP spec, lock in during build):**
> "Prompts SHOULD include descriptions for each argument so that clients
> can guide users."

**Tests:**
- Prompt with `Args:` block listing each parameter → no finding.
- Prompt with `Annotated[X, Field(description=...)]` per arg → no finding.
- Prompt with bare types and no description → MEDIUM finding per missing
  description.

**Done when:** the check against `wdtk-mcp`'s `draft_foi_request` reports
its description state correctly.

---

## check_tool_annotations_declared [done]

**Spec source:** MCP — `ToolAnnotations` field on Tool
(`modelcontextprotocol.io/specification/server/tools#annotations`).
Severity: MEDIUM (MCP says optional but recommended).

AST scan: for every `@mcp.tool(...)` decorated function, check that
`annotations={...}` is provided with at least the four standard hints
(`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`).

**Cited rule:**
> "Tool annotations help clients understand a tool's behavior before
> calling it." *(Lock in the verbatim wording from the MCP spec page
> during build.)*

**Tests:**
- Tool with all four annotations set → no finding.
- Tool with only `readOnlyHint` set → MEDIUM finding listing missing hints.
- Tool with no `annotations=` kwarg → MEDIUM finding.
- Tool body explicitly mutates state but `readOnlyHint=True` → out of scope
  for this check (correctness of annotations is judgment, not declaration).

**Done when:** all three fleet servers (wdtk, bailii, govuk) get accurate
findings on which tools have/don't have annotations.

---

## update_changelog_and_pr [skip]

Not a buildable unit — a checklist for the human (or the build loop
operator) at the end:

- CHANGELOG entry summarising the audit + new checks
- Verify all existing tests pass
- Re-run dogfood against wdtk + bailii; confirm citations appear in output
- Open PR with the spec file referenced

Mark this `[skip]` for the loop and do it manually after the last work unit.
