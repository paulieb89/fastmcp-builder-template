# FastMCP Builder Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn this repository into a working Claude Code plugin so the FastMCP Builder MCP server, skills, and commands can be installed in any project via `/plugin install <git-url>`.

**Architecture:** The plugin is wired entirely through `.claude-plugin/plugin.json`. Skills and commands move from `.claude/{skills,commands}` (project-scoped config) to `skills/` and `commands/` (plugin-root auto-discovery). The MCP server is declared inline in the manifest's `mcpServers` field — not in a separate `.mcp.json` — because a `.mcp.json` at repo root would also be picked up as project-scoped config and cause a duplicate-registration collision when this repo is opened in Claude Code. All intra-plugin paths use `${CLAUDE_PLUGIN_ROOT}` so the server reads its own bundled docs/examples regardless of the host project's directory. In-repo development no longer auto-loads the server; contributors run it directly with `uv run fastmcp run …` when needed.

**Tech Stack:** Python 3.11+, `uv`, FastMCP v3.2.4, Pydantic v2, pytest. Claude Code plugin format (`.claude-plugin/plugin.json` with inline `mcpServers`).

**Decisions locked in earlier:**

- Move skills/commands to plugin root (not path overrides).
- Delete root `.mcp.json`; declare `mcpServers` inline in `plugin.json`.
- Align versions — bump `pyproject.toml` from 0.2.0 to 0.3.0 to match `plugin.json`.
- Distribution: git URL install only for now (no marketplace).
- Server key in `mcpServers` = `srv` to shorten tool names from `mcp__plugin_fastmcp-builder_fastmcp-builder__<tool>` to `mcp__plugin_fastmcp-builder_srv__<tool>`.

**Out of scope:**

- Marketplace submission.
- A scaffold/init story for "use this template to start a new MCP server" (deferred Goal A).
- `allowed-tools` frontmatter on commands (better addressed once smoke-test confirms the actual prefixed names).
- Smoke-test in another project (separate plan; PR 2).

---

## File Structure

**Created:**

- `skills/mcp-primitive-classification/SKILL.md` (moved from `.claude/skills/`)
- `skills/fastmcp-design-review/SKILL.md` (moved)
- `skills/fastmcp-scaffold-author/SKILL.md` (moved)
- `skills/fastmcp-build-loop/SKILL.md` (moved)
- `commands/design-fastmcp.md` (moved from `.claude/commands/`)
- `commands/add-tool.md` (moved)
- `commands/review-manifest.md` (moved)

**Modified:**

- `.claude-plugin/plugin.json` — add `mcpServers.srv` block.
- `pyproject.toml` — bump `version` to `0.3.0`.
- `CHANGELOG.md` — add `0.3.0` entry under the existing format.
- `README.md` — replace "Using With Claude Code" section with plugin-install flow.
- `docs/claude-code-workflow.md` — rewrite Modes 1 and 2 around plugin install.
- `CONTRIBUTING.md` — add a release-verification step covering plugin smoke-test.

**Deleted:**

- `.mcp.json` (root) — replaced by inline `mcpServers` in the plugin manifest.
- `.claude/skills/` and `.claude/commands/` (after `git mv`).

---

### Task 1: Create feature branch

**Files:**

- None (git operation).

- [ ] **Step 1: Branch off `feat/plugin-manifest`**

Run:

```bash
git checkout feat/plugin-manifest
git pull origin feat/plugin-manifest 2>/dev/null || true
git checkout -b feat/wire-plugin-components
```

Expected: new branch `feat/wire-plugin-components` checked out.

- [ ] **Step 2: Verify clean working tree**

Run: `git status --short`

Expected: empty output (no uncommitted changes).

---

### Task 2: Move skills to plugin root

**Files:**

- Move: `.claude/skills/mcp-primitive-classification/SKILL.md` → `skills/mcp-primitive-classification/SKILL.md`
- Move: `.claude/skills/fastmcp-design-review/SKILL.md` → `skills/fastmcp-design-review/SKILL.md`
- Move: `.claude/skills/fastmcp-scaffold-author/SKILL.md` → `skills/fastmcp-scaffold-author/SKILL.md`
- Move: `.claude/skills/fastmcp-build-loop/SKILL.md` → `skills/fastmcp-build-loop/SKILL.md`

