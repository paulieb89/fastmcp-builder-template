# Plugin Audit Report

**Date:** 2026-05-10  
**Branch:** feat/test-cross-project-mode  
**Scope:** Review against plugin-dev standards: plugin-structure, plugin-settings, create-plugin workflow, skill quality

---

## 1. Current Structure

```
fastmcp-builder-template/
├── CLAUDE.md
├── README.md
├── pyproject.toml
├── fastmcp.json                       # FastMCP source/transport declaration
├── skills-lock.json                   # External skill lock (plugin-creator from openai/skills)
├── .mcp.json                          # MCP server registration
│
├── .claude/
│   ├── settings.json                  # enabledPlugins (hookify@claude-plugins-official)
│   ├── settings.local.json            # enabledMcpjsonServers
│   ├── commands/                      # LEGACY — 3 slash command files
│   │   ├── review-manifest.md
│   │   ├── design-fastmcp.md
│   │   └── add-tool.md
│   └── skills/                        # NON-COMPLIANT location — should be skills/ at root
│       ├── mcp-primitive-classification/SKILL.md
│       ├── fastmcp-design-review/SKILL.md
│       ├── fastmcp-scaffold-author/SKILL.md
│       └── fastmcp-build-loop/SKILL.md
│
├── .agents/                           # Codex convention — NOT Claude Code standard
│   └── skills/plugin-creator/         # Wrong project scope (Codex plugin scaffolder)
│
└── src/fastmcp_builder/               # MCP server (11 tools, 4 resources, 4 prompts)
    ├── server.py
    ├── docs.py
    ├── models.py
    ├── review.py
    └── scaffold.py
```

---

## 2. Gap Analysis

### MISSING

| Item | Why it matters |
|---|---|
| `.claude-plugin/plugin.json` | Required manifest — without it this is not a Claude Code plugin, cannot be installed or discovered |
| Top-level `skills/` directory | Standard location for plugin skills; `.claude/skills/` is editor config, not plugin structure |
| `task-observer` skill | Referenced unconditionally in `CLAUDE.md` — dead reference, silently fails every session |
| `agents/` directory | No Claude Code agent definitions exist |
| `hooks/hooks.json` | No hooks; cannot automate session start, tool events, etc. |
| `.claude/fastmcp-builder.local.md` | Per-project settings file entirely absent |
| `.gitignore` entry for `*.local.md` | User-local config would be accidentally committed |

### NON-COMPLIANT

| Item | Problem | Fix |
|---|---|---|
| Skills location | `.claude/skills/` instead of `skills/` at plugin root | Move all 4 skill dirs to `skills/` |
| Commands location | `.claude/commands/` (wrong dir, legacy format) | Migrate to `skills/`, delete `commands/` |
| `.mcp.json` env paths | Uses `${PWD}` — shell-dependent, requires launch from repo root | Replace with `${CLAUDE_PLUGIN_ROOT}/docs` and `${CLAUDE_PLUGIN_ROOT}/examples` |
| `fastmcp-build-loop` paths | References docs as filesystem paths, not MCP resource URIs | Use `fastmcp-builder://docs/...` URIs |
| `fastmcp-build-loop` args | `${1}` syntax does not resolve in Claude Code skills | Use `argument-hint` frontmatter + prose placeholder |
| `plugin-creator` skill | Wrong scope (Codex scaffolder), contains `agents/openai.yaml` violating local-first policy | Remove entirely |

### CORRECT

| Item | Status |
|---|---|
| `.mcp.json` present at root | ✅ |
| STDIO server, no network calls | ✅ |
| Skill subdirectory + SKILL.md structure | ✅ |
| Kebab-case skill naming | ✅ |
| `name` + `description` frontmatter on all skills | ✅ |
| Python package structure (`src/` layout, uv) | ✅ |

---

## 3. Skill Quality Review

### mcp-primitive-classification — NEEDS WORK

- 21 lines, no supporting files
- Description lacks natural trigger phrases ("should this be a tool or resource?")
- Voice: mixes user-narration and Claude instructions
- Never instructs Claude to call the `classify_mcp_primitive` MCP tool

### fastmcp-design-review — NEEDS WORK

- 20 lines, no supporting files
- Checklist is accurate but Claude is left to do manual review instead of calling `review_fastmcp_manifest`, `check_tool_description_quality`, `check_error_response_design` — tools that exist for this exact purpose
- Pattern resources (`fastmcp-builder://patterns/...`) never mentioned

### fastmcp-scaffold-author — NEEDS WORK

- 18 lines, no supporting files
- Overlaps with `fastmcp-build-loop` — no disambiguation guidance in either description
- Never references `generate_minimal_server_plan`, `suggest_tool_contract`, `suggest_resource_contract` — the server tools for scaffold planning

