# Git Cleanup and Plugin Compliance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean up the current branch, ship the Mode 2 tests in a PR, then progressively bring the repo into full Claude Code plugin compliance across three follow-on PRs.

**Architecture:** Four sequential PRs. The first closes the current branch. The next three each add one compliance layer: plugin manifest + structure, settings pattern, and skill quality. Each PR is independently mergeable and leaves the repo in a better state than it found it.

**Tech Stack:** Python 3.13, uv, FastMCP v3, pytest, Claude Code plugin conventions

---

## Branch inventory (current state)

Untracked files on `feat/test-cross-project-mode`:

| File | Action | Reason |
|---|---|---|
| `tests/test_cross_project_mode.py` | **Commit** | Branch purpose — 20 passing Mode 2 tests |
| `docs/plugin-audit.md` | **Commit** | Audit findings for this session |
| `.claude/settings.json` | **Commit** | Project-level Claude Code config (hookify plugin) |
| `.claude/skills/plugin-creator/` | **Delete** | Wrong scope — Codex scaffolder, violates local-first policy |
| `.agents/` | **Delete** | Codex convention directory, not Claude Code standard |
| `skills-lock.json` | **Delete** | Locks the above — no longer needed |

---

## PR 1 — Close `feat/test-cross-project-mode`

**Branch:** `feat/test-cross-project-mode` (current)
**Goal:** Ship Mode 2 tests + audit findings. Remove wrong-scope files. Clean tree.

### Task 1: Remove wrong-scope files

**Files:**
- Delete: `.claude/skills/plugin-creator/` (whole directory)
- Delete: `.agents/` (whole directory)
- Delete: `skills-lock.json`

- [ ] **Step 1: Delete wrong-scope directories and lock file**

```bash
rm -rf .claude/skills/plugin-creator
rm -rf .agents
rm skills-lock.json
```

- [ ] **Step 2: Verify deletions**

```bash
git status
```

Expected: `.claude/skills/plugin-creator`, `.agents/`, and `skills-lock.json` no longer appear in untracked files.

---

### Task 2: Commit project Claude Code settings

**Files:**
- Add: `.claude/settings.json`

- [ ] **Step 1: Stage settings file**

```bash
git add .claude/settings.json
```

- [ ] **Step 2: Commit**

```bash
git commit -m "chore: add project-level Claude Code settings (enable hookify plugin)"
```

---

### Task 3: Commit Mode 2 tests

**Files:**
- Add: `tests/test_cross_project_mode.py`

- [ ] **Step 1: Run the full test suite to confirm all pass**

```bash
uv run pytest -v
```

Expected: 20 Mode 2 tests pass, all other tests pass, no failures.

- [ ] **Step 2: Stage the test file**

```bash
git add tests/test_cross_project_mode.py
```

- [ ] **Step 3: Commit**

```bash
git commit -m "feat: add Mode 2 cross-project advisory tests

Verifies that docs, examples, and advisory tools work correctly
when the server CWD is a foreign project. Tests ROOT derivation,
env-var wiring (via importlib.reload), error paths, CWD isolation,
and the no-writes-to-CWD invariant."
```

---

### Task 4: Commit audit findings

**Files:**
- Add: `docs/plugin-audit.md`
- Add: `docs/superpowers/plans/2026-05-10-git-cleanup-and-plugin-compliance.md`

- [ ] **Step 1: Stage audit and plan docs**

```bash
git add docs/plugin-audit.md docs/superpowers/plans/2026-05-10-git-cleanup-and-plugin-compliance.md
```

- [ ] **Step 2: Commit**

```bash
git commit -m "docs: add plugin compliance audit and implementation plan"
```

---

### Task 5: Open PR for feat/test-cross-project-mode

- [ ] **Step 1: Push branch**

```bash
git push -u origin feat/test-cross-project-mode
```

- [ ] **Step 2: Open PR**