- [ ] **Step 1: Move skills directory**

Run:

```bash
git mv .claude/skills skills
```

Expected: no output; `git status` shows 4 renames (one per skill directory's SKILL.md).

- [ ] **Step 2: Verify new layout**

Run: `ls skills/`

Expected output:

```
fastmcp-build-loop
fastmcp-design-review
fastmcp-scaffold-author
mcp-primitive-classification
```

- [ ] **Step 3: Confirm each SKILL.md is present**

Run: `find skills -name SKILL.md`

Expected: 4 paths, one per skill directory.

---

### Task 3: Move commands to plugin root

**Files:**

- Move: `.claude/commands/design-fastmcp.md` → `commands/design-fastmcp.md`
- Move: `.claude/commands/add-tool.md` → `commands/add-tool.md`
- Move: `.claude/commands/review-manifest.md` → `commands/review-manifest.md`

- [ ] **Step 1: Move commands directory**

Run:

```bash
git mv .claude/commands commands
```

Expected: no output; `git status` shows 3 renames.

- [ ] **Step 2: Verify new layout**

Run: `ls commands/`

Expected output:

```
add-tool.md
design-fastmcp.md
review-manifest.md
```

- [ ] **Step 3: Remove now-empty .claude directory**

Run:

```bash
rmdir .claude 2>/dev/null && echo "removed" || echo "not empty — investigate"
```

Expected: `removed`. If `not empty`, run `ls .claude/` and decide case-by-case (likely a hidden file we missed).

---

### Task 4: Delete root .mcp.json

**Files:**

- Delete: `.mcp.json`

- [ ] **Step 1: Remove the file**

Run:

```bash
git rm .mcp.json
```

Expected: `rm '.mcp.json'`.

- [ ] **Step 2: Verify removal**

Run: `ls .mcp.json 2>&1`

Expected: `ls: cannot access '.mcp.json': No such file or directory`.

---

### Task 5: Wire mcpServers into plugin.json

**Files:**

- Modify: `.claude-plugin/plugin.json`

- [ ] **Step 1: Replace the manifest contents**

Use Edit/Write to make `.claude-plugin/plugin.json` exactly:

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
  "keywords": ["fastmcp", "mcp", "claude-code", "server-builder"],
  "mcpServers": {
    "srv": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "${CLAUDE_PLUGIN_ROOT}",
        "fastmcp",
        "run",
        "${CLAUDE_PLUGIN_ROOT}/src/fastmcp_builder/server.py:mcp"
      ],
      "env": {
        "FASTMCP_BUILDER_DOCS_DIR": "${CLAUDE_PLUGIN_ROOT}/docs",
        "FASTMCP_BUILDER_EXAMPLES_DIR": "${CLAUDE_PLUGIN_ROOT}/examples"
      }
    }
  }
}
```

Why `srv`: the plugin loader exposes tools as `mcp__plugin_<plugin>_<server>__<tool>`. Using `srv` as the server key avoids the duplicated `fastmcp-builder_fastmcp-builder` segment and keeps tool names readable.

Why `--project ${CLAUDE_PLUGIN_ROOT}`: when Claude Code launches the server, the working directory is the host project, not the plugin. Without `--project`, `uv run` would look for `pyproject.toml` in the host project and fail or pick up the wrong environment.

- [ ] **Step 2: Validate the JSON**

Run:

```bash
python -c "import json,sys; json.load(open('.claude-plugin/plugin.json')); print('ok')"
```

Expected: `ok`.

- [ ] **Step 3: Confirm version matches what we'll set in pyproject.toml**

Run: `grep '"version"' .claude-plugin/plugin.json`

Expected: `  "version": "0.3.0",`

---

### Task 6: Bump pyproject.toml version

**Files:**

- Modify: `pyproject.toml:3` (the `version` line)

- [ ] **Step 1: Update the version field**

Edit `pyproject.toml`. Replace:

```toml
version = "0.2.0"
```

with:

```toml
version = "0.3.0"
```

- [ ] **Step 2: Verify**

Run: `grep '^version' pyproject.toml`

Expected: `version = "0.3.0"`.

- [ ] **Step 3: Refresh uv.lock**

Run: `uv sync`

Expected: command completes without errors; `uv.lock` may update to reflect the new version.

---

### Task 7: Update CHANGELOG.md

**Files:**

- Modify: `CHANGELOG.md`

- [ ] **Step 1: Replace the `## Unreleased` section with a 0.3.0 entry**

