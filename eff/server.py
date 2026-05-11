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
def ethics_filter(user_story: str, context: str | None = None) -> dict:
    """Run the Ethics Filter Framework on a user story.

    Args:
        user_story: The user story to evaluate (standard agile format).
        context: Optional short description of the application domain
            (e.g. "patient-facing health app", "internal admin tool").
            When provided, every dimension's severity field is set to
            low / medium / high in this context. When omitted, severity is null.

    Server-level configuration (set via env at MCP host startup, not per call):
        OPENAI_API_KEY (required) — model provider credential.
        OPENAI_MODEL (optional, default "gpt-5.4-mini") — model override.
        OPENAI_BASE_URL (optional) — for OpenAI-compatible endpoints.
        EFF_RETRIEVAL_PROVIDER (optional) — "supabase" enables RAG; default off.
        SUPABASE_URL, SUPABASE_KEY — required when RAG is enabled.
        EFF_EXTRA_DIMENSIONS_PATH (optional) — path to a JSON file with extra
            domain-specific dimensions; scored alongside the 5 built-ins.
        EFF_AUDIT_LOG_PATH (optional) — path to a JSONL audit log; one row per
            successful invocation. Disabled by default.

    Returns:
        A dict with the per-dimension scores, an enhanced story, acceptance
        criteria, a summary count, and (when RAG is enabled) retrieved sources.
        On configuration or runtime failure, returns
        {"error": "...", "detail": "..."} instead.
    """
    try:
        return score_story(
            content=user_story,
            dimensions_path=DEFAULT_DIMENSIONS_PATH,
            model=DEFAULT_MODEL,
            context=context,
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


@mcp.tool()
def get_skill_instructions() -> str:
    """Return the EFF skill instructions and workflow (eff://skill)."""
    return read_resource("SKILL.md")


@mcp.tool()
def get_dimensions_rubric() -> str:
    """Return the EFF rubric and dimension definitions (eff://dimensions)."""
    return read_resource("dimensions.json")


@mcp.tool()
def get_examples() -> str:
    """Return the EFF worked examples and templates (eff://examples)."""
    return read_resource("examples.md")

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
def get_examples_resource():
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
