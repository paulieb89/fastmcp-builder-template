"""Source-level deterministic checks for FastMCP servers.

Each check walks the AST of a server module and reports findings as
ReviewFinding objects (same shape as review_fastmcp_manifest_data so
the design-review skill can merge findings uniformly by severity).
"""

from __future__ import annotations

import ast
import re

from .extract import iter_mcp_decorated_functions, load_ast
from .models import CheckReport, ReviewFinding, Severity, SilentErrorReport


PATTERN_ERROR_DICT = 'dict with "error" key'
PATTERN_ERROR_STRING = 'string literal starting with "Error"'
PATTERN_ERROR_FSTRING = 'f-string starting with "Error"'
_VIA_HELPER_TEMPLATE = 'via helper "{helper}" that returns error sentinels'


def check_silent_error_returns(path: str) -> SilentErrorReport:
    """Scan a FastMCP server source for the silent-failure-conversion anti-pattern.

    Flags any @mcp.tool-decorated function that returns an error-shaped
    sentinel (a dict with an "error" key, or a string/f-string starting
    with "Error") instead of raising. Follows one level of indirection:
    a tool that returns helper(...) is flagged when the helper itself
    returns error sentinels.
    """
    tree = load_ast(path)

    helpers = _collect_helpers(tree)
    helper_label = {name: _first_error_sentinel(fn) for name, fn in helpers.items()}

    findings: list[ReviewFinding] = []
    for node, kind, _decorator in iter_mcp_decorated_functions(tree):
        if kind != "tool":
            continue
        for return_stmt in _walk_returns(node):
            if return_stmt.value is None:
                continue
            label = _classify_error_sentinel(return_stmt.value) or _classify_indirect_error(
                return_stmt.value, helper_label
            )
            if label is None:
                continue
            findings.append(
                ReviewFinding(
                    severity=Severity.HIGH,
                    code="tool.silent_error_return",
                    message=(
                        f"Tool '{node.name}' returns error sentinel ({label}) "
                        f"at line {return_stmt.lineno} instead of raising."
                    ),
                    path=f"$.primitives.{node.name}",
                    spec_source="FastMCP",
                    spec_section="servers/tools.md#error-handling",
                )
            )

    return SilentErrorReport(passed=not findings, findings=findings)


