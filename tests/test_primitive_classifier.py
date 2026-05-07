from fastmcp_builder.models import PrimitiveKind
from fastmcp_builder.server import classify_mcp_primitive


def test_classifies_model_controlled_capability_as_tool():
    result = classify_mcp_primitive("review a manifest and return findings", "model", "model")

    assert result.recommendation == PrimitiveKind.TOOL


def test_classifies_client_readable_context_as_resource():
    result = classify_mcp_primitive("expose docs content", "client", "client")

    assert result.recommendation == PrimitiveKind.RESOURCE


def test_classifies_user_workflow_as_prompt():
    result = classify_mcp_primitive("create a reusable design workflow", "user", "user")

    assert result.recommendation == PrimitiveKind.PROMPT
