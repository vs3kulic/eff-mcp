"""
EFF MCP Server: Entry point for serving EFF resources and evaluation logic.
"""
from fastmcp import FastMCP

mcp = FastMCP("eff-mcp")

@mcp.tool()
def ethics_filter(user_story: str) -> str:
    """Run the Ethics Filter Framework on a User Story."""
    return f"EFF received your story: '{user_story}' — scorer not yet connected."

if __name__ == "__main__":
    mcp.run()
