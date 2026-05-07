from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from fastmcp_builder.docs import list_examples, list_markdown_docs, read_doc, read_example
from fastmcp_builder.models import (
    DescriptionQualityReport,
    ErrorDesignReport,
    ParameterSpec,
    PrimitiveClassification,
    PrimitiveKind,
    PromptContract,
    ResourceContract,
    ToolContract,
    UriStabilityReport,
)
from fastmcp_builder.review import check_uri_stability as _check_uri_stability, description_quality, review_fastmcp_manifest_data
from fastmcp_builder.scaffold import generate_plan


mcp = FastMCP("FastMCP Builder")


@mcp.tool
def classify_mcp_primitive(
    use_case: str,
    actor: str = "unknown",
    expected_control_pattern: str = "unknown",
) -> PrimitiveClassification:
    """Classify a capability as an MCP tool, resource, or prompt."""
    text = f"{use_case} {actor} {expected_control_pattern}".lower()

    if "user" in expected_control_pattern.lower() or "workflow" in text or "template" in text:
        return PrimitiveClassification(
            recommendation=PrimitiveKind.PROMPT,
            rationale="Use a prompt when the user intentionally starts a reusable workflow.",
            confidence=0.82,
            alternatives=["A tool may support individual steps inside the workflow."],
        )
    if "client" in expected_control_pattern.lower() or "read" in text or "expose" in text or "docs" in text:
        return PrimitiveClassification(
            recommendation=PrimitiveKind.RESOURCE,
            rationale="Use a resource when the server exposes data for the client to fetch or attach.",
            confidence=0.78,
            alternatives=["A tool is appropriate if the model must decide to compute or mutate something."],
        )
    return PrimitiveClassification(
        recommendation=PrimitiveKind.TOOL,
        rationale="Use a tool when the model should decide whether to invoke a typed capability.",
        confidence=0.74,
        alternatives=["A resource may fit if this is only static readable context."],
    )


@mcp.tool
def review_fastmcp_manifest(manifest: dict[str, Any]):
    """Review a FastMCP capability manifest for deterministic design issues."""
    return review_fastmcp_manifest_data(manifest)


@mcp.tool
def suggest_tool_contract(capability_description: str) -> ToolContract:
    """Suggest a narrow FastMCP tool contract from a capability description."""
    return ToolContract(
        name=_name_from_text(capability_description, "tool"),
        description=f"Use this tool to {capability_description.strip().rstrip('.')}.",
        parameters=[
            ParameterSpec(
                name="request",
                type="string",
                description="Plain-English request or source material to process.",
                required=True,
            )
        ],
        return_shape={"summary": "string", "recommendations": "list[string]", "warnings": "list[string]"},
        error_cases=[
            "validation_error: input is missing or too vague",
            "business_error: request is outside the tool boundary",
        ],
    )


@mcp.tool
def suggest_resource_contract(data_source_description: str) -> ResourceContract:
    """Suggest a local resource URI and read contract."""
    slug = _name_from_text(data_source_description, "resource").replace("_resource", "")
    return ResourceContract(
        uri_pattern=f"fastmcp-builder://docs/{slug}",
        mime_type="text/markdown",
        read_behavior="Read local curated project content without mutation or network access.",
        caching_notes="Content can be cached for the current session and refreshed when files change.",
    )


@mcp.tool
def suggest_prompt_contract(workflow_description: str) -> PromptContract:
    """Suggest a reusable MCP prompt contract for a workflow."""
    return PromptContract(
        name=_name_from_text(workflow_description, "workflow"),
        arguments=[
            ParameterSpec(
                name="goal",
                type="string",
                description="The outcome the user wants from the workflow.",
                required=True,
            ),
            ParameterSpec(
                name="constraints",
                type="string",
                description="Local boundaries, exclusions, and implementation preferences.",
                required=False,
            ),
        ],
        template_outline=[
            "Restate the goal and constraints.",
            "Classify requested MCP primitives.",
            "Propose a small implementation plan.",
            "Call out tests and safety boundaries.",
        ],
    )


@mcp.tool
def generate_minimal_server_plan(project_goal: str, primitives_wanted: list[str]):
    """Generate a minimal local FastMCP server implementation plan."""
    return generate_plan(project_goal, primitives_wanted)


@mcp.tool
def check_tool_description_quality(
    tool_name: str,
    description: str,
    schema: dict[str, Any],
) -> DescriptionQualityReport:
    """Check whether a tool description is specific enough for model-controlled use."""
    warnings = description_quality(tool_name, description, schema)
    return DescriptionQualityReport(passed=not warnings, warnings=warnings)