Edit `CHANGELOG.md`. Change:

```markdown
## Unreleased

## 0.2.0
```

to:

```markdown
## Unreleased

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
```

- [ ] **Step 2: Verify**

Run: `head -25 CHANGELOG.md`

Expected: the new `## 0.3.0` block appears between `## Unreleased` and `## 0.2.0`.

---

### Task 8: Update README.md install instructions

**Files:**

- Modify: `README.md` — the "Using With Claude Code" section.

- [ ] **Step 1: Replace the install section**

In `README.md`, locate the `## Using With Claude Code` section (currently describes `.mcp.json` discovery). Replace from `## Using With Claude Code` through (and including) the cross-project advisor paragraph that mentions `uv --directory` and `docs/claude-code-workflow.md`, with:

```markdown
## Install as a Claude Code Plugin

Install this repository as a Claude Code plugin to make the FastMCP Builder
tools, resources, prompts, skills, and slash commands available in any
project:

```bash
/plugin install https://github.com/paulieb89/fastmcp-builder-template
```

Prerequisites:

- `uv` must be installed and on `$PATH`. The plugin runs the MCP server with
  `uv run --project ${CLAUDE_PLUGIN_ROOT} …`, so `uv` is a hard requirement.

After install, confirm the server registered:

```text
/mcp
```

Expected: a server named `fastmcp-builder` (server key `srv`) appears.
Tools surface as `mcp__plugin_fastmcp-builder_srv__<tool_name>` (for example
`mcp__plugin_fastmcp-builder_srv__classify_mcp_primitive`).

Skills and slash commands auto-discover from the plugin:

- Slash commands: `/design-fastmcp`, `/add-tool`, `/review-manifest`
- Skills (loaded by Claude on matching prompts): see the table below

### In-Repo Development

When working **on** this template, you don't need the plugin server running.
Run the MCP server directly to test changes:

```bash
uv sync
uv run fastmcp run src/fastmcp_builder/server.py:mcp
```

To exercise the plugin end-to-end while developing, install it from your
local checkout in a separate test project (see
[docs/claude-code-workflow.md](docs/claude-code-workflow.md)).
```

- [ ] **Step 2: Verify the file still renders cleanly**

Run: `grep -n "## " README.md`

Expected: section headings present in a sensible order — `## Prerequisites`, `## Quick Start`, `## Install as a Claude Code Plugin`, `## In-Repo Development`, `## What This Template Teaches`, `## Included Builder Capabilities`, `## Local Boundaries`, `## Contributing`. Order doesn't need to be exact, but every section should be present.

---

### Task 9: Rewrite docs/claude-code-workflow.md modes

**Files:**

- Modify: `docs/claude-code-workflow.md` (full rewrite)

- [ ] **Step 1: Replace the file contents**

Write `docs/claude-code-workflow.md` to exactly:

```markdown
# Claude Code Workflow

This repository supports two usage modes.

## Mode 1: Use as an Installed Plugin (Cross-Project)

Install the plugin in any project you want builder assistance in:

```bash
/plugin install https://github.com/paulieb89/fastmcp-builder-template
```

After install:

- The `fastmcp-builder` MCP server starts automatically and surfaces its
  tools under `mcp__plugin_fastmcp-builder_srv__*`.
- Slash commands `/design-fastmcp`, `/add-tool`, and `/review-manifest`
  become available.
- Skills (`mcp-primitive-classification`, `fastmcp-design-review`,
  `fastmcp-scaffold-author`, `fastmcp-build-loop`) activate automatically
  when their descriptions match the conversation.

The server reads its own bundled docs and examples from
`${CLAUDE_PLUGIN_ROOT}/docs` and `${CLAUDE_PLUGIN_ROOT}/examples`. It does
not write into the host project.

## Mode 2: Develop the Template Itself (In-Repo)

When working on this repository, the plugin server is not auto-loaded
(there is no project-scoped `.mcp.json`). Run the server directly to test
your changes:

```bash
uv sync
uv run fastmcp run src/fastmcp_builder/server.py:mcp
```

Recommended development pattern:

1. Explore the relevant files.
2. Classify primitives before implementation.
3. Plan the smallest useful change.
4. Add tests with the code.
5. Run `uv run pytest`.
6. For resources: verify `mime_type` is declared on every `@mcp.resource`
   decorator.

To verify your in-progress changes work as a plugin, install the plugin
from your local checkout into a separate test project:

```bash
/plugin install /absolute/path/to/fastmcp-builder-template
```

Restart Claude Code in the test project and run `/mcp` to confirm the
server registered.
```

- [ ] **Step 2: Verify**

Run: `head -10 docs/claude-code-workflow.md`

Expected: the new `# Claude Code Workflow` header and Mode 1 intro.

---

### Task 10: Add release-verification step to CONTRIBUTING.md

**Files:**

- Modify: `CONTRIBUTING.md` — the "Release Verification" section.

- [ ] **Step 1: Locate the existing release-verification section**

Run: `grep -n "Release Verification" CONTRIBUTING.md`

Expected: a heading line. If absent, scroll to the end of the file and add a new section at the end.

- [ ] **Step 2: Replace or append the section**

Edit `CONTRIBUTING.md`. Replace the existing "Release Verification" section (or append, if missing) with:

```markdown
## Release Verification

Before tagging a release that bumps the plugin version, verify both
in-repo and plugin install paths.

### In-repo verification

```bash
git clone https://github.com/paulieb89/fastmcp-builder-template.git /tmp/fastmcp-builder-template-check
cd /tmp/fastmcp-builder-template-check
uv sync
uv run fastmcp version
uv run pytest
uv run fastmcp run src/fastmcp_builder/server.py:mcp
```

### Plugin install verification

In a clean test project (any directory), run:

```text
/plugin install /tmp/fastmcp-builder-template-check
/mcp
```

Expected: a server named `fastmcp-builder` (server key `srv`) appears, and
its tools surface as `mcp__plugin_fastmcp-builder_srv__<tool_name>`. Run
one tool (for example `classify_mcp_primitive`) and confirm the response
shape matches the Pydantic models in `src/fastmcp_builder/models.py`.
```

- [ ] **Step 3: Verify**

Run: `grep -A 2 "Release Verification" CONTRIBUTING.md | head -10`

Expected: the new section heading and intro paragraph.

---

### Task 11: Full verification

**Files:**

- None (verification only).

- [ ] **Step 1: Run the test suite**

Run: `uv run pytest`

Expected: all tests pass (current count: ~8 test files).

- [ ] **Step 2: Smoke-test the server runs directly**

Run:

```bash
uv run fastmcp run src/fastmcp_builder/server.py:mcp --help 2>&1 | head -5
```

Expected: usage output without traceback. (We pass `--help` so it exits cleanly without holding a stdio connection.)

- [ ] **Step 3: Validate the manifest JSON one more time**

Run:

```bash
python -c "import json; m = json.load(open('.claude-plugin/plugin.json')); assert m['name']=='fastmcp-builder' and m['version']=='0.3.0' and 'srv' in m['mcpServers']; print('manifest ok')"
```

Expected: `manifest ok`.

- [ ] **Step 4: Confirm layout sanity**

Run:

```bash
test -d skills && test -d commands && test ! -e .mcp.json && test ! -d .claude && echo "layout ok"
```

Expected: `layout ok`.

- [ ] **Step 5: Show the final diff summary before commit**

Run: `git status --short`

Expected: renames for skills + commands, deletion of `.mcp.json`, modifications to `plugin.json`, `pyproject.toml`, `uv.lock` (if changed), `CHANGELOG.md`, `README.md`, `docs/claude-code-workflow.md`, `CONTRIBUTING.md`, and the new plan file under `docs/superpowers/plans/`.

