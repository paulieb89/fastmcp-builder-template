---
name: fastmcp-build-loop
description: Build FastMCP tools, resources, and prompts one spec section at a time with verify-and-self-correct after each unit.
---

# FastMCP Build Loop

Spec-driven, iterative build skill for this template. One section at a time — implement, verify with `uv run pytest`, self-review, commit, then loop.

---

## Reference docs (read before implementing)

| Building...          | Read first                        |
|----------------------|-----------------------------------|
| Any primitive        | `docs/mcp-primitives.md`          |
| Tool                 | `docs/tool-design.md`             |
| Resource             | `docs/resource-design.md`         |
| Prompt               | `docs/prompt-design.md`           |
| Safety boundaries    | `docs/safety-boundaries.md`       |
| Code examples        | `examples/tool_example.py` etc.   |

Read the relevant doc before writing any code. Non-negotiable.

---

## Step 0 — Spec check

`${1}` is the spec file path. If not provided or missing, interview the user:

1. "What capability are you adding?" — becomes the section name
2. "What inputs does it take and what does it return?" — fills the schema
3. "Any constraints or edge cases?" — fills gotchas

Write one `## CapabilityName` section per capability. Show it to the user and wait for approval before proceeding.

Confirm the spec has at least one section:

```bash
grep -c "^## " ${1}
```

Check current branch — if on `main`, create a feature branch before touching any code:

```bash
git branch --show-current
git checkout -b feat/<spec-name-slug>
```

---

## Step 1 — Select next unit

```bash
grep -n "^## " ${1} | grep -v "\[done\]\|\[skip\]" | head -1
```

If all sections are marked `[done]` or `[skip]`: print a summary of what was built and stop.

---

## Step 2 — Load context

Before writing any code:

1. Read `CLAUDE.md` — operating rules and constraints
2. Read the relevant doc from the reference table above
3. Read existing files in `src/fastmcp_builder/` related to this unit

---

## Step 3 — Implement

Follow the spec section exactly.

Rules:
- Logic in `src/fastmcp_builder/review.py` (or appropriate module)
- Return model in `src/fastmcp_builder/models.py`
- Tool registered in `src/fastmcp_builder/server.py` via `@mcp.tool`
- Use Python type hints — the SDK generates JSON schema automatically
- Never write JSON schemas by hand
- No network calls, subprocess, auth, or external I/O
- Do not add features not in the spec — log extras as follow-ups

---

## Step 4 — Verify

```bash
uv run pytest
```

Fix errors. Re-run until green. If the same error recurs after two attempts: document in a `progress.md` note and move to Step 5.

---

## Step 5 — Self-review

Re-read what you wrote against the spec section:

- [ ] Name matches spec exactly
- [ ] All inputs present with correct types
- [ ] Output shape matches spec
- [ ] Constraints and edge cases from spec are handled
- [ ] No imports that don't exist
- [ ] No TODO placeholders
- [ ] Test added or updated

If any item fails: fix and re-run Step 4.

---

## Step 6 — Commit

Stage specific files only — never `git add .`:

```bash
git add src/fastmcp_builder/models.py src/fastmcp_builder/review.py src/fastmcp_builder/server.py tests/test_<unit>.py
git commit -m "feat: implement <unit-name>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Step 7 — Mark done and loop

Mark the section in `${1}`:

```
## CapabilityName [done]
```

Return to Step 1.

---

## Hard rules

- Never push — Paul does that
- Never add units not in the spec
- Never `git add .`
- Never skip the pytest verify step
- Never merge anything
