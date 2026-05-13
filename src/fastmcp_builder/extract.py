"""Parse Python source files for FastMCP primitives.

Walks a FastMCP server's source code via the `ast` module and produces a
manifest dict in the shape expected by `review_fastmcp_manifest_data`.
Deterministic, no execution of the source.
"""

from __future__ import annotations

import ast
from typing import Any

_TYPE_HINT_MAP = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "list": "array",
    "dict": "object",
}


def extract_manifest_from_source(path: str) -> dict[str, Any]:
    """Extract a FastMCP manifest from a Python source file.

    Returns a dict shaped like:
        {"name": "<server slug>", "primitives": [<tool|resource|prompt entries>]}

    Server name defaults to "unknown" when no FastMCP(...) constructor is
    detected. Primitives is the empty list when no @mcp.tool / @mcp.resource /
    @mcp.prompt decorators are present.
    """
    with open(path) as f:
        tree = ast.parse(f.read())

    primitives: list[dict[str, Any]] = []
    server_name = "unknown"
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            detected = _server_name_from_FastMCP_call(node)
            if detected:
                server_name = detected
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                kind = _classify_decorator(decorator)
                if kind == "tool":
                    primitives.append(_extract_tool(node))
                    break
                if kind == "resource":
                    primitives.append(_extract_resource(node, decorator))
                    break
                if kind == "prompt":
                    primitives.append(_extract_prompt(node))
                    break

    return {"name": server_name, "primitives": primitives}


def _server_name_from_FastMCP_call(call: ast.Call) -> str | None:
    """Return the snake_case slug of a FastMCP(...) call if matched, else None.

    Accepts both call shapes used by real fleet servers:
        FastMCP("My Server")          # positional
        FastMCP(name="My Server")     # keyword
        FastMCP("My Server", instructions=...)  # mixed
    """
    target = call.func
    is_fastmcp = (
        (isinstance(target, ast.Name) and target.id == "FastMCP")
        or (isinstance(target, ast.Attribute) and target.attr == "FastMCP")
    )
    if not is_fastmcp:
        return None

    raw: str | None = None
    if call.args and isinstance(call.args[0], ast.Constant) and isinstance(call.args[0].value, str):
        raw = call.args[0].value
    else:
        for kw in call.keywords:
            if kw.arg == "name" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                raw = kw.value.value
                break
    if raw is None:
        return None

    # Lowercase, replace non-alphanumeric runs with underscores, strip edges.
    slug = "".join(c.lower() if c.isalnum() else "_" for c in raw).strip("_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug or None


def _classify_decorator(decorator: ast.expr) -> str | None:
    """Return 'tool' / 'resource' / 'prompt' if the decorator is a FastMCP one."""
    # @mcp.tool, @mcp.resource, @mcp.prompt — Attribute nodes
    # @mcp.tool(...), @mcp.resource("uri", ...), @mcp.prompt(...) — Call nodes
    target = decorator.func if isinstance(decorator, ast.Call) else decorator
    if isinstance(target, ast.Attribute) and target.attr in {"tool", "resource", "prompt"}:
        return target.attr
    return None


def _extract_tool(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any]:
    return {
        "kind": "tool",
        "name": node.name,
        "description": _docstring(node),
        "input_schema": _input_schema(node),
    }


def _extract_prompt(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any]:
    """Prompts mirror tools but use `arguments` (list of {name, type}) instead of input_schema."""
    arguments = []
    for arg in node.args.args:
        if arg.arg in {"self", "ctx", "context"}:
            continue
        arguments.append({"name": arg.arg, "type": _annotation_type(arg.annotation)})
    return {
        "kind": "prompt",
        "name": node.name,
        "description": _docstring(node),
        "arguments": arguments,
    }


def _extract_resource(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    decorator: ast.expr,
) -> dict[str, Any]:
    """@mcp.resource("uri", name=..., description=...) — URI is the first positional arg."""
    uri_template = ""
    name = node.name
    description = _docstring(node)

    if isinstance(decorator, ast.Call):
        if decorator.args and isinstance(decorator.args[0], ast.Constant):
            uri_template = decorator.args[0].value
        for kw in decorator.keywords:
            if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                name = kw.value.value
            elif kw.arg == "description" and isinstance(kw.value, ast.Constant):
                description = kw.value.value

    return {
        "kind": "resource",
        "name": name,
        "description": description,
        "uri_template": uri_template,
    }


def _docstring(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    return ast.get_docstring(node) or ""


def _input_schema(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any]:
    """Build a JSON-Schema-shaped input schema from the function signature.

    Skips `self`, `ctx`, and `context` (FastMCP injects these). Required = the
    parameters without defaults.
    """
    args = node.args.args
    defaults = node.args.defaults
    num_required = len(args) - len(defaults)

    properties: dict[str, Any] = {}
    required: list[str] = []
    for index, arg in enumerate(args):
        if arg.arg in {"self", "ctx", "context"}:
            continue
        properties[arg.arg] = {"type": _annotation_type(arg.annotation)}
        if index < num_required:
            required.append(arg.arg)

    schema: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema


def _annotation_type(annotation: ast.expr | None) -> str:
    """Map a Python type annotation to a JSON Schema type string.

    Returns "string" for anything not in the basic primitive map (good-enough
    placeholder — the review tool checks shape, not type fidelity).
    """
    if annotation is None:
        return "string"
    if isinstance(annotation, ast.Name):
        return _TYPE_HINT_MAP.get(annotation.id, "string")
    if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name):
        return _TYPE_HINT_MAP.get(annotation.value.id, "string")
    return "string"