```bash
gh pr create \
  --title "feat: Mode 2 cross-project tests + plugin compliance audit" \
  --body "$(cat <<'EOF'
## Summary

- Adds 20 passing tests for Mode 2 (cross-project advisory) CWD isolation
- Tests env-var wiring, ROOT derivation, error paths, and the no-writes invariant
- Removes wrong-scope files (Codex plugin-creator, .agents/, skills-lock.json)
- Adds project-level Claude Code settings (.claude/settings.json)
- Adds plugin compliance audit (docs/plugin-audit.md) and follow-on implementation plan

## Test plan

- [ ] `uv run pytest -v` — all tests pass
- [ ] No untracked files remain after the three deletions

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## PR 2 — Plugin manifest and structure

**Branch:** `feat/plugin-manifest` (create from main after PR 1 merges)
**Goal:** Make this a real Claude Code plugin. Move skills and commands to standard locations. Fix dead references.

### Task 6: Create branch

**Files:** (none yet)

- [ ] **Step 1: Checkout main and pull**

```bash
git checkout main && git pull origin main
```

- [ ] **Step 2: Create feature branch**

```bash
git checkout -b feat/plugin-manifest
```

---

### Task 7: Create plugin manifest

**Files:**
- Create: `.claude-plugin/plugin.json`

- [ ] **Step 1: Create directory and manifest**

```bash
mkdir -p .claude-plugin
```

Write `.claude-plugin/plugin.json`:

```json
{
  "name": "fastmcp-builder",
  "version": "0.3.0",
  "description": "FastMCP server builder and advisor — teaches MCP primitive design, reviews server designs, and scaffolds local-first FastMCP servers.",
  "author": {
    "name": "paulieb89",
    "email": "paulboucherat@gmail.com"
  },
  "homepage": "https://github.com/paulieb89/fastmcp-builder-template",
  "repository": "https://github.com/paulieb89/fastmcp-builder-template",
  "license": "MIT",
  "keywords": ["fastmcp", "mcp", "claude-code", "server-builder"]
}
```

- [ ] **Step 2: Verify manifest is valid JSON**

```bash
python3 -c "import json; json.load(open('.claude-plugin/plugin.json')); print('valid')"
```

Expected: `valid`

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "feat: add Claude Code plugin manifest"
```

---

### Task 8: Move skills to plugin-root location

**Files:**
- Create: `skills/mcp-primitive-classification/SKILL.md`
- Create: `skills/fastmcp-design-review/SKILL.md`
- Create: `skills/fastmcp-scaffold-author/SKILL.md`
- Create: `skills/fastmcp-build-loop/SKILL.md`
- Delete: `.claude/skills/` (all contents)

- [ ] **Step 1: Create skills/ directory and move all four skills**

```bash
mkdir -p skills
cp -r .claude/skills/mcp-primitive-classification skills/
cp -r .claude/skills/fastmcp-design-review skills/
cp -r .claude/skills/fastmcp-scaffold-author skills/
cp -r .claude/skills/fastmcp-build-loop skills/
rm -rf .claude/skills
```

- [ ] **Step 2: Verify structure**

```bash
find skills/ -name "SKILL.md"
```

Expected output (all four):
```
skills/mcp-primitive-classification/SKILL.md
skills/fastmcp-design-review/SKILL.md
skills/fastmcp-scaffold-author/SKILL.md
skills/fastmcp-build-loop/SKILL.md
```

- [ ] **Step 3: Commit**

```bash
git add skills/ .claude/
git commit -m "refactor: move skills from .claude/skills/ to plugin-root skills/"
```

---

### Task 9: Migrate legacy commands to skills

**Files:**
- Create: `skills/review-manifest/SKILL.md` (from `.claude/commands/review-manifest.md`)
- Create: `skills/design-fastmcp/SKILL.md` (from `.claude/commands/design-fastmcp.md`)
- Create: `skills/add-tool/SKILL.md` (from `.claude/commands/add-tool.md`)
- Delete: `.claude/commands/` (all contents)

- [ ] **Step 1: Create skill dirs for each legacy command**

```bash
mkdir -p skills/review-manifest skills/design-fastmcp skills/add-tool
```

- [ ] **Step 2: Write `skills/review-manifest/SKILL.md`**

```markdown
---
name: review-manifest
description: Review a FastMCP server manifest for primitive boundary issues, naming problems, and scope violations. Use when asked to review or audit a FastMCP server design, check a manifest, or validate server structure.
disable-model-invocation: true
allowed-tools: mcp__fastmcp-builder__review_fastmcp_manifest
---

Call `review_fastmcp_manifest` with the server's manifest content.
Present the findings grouped by: primitive boundaries, naming, scope, and error design.
Flag any critical issues first, then important, then minor.
```

