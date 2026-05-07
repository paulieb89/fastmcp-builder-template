from fastmcp import FastMCP

mcp = FastMCP("Minimal Example")


@mcp.tool
def add(a: int, b: int) -> int:
    """Add two integers and return the sum."""
    return a + b


@mcp.resource("example://readme")
def readme() -> str:
    """Expose a small static resource."""
    return "This is a local example resource."


@mcp.prompt
def explain_code(topic: str) -> str:
    """Create a reusable explanation workflow."""
    return f"Explain this FastMCP topic clearly: {topic}"