---

### Task 12: Commit and open PR

**Files:**

- None (git operation).

- [ ] **Step 1: Stage all changes**

Run:

```bash
git add -A
```

- [ ] **Step 2: Commit with a descriptive message**

Run:

```bash
git commit -m "$(cat <<'EOF'
feat: wire repo as an installable Claude Code plugin

Move skills and commands from .claude/{skills,commands} to plugin-root
locations so plugin auto-discovery finds them. Declare the MCP server
inline in .claude-plugin/plugin.json (server key 'srv') using
${CLAUDE_PLUGIN_ROOT} for portable paths. Remove root .mcp.json — the
plugin manifest is now the single source of truth. Align pyproject.toml
to 0.3.0. Document the plugin install flow in README and rewrite
docs/claude-code-workflow.md around in-repo dev vs cross-project plugin
install.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: commit created on `feat/wire-plugin-components`.

- [ ] **Step 3: Push and open PR**

Run:

```bash
git push -u origin feat/wire-plugin-components
gh pr create --base main --title "feat: wire repo as an installable Claude Code plugin" --body "$(cat <<'EOF'
## Summary

- Skills moved from `.claude/skills/` to `skills/` and commands from `.claude/commands/` to `commands/` so Claude Code's plugin auto-discovery finds them.
- MCP server declared inline in `.claude-plugin/plugin.json` under `mcpServers.srv`, using `${CLAUDE_PLUGIN_ROOT}` for portable paths. Server key `srv` keeps tool names short (`mcp__plugin_fastmcp-builder_srv__<tool>`).
- Root `.mcp.json` deleted — would have collided with project-scoped config when this repo is opened in Claude Code.
- Versions aligned: `pyproject.toml` bumped to 0.3.0 to match `plugin.json`.
- README and `docs/claude-code-workflow.md` rewritten around in-repo dev vs cross-project plugin install.
- `CONTRIBUTING.md` release-verification section now covers both paths.

## Test plan

- [ ] `uv run pytest` passes
- [ ] `uv run fastmcp run src/fastmcp_builder/server.py:mcp` starts the server in-repo (smoke check)
- [ ] `/plugin install <this branch>` in a separate project registers the server (PR 2 — separate plan)
- [ ] `/mcp` shows `fastmcp-builder` with tools prefixed `mcp__plugin_fastmcp-builder_srv__` (PR 2)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Expected: PR URL printed on stdout.

---

## Self-Review

**1. Spec coverage check.** Decisions locked in upthread:

- ✅ Move skills/commands to plugin root → Tasks 2, 3
- ✅ Delete root `.mcp.json` → Task 4
- ✅ Inline `mcpServers` in `plugin.json` → Task 5
- ✅ `${CLAUDE_PLUGIN_ROOT}` for paths → Task 5
- ✅ Short server key (`srv`) → Task 5
- ✅ Align versions to 0.3.0 → Task 5 (manifest, already at 0.3.0), Task 6 (pyproject)
- ✅ CHANGELOG entry → Task 7
- ✅ README install section → Task 8
- ✅ Rewrite `docs/claude-code-workflow.md` → Task 9
- ✅ CONTRIBUTING release-verification → Task 10
- ✅ Verify tests still pass → Task 11
- ✅ PR with explanatory body → Task 12

**2. Placeholder scan.** No `TBD`, `TODO`, `fill in details`, or vague handwaving — each task names the exact file path, the exact replacement text, and the exact verification command.

**3. Type consistency.** The server key `srv` is used consistently across:

- `plugin.json` (Task 5)
- `README.md` example tool name (Task 8)
- `docs/claude-code-workflow.md` (Task 9)
- `CONTRIBUTING.md` (Task 10)
- PR body (Task 12)

The version `0.3.0` is used consistently across `plugin.json`, `pyproject.toml`, `CHANGELOG.md`.

**4. Out-of-scope items confirmed deferred:**

- Cross-project smoke test → separate plan (PR 2).
- Marketplace submission → out of scope.
- `allowed-tools` frontmatter on commands → revisit after smoke-test.
- Scaffold/init flow for new projects → separate plan (Goal A).