- [ ] **Step 3: Write `skills/design-fastmcp/SKILL.md`**

```markdown
---
name: design-fastmcp
description: Design a new FastMCP server from scratch using the design_fastmcp_server prompt. Use when asked to create, plan, or design a FastMCP server, or when starting a new MCP server project.
disable-model-invocation: true
---

Invoke the `design_fastmcp_server` MCP prompt to begin structured server design.
Walk the user through: purpose, primitives needed, tool contracts, resource URIs, and prompt workflows.
Confirm the design before any implementation begins.
```

- [ ] **Step 4: Write `skills/add-tool/SKILL.md`**

```markdown
---
name: add-tool
description: Add a new tool to an existing FastMCP server using contract-first design. Use when asked to add a tool, implement a new capability, or extend a server with new functionality.
disable-model-invocation: true
allowed-tools: mcp__fastmcp-builder__suggest_tool_contract mcp__fastmcp-builder__check_tool_name_format mcp__fastmcp-builder__check_tool_description_quality
---

Before writing any code:
1. Call `suggest_tool_contract` with the user's description of what the tool should do.
2. Call `check_tool_name_format` on the proposed name.
3. Call `check_tool_description_quality` on the proposed description.
4. Present the contract to the user and get confirmation.
5. Only then implement the tool in `src/fastmcp_builder/server.py`.
6. Write a test in `tests/`.
7. Run `uv run pytest` — all tests must pass before committing.
```

- [ ] **Step 5: Delete legacy commands directory**

```bash
rm -rf .claude/commands
```

- [ ] **Step 6: Commit**

```bash
git add skills/ .claude/
git commit -m "refactor: migrate legacy commands to skills/"
```

---

### Task 10: Fix CLAUDE.md — dead reference and skill table

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Open CLAUDE.md and locate the Skills table and task-observer reference**

Read `CLAUDE.md` and find:
1. The `## Skills` table that maps "when you want to..." to skill invocations
2. Any `task-observer` mention

- [ ] **Step 2: Update the skills table to reflect new locations and add migrated commands**

Replace the existing skills table with:

```markdown
## Skills

Use these project-scoped skills — invoke with `/skill-name`:

| When you want to...                          | Use                         |
|----------------------------------------------|-----------------------------|
| Decide if something is a tool/resource/prompt | `/mcp-primitive-classification` |
| Review an existing or proposed server design  | `/fastmcp-design-review`    |
| Create a new FastMCP server from scratch      | `/fastmcp-scaffold-author`  |
| Add tools/resources/prompts from a spec file  | `/fastmcp-build-loop`       |
| Review a server manifest                      | `/review-manifest`          |
| Design a new server interactively             | `/design-fastmcp`           |
| Add a single new tool (contract-first)        | `/add-tool`                 |
```

- [ ] **Step 3: Remove the task-observer instruction from CLAUDE.md**

Find and remove the paragraph that says to invoke `/task-observer` at the start of every session (it references a skill that does not exist in this repo).

- [ ] **Step 4: Run tests to confirm nothing broken**

```bash
uv run pytest -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md skill table, remove dead task-observer reference"
```

---

### Task 11: Fix .mcp.json — replace ${PWD} with ${CLAUDE_PLUGIN_ROOT}

**Files:**
- Modify: `.mcp.json`

- [ ] **Step 1: Update env vars in .mcp.json**

Replace:
```json
"env": {
  "FASTMCP_BUILDER_DOCS_DIR": "${PWD}/docs",
  "FASTMCP_BUILDER_EXAMPLES_DIR": "${PWD}/examples"
}
```

With:
```json
"env": {
  "FASTMCP_BUILDER_DOCS_DIR": "${CLAUDE_PLUGIN_ROOT}/docs",
  "FASTMCP_BUILDER_EXAMPLES_DIR": "${CLAUDE_PLUGIN_ROOT}/examples"
}
```

- [ ] **Step 2: Verify JSON is valid**

```bash
python3 -c "import json; json.load(open('.mcp.json')); print('valid')"
```

Expected: `valid`

