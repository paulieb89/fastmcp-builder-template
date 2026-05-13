# Plugin Check Audit

Output of `audit_existing_checks_for_citations` (build-loop unit 2 of the
`mcp-compliance-checks` spec). Each row classifies one plugin check by its
spec source, so HIGH-severity findings are protocol-grounded and opinion-class
findings are clearly marked.

## ReviewFinding-emitting checks

These checks emit `ReviewFinding` objects with `spec_source` + `spec_section`
fields populated.

| Code | Module | Severity | Spec source | Spec section | Notes |
|---|---|---|---|---|---|
| `manifest.not_object` | `review.py` | HIGH | MCP | `server/initialize` | Server descriptor must be a JSON object. |
| `manifest.missing_name` | `review.py` | HIGH | MCP | `server/initialize` | Server must declare a name. |
| `manifest.missing_primitives` | `review.py` | HIGH | MCP | `server/capabilities` | Server must expose primitives. |
| `manifest.name_format` | `review.py` | MEDIUM | FastMCP | `servers/server.md` | snake_case convention; not MCP-mandatory. |
| `primitives.not_list` | `review.py` | HIGH | MCP | `server/capabilities` | Primitives are a list/array. |
| `primitive.not_object` | `review.py` | HIGH | MCP | `server/capabilities` | Each primitive is a JSON object. |
| `primitive.invalid_kind` | `review.py` | HIGH | MCP | `server/tools-resources-prompts` | Kind must be tool/resource/prompt. |
| `primitive.missing_name` | `review.py` | HIGH | MCP | `server/tools-resources-prompts` | Primitives have names. |
| `primitive.name_format` | `review.py` | MEDIUM | FastMCP | `servers/tools.md#naming` | snake_case for tool/prompt names; resources skip (already special-cased). |
| `primitive.duplicate_name` | `review.py` | HIGH | MCP | `server/capabilities` | Primitive names must be unique. |
| `primitive.description_too_short` | `review.py` | MEDIUM | MCP | `server/tools#description` | Descriptions guide model selection. |
| `tool.missing_parameters` | `review.py` | MEDIUM | MCP | `server/tools#inputSchema` | Tools declare an input schema. |
| `resource.missing_uri` | `review.py` | HIGH | MCP | `server/resources#uri` | Resources must declare a URI. |
| `prompt.missing_arguments` | `review.py` | LOW | opinion | — | Arguments are optional in MCP; lightweight hygiene. |
| `tool.silent_error_return` | `checks.py` | HIGH | FastMCP | `servers/tools.md#error-handling` | Raise, don't return error sentinels. |

## Warnings-list-based checks (not ReviewFinding-shaped)

These checks return their own report types (`ToolNameReport`,
`UriStabilityReport`, etc.) whose `warnings` are plain strings. They don't
have a finding-level citation slot today, but their citations are documented
here for traceability. A future refactor could migrate them to
`ReviewFinding`.

| Tool | Severity (default) | Spec source | Spec section | Notes |
|---|---|---|---|---|
| `check_tool_name_format` | MEDIUM | FastMCP | `servers/tools.md#naming` | snake_case, length, generic-name guards. |
| `check_prompt_name_format` | MEDIUM | FastMCP | `servers/prompts.md#naming` | snake_case for prompt names. |
| `check_uri_stability` | MEDIUM | MCP | `server/resources#uri-stability` | No volatile tokens, no query strings, no live HTTP URLs. |
| `check_tool_description_quality` | MEDIUM | MCP | `server/tools#description` | Description specificity for model-controlled use. |
| `check_error_response_design` | n/a | **opinion** | — | Categorisation helper, not a deterministic rule. Demoted from the design-review skill's automatic Layer 2 path (unit 3, `drop_or_demote_unsourced_checks`); still callable as a tool on demand. |

## Non-review tools (no findings, no citation needed)

These plugin tools produce design output rather than reviewing existing
code. They don't emit findings.

| Tool | Purpose |
|---|---|
| `classify_mcp_primitive` | Help decide tool / resource / prompt for a new capability. |
| `suggest_tool_contract` | Generate a starter tool contract. |
| `suggest_resource_contract` | Generate a starter resource contract. |
| `suggest_prompt_contract` | Generate a starter prompt contract. |
| `generate_minimal_server_plan` | Scaffold a small-server plan. |
| `extract_manifest_from_source` | Parse Python source → manifest dict. |

## Decisions captured

- **`check_error_response_design`** has no clean spec citation. Per Q2 in the
  spec's Open Questions, it stays callable on demand but is **removed from the
  fastmcp-design-review skill's automatic Layer 2 invocation** in unit 3.
- **`prompt.missing_arguments`** is opinion-class (LOW). Stays in the manifest
  reviewer for now but does not promote findings to HIGH/MEDIUM severity gates.
- **`primitive.name_format`** stays MEDIUM. Snake_case is a FastMCP/Python
  convention, not an MCP protocol mandate, but it materially affects how
  hosts surface the names so it earns MEDIUM rather than LOW.