def _collect_helpers(tree: ast.Module) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    """Module-level function definitions, by name. Includes @mcp.tool functions
    (so a tool can recurse to another tool's body) but those rarely matter."""
    return {
        top.name: top
        for top in tree.body
        if isinstance(top, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _first_error_sentinel(node: ast.AST) -> str | None:
    """The first error-sentinel return inside `node`, or None."""
    for return_stmt in _walk_returns(node):
        if return_stmt.value is None:
            continue
        label = _classify_error_sentinel(return_stmt.value)
        if label is not None:
            return label
    return None


def _walk_returns(node: ast.AST) -> list[ast.Return]:
    return [child for child in ast.walk(node) if isinstance(child, ast.Return)]


def _classify_error_sentinel(value: ast.expr) -> str | None:
    """Return a short label of the pattern if `value` looks like an error sentinel."""
    if isinstance(value, ast.Dict):
        for key in value.keys:
            if isinstance(key, ast.Constant) and key.value == "error":
                return PATTERN_ERROR_DICT

    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        if _looks_like_error_prefix(value.value):
            return PATTERN_ERROR_STRING

    if isinstance(value, ast.JoinedStr) and value.values:
        first = value.values[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            if _looks_like_error_prefix(first.value):
                return PATTERN_ERROR_FSTRING

    return None


def _classify_indirect_error(
    value: ast.expr,
    helper_label: dict[str, str | None],
) -> str | None:
    """If `value` is a call to a known error-returning helper, name the helper."""
    if not isinstance(value, ast.Call):
        return None
    callee = None
    if isinstance(value.func, ast.Name):
        callee = value.func.id
    elif isinstance(value.func, ast.Attribute):
        callee = value.func.attr
    if callee and helper_label.get(callee):
        return _VIA_HELPER_TEMPLATE.format(helper=callee)
    return None


def _looks_like_error_prefix(text: str) -> bool:
    return text.lstrip().lower().startswith("error")


_STANDARD_TOOL_HINTS = ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint")


def check_tool_annotations_declared(path: str) -> CheckReport:
    """Scan source for @mcp.tool decorators that don't declare the four
    standard ToolAnnotations hints.

    Spec source: MCP — `ToolAnnotations` field on Tool. Severity MEDIUM
    (MCP-recommended, not MUST). Hosts use these hints to render the tool,
    confirm destructive ones, etc.

    Flags two cases:
      - No `annotations=` kwarg at all.
      - `annotations={...}` is a dict literal but missing one or more of the
        four standard hints. (A non-literal value — e.g. a named constant —
        is given the benefit of the doubt since we can't read it statically.)
    """
    tree = load_ast(path)

    findings: list[ReviewFinding] = []
    for node, kind, decorator in iter_mcp_decorated_functions(tree):
        if kind != "tool":
            continue

        annotations_kw = None
        if isinstance(decorator, ast.Call):
            for kw in decorator.keywords:
                if kw.arg == "annotations":
                    annotations_kw = kw
                    break

        if annotations_kw is None:
            findings.append(
                ReviewFinding(
                    severity=Severity.MEDIUM,
                    code="tool.missing_annotations",
                    message=(
                        f"Tool '{node.name}' has no annotations= kwarg. "
                        f"Declare ToolAnnotations hints (readOnlyHint, "
                        f"destructiveHint, idempotentHint, openWorldHint) so "
                        f"hosts can render and gate the tool correctly."
                    ),
                    path=f"$.primitives.{node.name}",
                    spec_source="MCP",
                    spec_section="server/tools#annotations",
                )
            )
            continue

        # If the value isn't a dict literal, we can't analyse it — pass.
        if not isinstance(annotations_kw.value, ast.Dict):
            continue

        declared_hints = {
            key.value
            for key in annotations_kw.value.keys
            if isinstance(key, ast.Constant) and isinstance(key.value, str)
        }
        missing = [hint for hint in _STANDARD_TOOL_HINTS if hint not in declared_hints]
        if missing:
            findings.append(
                ReviewFinding(
                    severity=Severity.MEDIUM,
                    code="tool.missing_annotations",
                    message=(
                        f"Tool '{node.name}' annotations missing standard hints: "
                        f"{', '.join(missing)}."
                    ),
                    path=f"$.primitives.{node.name}",
                    spec_source="MCP",
                    spec_section="server/tools#annotations",
                )
            )

    return CheckReport(passed=not findings, findings=findings)


def check_resource_mime_type_declared(path: str) -> CheckReport:
    """Scan source for @mcp.resource decorators that don't declare a mime_type.

    Spec source: FastMCP framework — `servers/resources.md`. The `mime_type=`
    kwarg lets the client display the resource correctly without inferring
    from the return type. Severity MEDIUM (FastMCP-recommended, not
    MCP-mandatory).
    """
    tree = load_ast(path)

    findings: list[ReviewFinding] = []
    for node, kind, decorator in iter_mcp_decorated_functions(tree):
        if kind != "resource":
            continue
        has_mime = False
        if isinstance(decorator, ast.Call):
            has_mime = any(kw.arg == "mime_type" for kw in decorator.keywords)
        if not has_mime:
            findings.append(
                ReviewFinding(
                    severity=Severity.MEDIUM,
                    code="resource.missing_mime_type",
                    message=(
                        f"Resource '{node.name}' has no mime_type= kwarg on its "
                        f"@mcp.resource decorator. FastMCP will infer one from "
                        f"the return type, which is brittle for non-string content."
                    ),
                    path=f"$.primitives.{node.name}",
                    spec_source="FastMCP",
                    spec_section="servers/resources.md#mime_type",
                )
            )

    return CheckReport(passed=not findings, findings=findings)


def check_prompt_argument_descriptions(path: str) -> CheckReport:
    """Scan source for @mcp.prompt arguments that lack descriptions.

    Spec source: MCP — `PromptArgument.description` field SHOULD be present.
    A description can come from either `Annotated[X, Field(description="...")]`
    on the parameter, or a docstring `Args:` block (Google/NumPy style) naming
    the parameter. Severity MEDIUM (MCP SHOULD, not MUST).
    """
    tree = load_ast(path)

    findings: list[ReviewFinding] = []
    for node, kind, _decorator in iter_mcp_decorated_functions(tree):
        if kind != "prompt":
            continue
        docstring = ast.get_docstring(node) or ""
        for arg in node.args.args:
            if arg.arg in {"self", "ctx", "context"}:
                continue
            if _arg_has_description(arg, docstring):
                continue
            findings.append(
                ReviewFinding(
                    severity=Severity.MEDIUM,
                    code="prompt.argument_missing_description",
                    message=(
                        f"Prompt '{node.name}' argument '{arg.arg}' has no description. "
                        f"Add one via `Annotated[X, Field(description=...)]` or a "
                        f"docstring `Args:` block."
                    ),
                    path=f"$.primitives.{node.name}.arguments.{arg.arg}",
                    spec_source="MCP",
                    spec_section="server/prompts#argument-description",
                )
            )

    return CheckReport(passed=not findings, findings=findings)


# Compiled outside the check so we don't recompile per call.
_ARGS_HEADER = re.compile(r"^\s*(Args|Arguments|Parameters):\s*$", re.MULTILINE)


def _arg_has_description(arg: ast.arg, docstring: str) -> bool:
    """True if `arg.arg` looks documented via an Annotated/Field on the annotation
    or named in the docstring's Args section."""
    if _annotation_has_field_description(arg.annotation):
        return True
    return _docstring_documents_arg(docstring, arg.arg)


def _annotation_has_field_description(annotation: ast.expr | None) -> bool:
    """Recursively look for Annotated[X, Field(description=...)] on an annotation."""
    if annotation is None:
        return False
    if not isinstance(annotation, ast.Subscript):
        return False
    if not (isinstance(annotation.value, ast.Name) and annotation.value.id == "Annotated"):
        return False
    slice_node = annotation.slice
    if not isinstance(slice_node, ast.Tuple):
        return False
    for elt in slice_node.elts[1:]:
        if not isinstance(elt, ast.Call):
            continue
        callee = elt.func
        callee_name = (
            callee.id if isinstance(callee, ast.Name)
            else callee.attr if isinstance(callee, ast.Attribute)
            else None
        )
        if callee_name != "Field":
            continue
        for kw in elt.keywords:
            if kw.arg == "description" and isinstance(kw.value, ast.Constant):
                if isinstance(kw.value.value, str) and kw.value.value.strip():
                    return True
    return False


def _docstring_documents_arg(docstring: str, arg_name: str) -> bool:
    """Look for an `Args:` (or Arguments / Parameters) block that mentions arg_name.

    Matches Google-style (`name: description` / `name (type): description`) and
    bullet-style (`- name: description`). Once an args header is found, the rule
    is permissive — any subsequent line containing the arg name followed by a
    colon or open-paren counts as documented.
    """
    if not docstring:
        return False
    header_match = _ARGS_HEADER.search(docstring)
    if not header_match:
        return False
    body = docstring[header_match.end():]
    # Pattern: arg_name optionally followed by parens, then colon.
    pattern = rf"(?m)^\s*(?:[-*]\s*)?{re.escape(arg_name)}\s*(?:\([^)]*\))?\s*:"
    return bool(re.search(pattern, body))