- [ ] **Step 3: Commit**

```bash
git add .mcp.json
git commit -m "fix: use CLAUDE_PLUGIN_ROOT for portable MCP server paths"
```

---

### Task 12: Open PR 2

- [ ] **Step 1: Push branch**

```bash
git push -u origin feat/plugin-manifest
```

- [ ] **Step 2: Open PR**

```bash
gh pr create \
  --title "feat: Claude Code plugin manifest and structure compliance" \
  --body "$(cat <<'EOF'
## Summary

- Adds `.claude-plugin/plugin.json` — makes this a discoverable Claude Code plugin
- Moves skills from `.claude/skills/` to `skills/` at plugin root (standard location)
- Migrates 3 legacy `commands/` files to proper `skills/` entries with frontmatter
- Fixes `${PWD}` → `${CLAUDE_PLUGIN_ROOT}` in `.mcp.json` for portability
- Updates `CLAUDE.md` skill table; removes dead `task-observer` reference

## Test plan

- [ ] `uv run pytest -v` — all tests pass
- [ ] `python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"` — manifest valid
- [ ] `find skills/ -name SKILL.md | wc -l` — returns 7 (4 original + 3 migrated)
- [ ] No `.claude/skills/` or `.claude/commands/` directories remain

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## PR 3 — Plugin settings pattern

**Branch:** `feat/plugin-settings` (create from main after PR 2 merges)
**Goal:** Add per-project settings file support. Protect it from git. Document it.

### Task 13: Create branch

- [ ] **Step 1**

```bash
git checkout main && git pull origin main && git checkout -b feat/plugin-settings
```

---

### Task 14: Add .gitignore protection for local settings

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Append to .gitignore**

Add to `.gitignore`:

```gitignore
# Per-project Claude Code plugin settings (user-local, not committed)
.claude/*.local.md
.claude/*.local.json
```

- [ ] **Step 2: Commit**

```bash
git add .gitignore
git commit -m "chore: gitignore per-project Claude plugin settings files"
```

---

### Task 15: Create settings template and documentation

**Files:**
- Create: `docs/plugin-settings-template.md`
- Modify: `README.md`

- [ ] **Step 1: Create settings template at `docs/plugin-settings-template.md`**

```markdown
# FastMCP Builder — Per-Project Settings

Copy this file to `.claude/fastmcp-builder.local.md` in your project to configure
the FastMCP Builder plugin for that project. Do not commit this file — it is
gitignored by design.

---
enabled: true

# in-repo  — using this repo to build/extend the fastmcp-builder itself
# cross-project — pointing another project's .mcp.json at this server as an advisor
mode: in-repo

# Override the docs directory the server reads from.
# Leave blank to use the default (docs/ inside the fastmcp-builder-template).
# In cross-project mode, point this at docs relevant to the project being advised.
docs_dir: ""

# Override the examples directory.
# Leave blank to use the default (examples/ inside the fastmcp-builder-template).
examples_dir: ""

# Cross-project mode only: name and goal of the project being advised.
# Claude uses this to frame design feedback without reading the target codebase.
advisory_project: ""
advisory_project_goal: ""

# Remove skills that are not relevant to the current mode.
# fastmcp-build-loop is only useful in-repo (it references src/ paths).
active_skills:
  - mcp-primitive-classification
  - fastmcp-design-review
  - fastmcp-scaffold-author
  - fastmcp-build-loop
---

<!-- Add project-specific context here. Claude reads this during skill invocations. -->
<!-- Example: "This project uses a custom URI scheme acme://. Treat it as stable." -->
```

- [ ] **Step 2: Add a Configuration section to README.md**

Find the existing Mode 2 section in `README.md` and append after it:

```markdown
### Per-Project Configuration

Copy `docs/plugin-settings-template.md` to `.claude/fastmcp-builder.local.md` in
any project that uses this server. Edit the frontmatter to match your setup.
The file is gitignored — it is per-machine and per-project.
```

- [ ] **Step 3: Run tests**

```bash
uv run pytest -v
```

Expected: all pass.

- [ ] **Step 4: Commit**

```bash
git add docs/plugin-settings-template.md README.md
git commit -m "docs: add per-project settings template and README section"
```

---

### Task 16: Open PR 3

