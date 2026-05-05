# -*- coding: utf-8 -*-
"""This module contains the FastMCP server implementation for the EFF scorer."""
import logging
import sys
from pathlib import Path
from fastmcp import FastMCP
from eff.scorer import score_story, DEFAULT_DIMENSIONS_PATH, DEFAULT_MODEL

RESOURCES_PATH = Path(__file__).resolve().parent / "resources"

logger = logging.getLogger("eff")

def read_resource(filename: str) -> str:
    return (RESOURCES_PATH / filename).read_text(encoding="utf-8")

mcp = FastMCP("eff-mcp")


#############
# MCP Tools #
#############

@mcp.tool()
def ethics_filter(user_story: str) -> dict:
    """Run the Ethics Filter Framework on a user story."""
    try:
        return score_story(
            content=user_story,
            dimensions_path=DEFAULT_DIMENSIONS_PATH,
            model=DEFAULT_MODEL,
        )
    except EnvironmentError as exc:
        logger.error("Configuration error: %s", exc)
        return {"error": "configuration_error", "detail": str(exc)}
    except Exception as exc:
        logger.exception("ethics_filter failed")
        return {"error": "internal_error", "detail": str(exc)}


@mcp.tool()
def list_resources() -> dict:
    """List available EFF MCP resources and their descriptions."""
    return {
        "resources": [
            {"uri": "eff://dimensions",
             "description": "EFF rubric and dimension definitions (JSON)"},
            {"uri": "eff://skill",
             "description": "EFF skill instructions and workflow (Markdown)"},
            {"uri": "eff://examples",
             "description": "EFF worked examples and templates (Markdown)"}
        ]
    }

#################
# MCP Resources #
#################

@mcp.resource("eff://dimensions")
def get_dimensions():
    """Serve the EFF dimensions.json as an MCP resource."""
    return read_resource("dimensions.json")


@mcp.resource("eff://skill")
def get_skill():
    """Serve the EFF SKILL.md as an MCP resource."""
    return read_resource("SKILL.md")


@mcp.resource("eff://examples")
def get_examples():
    """Serve the EFF examples.md as an MCP resource."""
    return read_resource("examples.md")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        stream=sys.stderr,
    )
    mcp.run()


if __name__ == "__main__":
    main()