@mcp.tool
def check_uri_stability(uri_pattern: str) -> UriStabilityReport:
    """Check a resource URI pattern for stability issues that would break client integrations."""
    warnings = _check_uri_stability(uri_pattern)
    return UriStabilityReport(passed=not warnings, warnings=warnings)


@mcp.tool
def check_error_response_design(tool_behavior: str, failure_modes: list[str]) -> ErrorDesignReport:
    """Classify tool failure modes into practical error-response categories."""
    report = ErrorDesignReport()
    for mode in failure_modes:
        lowered = mode.lower()
        if any(word in lowered for word in ("missing", "invalid", "schema", "format")):
            report.validation_errors.append(mode)
        elif any(word in lowered for word in ("timeout", "temporary", "rate", "retry")):
            report.transient_errors.append(mode)
        elif any(word in lowered for word in ("permission", "secret", "unauthorized", "forbidden")):
            report.permission_errors.append(mode)
        else:
            report.business_errors.append(mode)
    report.notes.append(f"Design errors for behavior boundary: {tool_behavior}")
    return report


@mcp.resource("fastmcp-builder://docs")
def docs_index() -> str:
    """List curated learning docs available in this template."""
    return "\n".join(list_markdown_docs())


@mcp.resource("fastmcp-builder://docs/{slug}")
def docs_by_slug(slug: str) -> str:
    """Read a curated local documentation note by slug."""
    return read_doc(slug)


@mcp.resource("fastmcp-builder://examples")
def examples_index() -> str:
    """List local FastMCP examples available in this template."""
    return "\n".join(list_examples())


@mcp.resource("fastmcp-builder://examples/{name}")
def example_by_name(name: str) -> str:
    """Read a local example file by name."""
    return read_example(name)


@mcp.resource("fastmcp-builder://patterns/tool-design")
def tool_design_pattern() -> str:
    """Read the curated tool design pattern note."""
    return read_doc("tool-design")


@mcp.resource("fastmcp-builder://patterns/resource-design")
def resource_design_pattern() -> str:
    """Read the curated resource design pattern note."""
    return read_doc("resource-design")


@mcp.resource("fastmcp-builder://patterns/prompt-design")
def prompt_design_pattern() -> str:
    """Read the curated prompt design pattern note."""
    return read_doc("prompt-design")


@mcp.prompt
def design_fastmcp_server(project_goal: str, primitives: str, constraints: str = "local-only, deterministic") -> str:
    """Design a small FastMCP server before implementation."""
    return (
        "Design a local-first FastMCP v3 server.\n"
        f"Goal: {project_goal}\n"
        f"Requested primitives: {primitives}\n"
        f"Constraints: {constraints}\n"
        "Classify each primitive, propose files, identify safety boundaries, and list tests."
    )


@mcp.prompt
def review_fastmcp_server_design(manifest_summary: str) -> str:
    """Review a FastMCP server design for primitive boundaries and safety."""
    return (
        "Review this FastMCP server design. Focus on primitive classification, local-first operation, "
        "clear tool contracts, resource URI stability, prompt usefulness, and deterministic tests.\n\n"
        f"Design summary:\n{manifest_summary}"
    )


@mcp.prompt
def add_fastmcp_tool(tool_goal: str, constraints: str = "no shell execution, no runtime network") -> str:
    """Plan a single safe FastMCP tool addition."""
    return (
        f"Plan one FastMCP tool for: {tool_goal}\n"
        f"Constraints: {constraints}\n"
        "Return the tool name, parameters, return shape, error cases, implementation steps, and tests."
    )


@mcp.prompt
def prepare_claude_code_session(task: str) -> str:
    """Prepare Claude Code to work in this template."""
    return (
        "Work in explore, plan, implement, verify order for this local FastMCP template.\n"
        f"Task: {task}\n"
        "Do not add runtime network calls, shell execution tools, hosted services, databases, or background jobs."
    )


def _name_from_text(text: str, fallback_suffix: str) -> str:
    words = [word for word in "".join(ch if ch.isalnum() else " " for ch in text.lower()).split() if word]
    stop_words = {"a", "an", "and", "for", "from", "of", "the", "to", "with"}
    useful = [word for word in words if word not in stop_words][:5]
    if not useful:
        useful = ["fastmcp", fallback_suffix]
    name = "_".join(useful)
    if not name.endswith(fallback_suffix):
        name = f"{name}_{fallback_suffix}"
    return name[:64]


if __name__ == "__main__":
    mcp.run()
