from __future__ import annotations

from .models import PrimitiveKind, ServerPlan


def generate_plan(project_goal: str, primitives_wanted: list[str]) -> ServerPlan:
    primitives = [_coerce_primitive(value) for value in primitives_wanted]
    unique_primitives = list(dict.fromkeys(primitives))

    checklist = [
        "Define the server object with `mcp = FastMCP(...)`.",
        "Add typed Pydantic models for structured inputs and outputs.",
        "Implement each primitive with the matching FastMCP decorator.",
        "Keep runtime behavior local and deterministic.",
        "Add pytest coverage for classification, review, and server registration.",
    ]

    files = [
        "pyproject.toml",
        "src/<package>/server.py",
        "src/<package>/models.py",
        "tests/test_server_smoke.py",
        "README.md",
    ]

    if PrimitiveKind.RESOURCE in unique_primitives:
        files.append("docs/<topic>.md")
    if PrimitiveKind.PROMPT in unique_primitives:
        checklist.append("Document prompt arguments and expected workflow boundaries.")

    return ServerPlan(
        goal=project_goal,
        files=files,
        checklist=checklist,
        primitives=unique_primitives,
    )


def _coerce_primitive(value: str) -> PrimitiveKind:
    lowered = value.strip().lower()
    if lowered in {"tool", "tools"}:
        return PrimitiveKind.TOOL
    if lowered in {"resource", "resources"}:
        return PrimitiveKind.RESOURCE
    if lowered in {"prompt", "prompts"}:
        return PrimitiveKind.PROMPT
    raise ValueError(f"Unknown primitive: {value}")
