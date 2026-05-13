"""Source-level deterministic checks for FastMCP servers.

Each check walks the AST of a server module and reports findings.
Complements review_fastmcp_manifest (which checks the manifest shape)
by catching anti-patterns visible only in the source code itself.
"""

from __future__ import annotations

import ast
from typing import Any


def check_silent_error_returns(path: str) -> dict[str, Any]:
    """Scan a FastMCP server source for the silent-failure-conversion anti-pattern.

    Flags any @mcp.tool-decorated function that returns an error-shaped
    sentinel (a dict literal with an "error" key, or a string literal
    starting with "Error") instead of raising. Also follows one level of
    indirection: if a tool returns `_handle_error(e)` and that helper
    contains error sentinels, the tool's call site is flagged.

    Returns:
        {"passed": bool, "findings": list[{"tool": str, "line": int, "pattern": str}]}
    """
    with open(path) as f:
        tree = ast.parse(f.read())

    # Build a map of module-level function definitions so we can follow
    # one level of indirection when a tool returns helper(...).
    helpers: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    for top_level in tree.body:
        if isinstance(top_level, (ast.FunctionDef, ast.AsyncFunctionDef)):
            helpers[top_level.name] = top_level

    findings: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not _is_mcp_tool(node):
            continue
        for return_stmt in _walk_returns(node):
            if return_stmt.value is None:
                continue
            sentinel = _classify_error_sentinel(return_stmt.value)
            if sentinel is None:
                sentinel = _classify_indirect_error(return_stmt.value, helpers)
            if sentinel is not None:
                findings.append({
                    "tool": node.name,
                    "line": return_stmt.lineno,
                    "pattern": sentinel,
                })

    return {"passed": not findings, "findings": findings}


def _is_mcp_tool(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for decorator in node.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if isinstance(target, ast.Attribute) and target.attr == "tool":
            return True
    return False


def _walk_returns(node: ast.AST) -> list[ast.Return]:
    """All Return statements inside `node`, including nested in if/for/with/try."""
    return [child for child in ast.walk(node) if isinstance(child, ast.Return)]


def _classify_indirect_error(
    value: ast.expr,
    helpers: dict[str, ast.FunctionDef | ast.AsyncFunctionDef],
) -> str | None:
    """If `value` is a call to a same-module helper that itself returns
    error-shaped sentinels, return a label naming the indirection."""
    if not isinstance(value, ast.Call):
        return None
    callee_name: str | None = None
    if isinstance(value.func, ast.Name):
        callee_name = value.func.id
    elif isinstance(value.func, ast.Attribute):
        callee_name = value.func.attr
    if callee_name is None or callee_name not in helpers:
        return None
    helper = helpers[callee_name]
    for return_stmt in _walk_returns(helper):
        if return_stmt.value is None:
            continue
        if _classify_error_sentinel(return_stmt.value) is not None:
            return f'via helper "{callee_name}" that returns error sentinels'
    return None


def _classify_error_sentinel(value: ast.expr) -> str | None:
    """Return a short label of the pattern if `value` looks like an error sentinel."""
    # Pattern 1: dict literal with an "error" key, e.g. {"error": "..."}.
    if isinstance(value, ast.Dict):
        for key in value.keys:
            if isinstance(key, ast.Constant) and key.value == "error":
                return 'dict with "error" key'

    # Pattern 2: string literal starting with "Error" or "error:".
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        stripped = value.value.lstrip()
        if stripped.lower().startswith("error"):
            return 'string literal starting with "Error"'

    # Pattern 3: f-string whose first segment starts with "Error".
    if isinstance(value, ast.JoinedStr) and value.values:
        first = value.values[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            if first.value.lstrip().lower().startswith("error"):
                return 'f-string starting with "Error"'

    return None