- [ ] **Step 1: Push and open PR**

```bash
git push -u origin feat/plugin-settings
gh pr create \
  --title "feat: plugin settings pattern — per-project configuration" \
  --body "$(cat <<'EOF'
## Summary

- Adds `.gitignore` protection for `.claude/*.local.md` files
- Adds `docs/plugin-settings-template.md` — copy to `.claude/fastmcp-builder.local.md` to configure per project
- Documents the settings pattern in README
- Covers in-repo vs cross-project mode, docs/examples dir overrides, advisory context fields

## Test plan

- [ ] `uv run pytest -v` — all tests pass
- [ ] `echo ".claude/test.local.md" > .claude/test.local.md && git status` — file not tracked

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## PR 4 — Skill quality improvements

**Branch:** `feat/skill-improvements` (create from main after PR 3 merges)
**Goal:** Fix the four core skills so they actually use the MCP server's tools. Fix runtime bugs (`${1}`, hardcoded model name). Sharpen trigger descriptions.

### Task 17: Create branch

- [ ] **Step 1**

```bash
git checkout main && git pull origin main && git checkout -b feat/skill-improvements
```

---

### Task 18: Fix fastmcp-build-loop — runtime bugs

**Files:**
- Modify: `skills/fastmcp-build-loop/SKILL.md`

Two bugs to fix: `${1}` shell variable that Claude Code does not expand, and a hardcoded model name in the commit template.

- [ ] **Step 1: Add `argument-hint` to frontmatter and replace `${1}` with prose**

In `skills/fastmcp-build-loop/SKILL.md`, update the frontmatter from:
```yaml
---
name: fastmcp-build-loop
description: ...
---
```
to:
```yaml
---
name: fastmcp-build-loop
description: ...
argument-hint: [path/to/spec.md]
---
```

Then find every occurrence of `${1}` in the body and replace with `the spec file the user provides` or rewrite the surrounding instruction so Claude knows to ask for the path if not provided as an argument.

- [ ] **Step 2: Replace hardcoded model name in commit template**

Find the line that produces a commit message containing `Claude Sonnet 4.6` and replace with:
```
Co-Authored-By: Claude <noreply@anthropic.com>
```

- [ ] **Step 3: Replace filesystem doc paths with MCP resource URIs**

In the doc reference table, replace entries like `docs/tool-design.md` with `fastmcp-builder://docs/tool-design` so Claude uses the MCP resource rather than the Read tool.

- [ ] **Step 4: Commit**

```bash
git add skills/fastmcp-build-loop/SKILL.md
git commit -m "fix: resolve runtime bugs in fastmcp-build-loop skill"
```

---

### Task 19: Fix fastmcp-design-review — wire up MCP review tools

**Files:**
- Modify: `skills/fastmcp-design-review/SKILL.md`

- [ ] **Step 1: Add `allowed-tools` frontmatter and rewrite body to call review tools**

Update frontmatter to include:
```yaml
allowed-tools: mcp__fastmcp-builder__review_fastmcp_manifest mcp__fastmcp-builder__check_tool_description_quality mcp__fastmcp-builder__check_error_response_design mcp__fastmcp-builder__check_uri_stability
```

Rewrite the body so the review sequence is:
1. Call `review_fastmcp_manifest` on the server design — present results
2. Call `check_tool_description_quality` for each tool description
3. Call `check_uri_stability` for each resource URI
4. Call `check_error_response_design` for error handling patterns
5. Summarise: critical issues, important issues, minor issues

Replace the static checklist with this structured tool-calling workflow.

- [ ] **Step 2: Commit**

```bash
git add skills/fastmcp-design-review/SKILL.md
git commit -m "fix: wire fastmcp-design-review to MCP review tools"
```

---

### Task 20: Fix mcp-primitive-classification — use the classify tool

**Files:**
- Modify: `skills/mcp-primitive-classification/SKILL.md`

- [ ] **Step 1: Add `allowed-tools` and update body**

Add to frontmatter:
```yaml
allowed-tools: mcp__fastmcp-builder__classify_mcp_primitive
```

Rewrite the body so it:
1. Calls `classify_mcp_primitive` with the user's capability description
2. Presents the recommendation with the reasoning
3. If ambiguous, applies the three classification rules from the existing body as a tiebreaker

Sharpen the `description` trigger phrases:
```
Classify a proposed MCP capability as a tool, resource, or prompt. Use when the user asks "should this be a tool or a resource?", "which primitive fits X?", or is deciding how to expose a new capability before writing any code.
```

- [ ] **Step 2: Commit**

```bash
git add skills/mcp-primitive-classification/SKILL.md
git commit -m "fix: wire mcp-primitive-classification to classify_mcp_primitive tool"
```

---

### Task 21: Fix fastmcp-scaffold-author — wire up planning tools and disambiguate

**Files:**
- Modify: `skills/fastmcp-scaffold-author/SKILL.md`

- [ ] **Step 1: Add `allowed-tools`, update description, add tool-calling workflow**

Add to frontmatter:
```yaml
allowed-tools: mcp__fastmcp-builder__generate_minimal_server_plan mcp__fastmcp-builder__suggest_tool_contract mcp__fastmcp-builder__suggest_resource_contract mcp__fastmcp-builder__suggest_prompt_contract
```

Update `description` to distinguish from `fastmcp-build-loop`:
```
Scaffold a new FastMCP server from scratch — use this when starting a brand new server with no existing code. For adding tools/resources/prompts to an existing server from a spec, use fastmcp-build-loop instead.
```

Rewrite the body workflow:
1. Call `generate_minimal_server_plan` with the user's server description
2. For each tool in the plan, call `suggest_tool_contract`
3. For each resource, call `suggest_resource_contract`
4. Present the full scaffold plan for user confirmation
5. Only then write the scaffold code following FastMCP v3 patterns

- [ ] **Step 2: Commit**

```bash
git add skills/fastmcp-scaffold-author/SKILL.md
git commit -m "fix: wire fastmcp-scaffold-author to planning tools, disambiguate from build-loop"
```

---

### Task 22: Run full test suite and open PR 4

- [ ] **Step 1: Run all tests**

```bash
uv run pytest -v
```

Expected: all tests pass.

- [ ] **Step 2: Push and open PR**

```bash
git push -u origin feat/skill-improvements
gh pr create \
  --title "fix: skill quality improvements — wire MCP tools, fix runtime bugs" \
  --body "$(cat <<'EOF'
## Summary

- `fastmcp-build-loop`: fixes `${1}` runtime bug, adds `argument-hint`, replaces hardcoded model name, switches doc references to MCP resource URIs
- `fastmcp-design-review`: adds `allowed-tools`, rewrites body to call `review_fastmcp_manifest`, `check_tool_description_quality`, `check_error_response_design`, `check_uri_stability`
- `mcp-primitive-classification`: adds `allowed-tools`, calls `classify_mcp_primitive`, sharpens trigger description
- `fastmcp-scaffold-author`: adds `allowed-tools`, calls `generate_minimal_server_plan`, disambiguates from `fastmcp-build-loop`

## Test plan

- [ ] `uv run pytest -v` — all tests pass
- [ ] Each skill SKILL.md has `allowed-tools` frontmatter
- [ ] No `${1}` references remain in any SKILL.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Self-review

**Spec coverage check:**
- ✅ Remove wrong-scope files (Task 1)
- ✅ Plugin manifest created (Task 7)
- ✅ Skills moved to standard location (Task 8)
- ✅ Commands migrated to skills (Task 9)
- ✅ CLAUDE.md dead reference removed (Task 10)
- ✅ `${PWD}` → `${CLAUDE_PLUGIN_ROOT}` (Task 11)
- ✅ `.gitignore` covers `*.local.md` (Task 14)
- ✅ Settings template created (Task 15)
- ✅ `fastmcp-build-loop` `${1}` bug fixed (Task 18)
- ✅ All four skills wired to MCP tools (Tasks 18-21)
- ✅ Trigger disambiguation between scaffold-author and build-loop (Task 21)

**Not in scope (separate work):**
- Hook implementation (`hooks/hooks.json`) — no hooks designed yet
- Agent definitions (`agents/`) — no agents designed yet
- Skill behavioral tests — no testing framework for skill invocations exists

**Placeholder scan:** No TBDs, no "implement later", no vague steps. All code blocks are complete.
