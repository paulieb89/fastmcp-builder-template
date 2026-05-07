from fastmcp_builder.models import PrimitiveKind
from fastmcp_builder.scaffold import generate_plan


def test_generate_plan_returns_files_and_primitives():
    plan = generate_plan("Teach MCP basics", ["tool", "resource", "prompt"])

    assert plan.goal == "Teach MCP basics"
    assert PrimitiveKind.TOOL in plan.primitives
    assert PrimitiveKind.RESOURCE in plan.primitives
    assert PrimitiveKind.PROMPT in plan.primitives
    assert "src/<package>/server.py" in plan.files