### fastmcp-build-loop — GOOD (best of the four)

- 145 lines, references external docs, imperative voice throughout
- `${1}` variable syntax in bash blocks does not resolve in Claude Code — Claude sees the literal string
- Missing `argument-hint` frontmatter despite clearly accepting a spec file argument
- Doc references use filesystem paths instead of MCP resource URIs
- Hardcodes "Claude Sonnet 4.6" in commit message template (will go stale)

### plugin-creator — POOR / Remove

- Wrong project scope: Codex plugin scaffolder, not FastMCP
- Contains `agents/openai.yaml` which violates local-first, no-hosted-services policy
- Should be removed from this repository

---

## 4. Plugin Settings Assessment

### Current mechanism

`.mcp.json` injects `FASTMCP_BUILDER_DOCS_DIR=${PWD}/docs` and `FASTMCP_BUILDER_EXAMPLES_DIR=${PWD}/examples` as env-vars at server launch. These are consumed at module import time in `docs.py`.

### What's missing

No `.claude/fastmcp-builder.local.md` file exists. No `.gitignore` coverage for `*.local.md`.

### Recommended settings schema

```markdown
---
enabled: true

# in-repo | cross-project
mode: in-repo

# Override doc/example dirs (leave blank to use defaults)
docs_dir: ""
examples_dir: ""

# Cross-project mode only
advisory_project: ""
advisory_project_goal: ""

# Suppress skills not relevant to current mode
active_skills:
  - mcp-primitive-classification
  - fastmcp-design-review
  - fastmcp-scaffold-author
  - fastmcp-build-loop

auto_load_primitives_doc: false
---

<!-- Per-project context for Claude -->
```

`docs_dir` / `examples_dir` should be read by a hook and injected as env-vars, removing the need to edit `.mcp.json` per machine.

---

## 5. Create-Plugin Workflow Phase Assessment

| Phase | Status | Notes |
|---|---|---|
| 1. Discovery | PARTIAL | Plugin purpose documented in README/CLAUDE.md, but never framed as a Claude Code plugin |
| 2. Component Planning | PARTIAL | Components exist but grew incrementally — no planning artifact |
| 3. Detailed Design | PARTIAL | Tool/resource/prompt contracts typed via Pydantic; no plugin-level architecture doc |
| 4. Plugin Structure | PARTIAL | Dirs exist; missing `.claude-plugin/plugin.json`, hooks, settings file, `.gitignore` entry |
| 5. Implementation | PARTIAL | Skills written; no hooks, no settings mechanism |
| 6. Validation | MISSING | No plugin-validator run, no skill-reviewer run, no validation report |
| 7. Testing | PARTIAL | pytest suite passing; no skill behavioral tests; `test_cross_project_mode.py` untracked |

---

## 6. MCP Server Coverage Gaps

Tools/resources/prompts in `server.py` that no skill instructs Claude to use:

| Server capability | Missing skill coverage |
|---|---|
| `check_tool_description_quality` | No skill calls this during authoring |
| `check_tool_name_format` / `check_prompt_name_format` | Not mentioned anywhere |
| `check_uri_stability` | Not mentioned anywhere |
| `check_error_response_design` | Not mentioned anywhere |
| `suggest_tool_contract` / `suggest_resource_contract` / `suggest_prompt_contract` | scaffold/build skills never call these |
| `design_fastmcp_server` prompt | No skill references it as a starting point |
| `prepare_claude_code_session` prompt | No skill references session preparation |
| `fastmcp-builder://docs/{slug}` resources | Only `fastmcp-build-loop` references docs, as filesystem paths not MCP URIs |
| `fastmcp-builder://examples/{name}` resources | Never referenced in any skill |

---

## 7. Priority Fixes (ordered)

1. **Create `.claude-plugin/plugin.json`** — the blocker for plugin identity
2. **Move skills from `.claude/skills/` → `skills/`** at plugin root; migrate `commands/` into skills; update `CLAUDE.md` table
3. **Fix or remove `task-observer` reference in `CLAUDE.md`** — currently a dead reference
4. **Remove `plugin-creator` skill** — wrong scope, violates local-first policy
5. **Replace `${PWD}` with `${CLAUDE_PLUGIN_ROOT}` in `.mcp.json`** — portability fix
6. **Add `argument-hint` to `fastmcp-build-loop`; replace `${1}` with prose placeholder** — runtime correctness
7. **Update `fastmcp-design-review` to call MCP review tools** — main value-add currently absent
8. **Create `.claude/fastmcp-builder.local.md` template + add `*.local.md` to `.gitignore`** — settings pattern compliance
9. **Add trigger disambiguation between `fastmcp-scaffold-author` and `fastmcp-build-loop`** — reduces routing confusion
10. **Commit `tests/test_cross_project_mode.py`** — currently untracked
