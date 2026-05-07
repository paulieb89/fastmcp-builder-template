def design_prompt(project_goal: str, constraints: str) -> str:
    return (
        "Design a local FastMCP server.\n"
        f"Goal: {project_goal}\n"
        f"Constraints: {constraints}\n"
        "Return primitives, files, safety boundaries, and tests."
    )
