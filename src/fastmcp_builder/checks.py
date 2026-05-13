"""Source-level deterministic checks for FastMCP servers.

Each check walks the AST of a server module and reports findings as
ReviewFinding objects (same shape as review_fastmcp_manifest_data so
the design-review skill can merge findings uniformly by severity).
"""

from __future__ import annotations

import ast

from .extract import iter_mcp_decorated_functions, load_ast
from .models import ReviewFinding, Severity, SilentErrorReport


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
