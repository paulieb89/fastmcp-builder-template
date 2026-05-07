from fastmcp_builder.models import ParameterSpec, ResourceContract, ToolContract, PromptContract
from fastmcp_builder.server import (
    check_error_response_design,
    suggest_prompt_contract,
    suggest_resource_contract,
    suggest_tool_contract,
)


def test_suggest_tool_contract_returns_valid_contract():
    result = suggest_tool_contract("validate email addresses")

    assert isinstance(result, ToolContract)
    assert isinstance(result.name, str) and result.name
    assert len(result.parameters) >= 1
    assert all(isinstance(p, ParameterSpec) for p in result.parameters)
    assert len(result.error_cases) >= 1


def test_suggest_resource_contract_returns_valid_contract():
    result = suggest_resource_contract("local project changelog")

    assert isinstance(result, ResourceContract)
    assert result.uri_pattern.startswith("fastmcp-builder://")
    assert result.mime_type == "text/markdown"


def test_suggest_prompt_contract_returns_valid_contract():
    result = suggest_prompt_contract("design a local MCP server")

    assert isinstance(result, PromptContract)
    assert isinstance(result.name, str) and result.name
    assert len(result.arguments) >= 1
    assert all(isinstance(a, ParameterSpec) for a in result.arguments)


def test_check_error_response_design_classifies_modes():
    result = check_error_response_design(
        tool_behavior="parse and validate structured input",
        failure_modes=[
            "missing required field",
            "timeout when reading large file",
            "unauthorized access to restricted path",
            "operation is outside the supported scope",
        ],
    )

    assert "missing required field" in result.validation_errors
    assert "timeout when reading large file" in result.transient_errors
    assert "unauthorized access to restricted path" in result.permission_errors
    assert "operation is outside the supported scope" in result.business_errors
