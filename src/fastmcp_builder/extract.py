"""Parse Python source files for FastMCP primitives.

Walks a FastMCP server's source code via the `ast` module and produces a
manifest dict in the shape expected by `review_fastmcp_manifest_data`.
Deterministic, no execution of the source.

Also exports shared AST helpers consumed by `checks.py`:
    load_ast(path)                  open + parse a source file
    classify_decorator(decorator)   'tool'/'resource'/'prompt' or None
    iter_mcp_decorated_functions    yields (node, kind, decorator) for each
"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from typing import Any, TypeGuard

_TYPE_HINT_MAP = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "list": "array",
    "dict": "object",
}


# ---------------------------------------------------------------------------
# Shared AST helpers (used by extract.py itself and by checks.py)
# ---------------------------------------------------------------------------


def load_ast(path: str) -> ast.Module:
    """Open and parse a Python source file. Always UTF-8."""
    with open(path, encoding="utf-8") as f:
        return ast.parse(f.read())


def classify_decorator(decorator: ast.expr) -> str | None:
    """Return 'tool' / 'resource' / 'prompt' if the decorator is a FastMCP one.

    Handles both `@mcp.tool` (Attribute) and `@mcp.tool(...)` (Call wrapping
    Attribute) forms.
    """
    target = decorator.func if isinstance(decorator, ast.Call) else decorator
    if isinstance(target, ast.Attribute) and target.attr in {"tool", "resource", "prompt"}:
        return target.attr
    return None


def iter_mcp_decorated_functions(
    tree: ast.Module,
) -> Iterator[tuple[ast.FunctionDef | ast.AsyncFunctionDef, str, ast.expr]]:
    """Yield (function_node, primitive_kind, decorator_node) for each module-level
    function decorated with @mcp.tool / @mcp.resource / @mcp.prompt.

    Module-level only — FastMCP primitives can't live inside nested scopes.
    """
    for top_level in tree.body:
        if not isinstance(top_level, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in top_level.decorator_list:
            kind = classify_decorator(decorator)
            if kind is not None:
                yield top_level, kind, decorator
                break


# ---------------------------------------------------------------------------
# Manifest extraction
# ---------------------------------------------------------------------------


def extract_manifest_from_source(path: str) -> dict[str, Any]:
    """Extract a FastMCP manifest from a Python source file.

    Returns a dict shaped like:
        {"name": "<server slug>", "primitives": [<tool|resource|prompt entries>]}

    Server name defaults to "unknown" when no FastMCP(...) constructor is
    detected. Primitives is the empty list when no @mcp.tool / @mcp.resource /
    @mcp.prompt decorators are present.
    """
    tree = load_ast(path)

    server_name = _detect_server_name(tree)
    module_classes = _collect_module_classes(tree)

    primitives: list[dict[str, Any]] = []
    for node, kind, decorator in iter_mcp_decorated_functions(tree):
        if kind == "tool":
            primitives.append(_extract_tool(node, module_classes))
        elif kind == "resource":
            primitives.append(_extract_resource(node, decorator))
        elif kind == "prompt":
            primitives.append(_extract_prompt(node))

    return {"name": server_name, "primitives": primitives}


def _collect_module_classes(tree: ast.Module) -> dict[str, ast.ClassDef]:
    """All top-level class definitions in the module, keyed by name."""
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    }


def _detect_server_name(tree: ast.Module) -> str:
    """Find the first FastMCP(...) call anywhere in the tree, return its slug."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            detected = _server_name_from_FastMCP_call(node)
            if detected:
                return detected
    return "unknown"


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

    slug = "".join(c.lower() if c.isalnum() else "_" for c in raw).strip("_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug or None


def _extract_tool(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    module_classes: dict[str, ast.ClassDef] | None = None,
) -> dict[str, Any]:
    return {
        "kind": "tool",
        "name": node.name,
        "description": _docstring(node),
        "input_schema": _input_schema(node, module_classes),
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


def _input_schema(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    module_classes: dict[str, ast.ClassDef] | None = None,
) -> dict[str, Any]:
    """Build a JSON-Schema-shaped input schema from the function signature.

    Skips `self`, `ctx`, and `context` (FastMCP injects these). Required = the
    parameters without defaults. If a parameter's annotation refers to a
    Pydantic BaseModel defined in the same module, the model is expanded
    inline so the model's fields are visible to the LLM.
    """
    args = node.args.args
    defaults = node.args.defaults
    num_required = len(args) - len(defaults)

    properties: dict[str, Any] = {}
    required: list[str] = []
    for index, arg in enumerate(args):
        if arg.arg in {"self", "ctx", "context"}:
            continue
        properties[arg.arg] = _property_schema(arg.annotation, module_classes)
        if index < num_required:
            required.append(arg.arg)

    schema: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema


def _annotation_type(annotation: ast.expr | None) -> str:
    """Back-compat string-only view of `_property_schema` for prompt args."""
    return _property_schema(annotation).get("type", "string")


def _property_schema(
    annotation: ast.expr | None,
    module_classes: dict[str, ast.ClassDef] | None = None,
) -> dict[str, Any]:
    """Map a Python type annotation to a JSON Schema property dict.

    Returns `{"type": <json_type>, ...}` with optional enrichments:
        - `enum`         from `Literal["a", "b"]`
        - `description`  from `Annotated[..., Field(description=...)]`
        - `minimum`/`maximum`/etc. from `Field(ge=, le=, ...)`
        - `properties`/`required` from a same-module Pydantic BaseModel

    Unwraps `Optional[X]` / `Union[X, None]` / `X | None` before mapping.
    """
    if annotation is None:
        return {"type": "string"}

    unwrapped = _unwrap_optional(annotation)
    if unwrapped is not annotation:
        return _property_schema(unwrapped, module_classes)

    if _is_annotated(annotation):
        inner, field_calls = _split_annotated(annotation)
        prop = _property_schema(inner, module_classes)
        for call in field_calls:
            prop.update(_field_call_to_schema(call))
        return prop

    if _is_literal(annotation):
        values = _literal_values(annotation)
        return {"type": "string", "enum": values}

    if isinstance(annotation, ast.Name):
        # Same-module Pydantic model — expand its fields inline.
        if module_classes and annotation.id in module_classes:
            return _model_schema(module_classes[annotation.id], module_classes)
        return {"type": _TYPE_HINT_MAP.get(annotation.id, "string")}

    if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name):
        return {"type": _TYPE_HINT_MAP.get(annotation.value.id, "string")}

    return {"type": "string"}


def _model_schema(
    class_def: ast.ClassDef,
    module_classes: dict[str, ast.ClassDef],
) -> dict[str, Any]:
    """Build a JSON Schema object dict from a Pydantic-style class definition.

    Walks the class body for `field_name: type = Field(...)` or
    `field_name: type = <default>` annotated assignments. A field without a
    default is required. Field(...) kwargs surface as JSON Schema enrichments.
    """
    properties: dict[str, Any] = {}
    required: list[str] = []
    for stmt in class_def.body:
        if not isinstance(stmt, ast.AnnAssign) or not isinstance(stmt.target, ast.Name):
            continue
        field_name = stmt.target.id
        if field_name.startswith("_") or field_name == "model_config":
            continue
        prop = _property_schema(stmt.annotation, module_classes)
        if isinstance(stmt.value, ast.Call):
            prop.update(_field_call_to_schema(stmt.value))
        # Required = no default value at all, or Field(...) with no `default=` /
        # `default_factory=` kwarg and no positional default. Pydantic's `...`
        # (Ellipsis) marks a required field explicitly.
        if _field_is_required(stmt.value):
            required.append(field_name)
        properties[field_name] = prop

    schema: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema


def _field_is_required(value: ast.expr | None) -> bool:
    """True when an AnnAssign value indicates a required field.

    - No value (`name: str` with nothing after `=` is illegal in Python AnnAssign,
      so this case means `value is None` — required).
    - `Field(...)` with no `default` / `default_factory` kwarg — required.
    - `Field(...)` with positional Ellipsis as first arg — required.
    - Anything else (literal default, `Field(default=...)`, `Field(default_factory=...)`) — optional.
    """
    if value is None:
        return True
    if not isinstance(value, ast.Call):
        return False  # `x: int = 10` — has a default literal, not required.
    callee = value.func
    callee_name = callee.id if isinstance(callee, ast.Name) else (
        callee.attr if isinstance(callee, ast.Attribute) else None
    )
    if callee_name != "Field":
        return False
    # Ellipsis as first positional arg = required.
    if value.args and isinstance(value.args[0], ast.Constant) and value.args[0].value is Ellipsis:
        return True
    has_default = any(
        kw.arg in {"default", "default_factory"} for kw in value.keywords
    )
    return not has_default


def _is_annotated(annotation: ast.expr) -> TypeGuard[ast.Subscript]:
    return (
        isinstance(annotation, ast.Subscript)
        and isinstance(annotation.value, ast.Name)
        and annotation.value.id == "Annotated"
    )


def _split_annotated(annotation: ast.Subscript) -> tuple[ast.expr, list[ast.Call]]:
    """Return (inner_type, [Field(...) calls in the Annotated metadata])."""
    slice_node = annotation.slice
    if not isinstance(slice_node, ast.Tuple) or not slice_node.elts:
        return slice_node, []
    inner = slice_node.elts[0]
    field_calls = [e for e in slice_node.elts[1:] if isinstance(e, ast.Call)]
    return inner, field_calls


def _is_literal(annotation: ast.expr) -> TypeGuard[ast.Subscript]:
    return (
        isinstance(annotation, ast.Subscript)
        and isinstance(annotation.value, ast.Name)
        and annotation.value.id == "Literal"
    )


def _literal_values(annotation: ast.Subscript) -> list[Any]:
    """Extract the values inside Literal[a, b, c]."""
    slice_node = annotation.slice
    if isinstance(slice_node, ast.Tuple):
        return [e.value for e in slice_node.elts if isinstance(e, ast.Constant)]
    if isinstance(slice_node, ast.Constant):
        return [slice_node.value]
    return []


# Pydantic Field(...) kwarg → JSON Schema property key.
_FIELD_KWARG_TO_SCHEMA = {
    "description": "description",
    "ge": "minimum",
    "gt": "exclusiveMinimum",
    "le": "maximum",
    "lt": "exclusiveMaximum",
    "min_length": "minLength",
    "max_length": "maxLength",
    "pattern": "pattern",
}


def _field_call_to_schema(call: ast.Call) -> dict[str, Any]:
    """Map kwargs of a `Field(...)` (or `Field(default=..., ...)`) call to JSON Schema keys."""
    # Only treat calls whose callee is named "Field" — be tolerant of import aliases.
    callee = call.func
    callee_name = None
    if isinstance(callee, ast.Name):
        callee_name = callee.id
    elif isinstance(callee, ast.Attribute):
        callee_name = callee.attr
    if callee_name != "Field":
        return {}

    out: dict[str, Any] = {}
    for kw in call.keywords:
        if kw.arg is None:
            continue
        if kw.arg in _FIELD_KWARG_TO_SCHEMA and isinstance(kw.value, ast.Constant):
            out[_FIELD_KWARG_TO_SCHEMA[kw.arg]] = kw.value.value
    return out


def _unwrap_optional(annotation: ast.expr) -> ast.expr:
    """Strip Optional[X], Union[X, None], and X | None down to X.

    Returns the original annotation when no Optional/Union-with-None pattern
    is present. Handles arbitrary nesting of these forms.
    """
    # Optional[X]  →  Subscript(value=Name('Optional'), slice=X)
    if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name):
        if annotation.value.id == "Optional":
            return _unwrap_optional(annotation.slice)
        if annotation.value.id == "Union":
            # Union[X, None] — Subscript(slice=Tuple(elts=[X, None]))
            if isinstance(annotation.slice, ast.Tuple):
                non_none = [
                    e for e in annotation.slice.elts
                    if not (isinstance(e, ast.Constant) and e.value is None)
                ]
                if len(non_none) == 1:
                    return _unwrap_optional(non_none[0])

    # X | None  →  BinOp(left=X, op=BitOr, right=Constant(None))
    if isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
        left_is_none = isinstance(annotation.left, ast.Constant) and annotation.left.value is None
        right_is_none = isinstance(annotation.right, ast.Constant) and annotation.right.value is None
        if right_is_none and not left_is_none:
            return _unwrap_optional(annotation.left)
        if left_is_none and not right_is_none:
            return _unwrap_optional(annotation.right)

    return annotation
