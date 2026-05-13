# -*- coding: utf-8 -*-
"""This module contains the FastMCP server implementation for the EFF scorer."""
import logging
import sys
import os
from pathlib import Path
from fastmcp import FastMCP
from eff.scorer import score_story, DEFAULT_DIMENSIONS_PATH, DEFAULT_MODEL
import bibtexparser
import asyncio
import aiohttp


RESOURCES_PATH = Path(__file__).resolve().parent / "resources"

# --- BibTeX cache ---
_bib_db = None

def get_bib_db():
    global _bib_db
    if _bib_db is None:
        bib_path = RESOURCES_PATH / "references.bib"
        with open(bib_path, "r", encoding="utf-8") as bibfile:
            _bib_db = bibtexparser.load(bibfile)
    return _bib_db

logger = logging.getLogger("eff")

def read_resource(filename: str) -> str:
    return (RESOURCES_PATH / filename).read_text(encoding="utf-8")


mcp = FastMCP("eff-mcp")


#############
# MCP Tools #
#############

async def verify_doi(doi: str) -> bool:
    url = f"https://doi.org/{doi}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, allow_redirects=True, timeout=8) as resp:
                return resp.status == 200
    except Exception:
        return False


async def generate_and_verify_citations(dim: str, fail_or_ni: str, story: str, model: str) -> list:
    """Generate citations for a dimension using LLM and verify DOIs."""
    import openai
    import json
    prompt = (
        f"Provide 2-3 real academic citations (JSON list) for the topic: '{dim}' "
        f"in the context of user story quality, ethics, or requirements engineering, "
        f"in the context of this user story: '{story}'. "
        f"Only include peer-reviewed articles or books. Each citation must have: author, title, journal, year, doi. "
        f"Return only a JSON array, no prose. "
        f"Example: [{{'author': '...', 'title': '...', 'journal': '...', 'year': 2021, 'doi': '10.1234/abcd'}}]"
    )
    citations = []
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        completion = await asyncio.to_thread(
            client.chat.completions.create,
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful academic assistant."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=800,
            temperature=0.2,
        )
        content = completion.choices[0].message.content
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            citations = parsed.get("citations", [])
        elif isinstance(parsed, list):
            citations = parsed
    except Exception as exc:
        logger.warning(f"Citation generation failed for {dim}: {exc}")
        return []

    # Verify DOIs concurrently
    tasks = [verify_doi(cit.get("doi", "")) for cit in citations if "doi" in cit]
    results = await asyncio.gather(*tasks)
    return [cit for cit, ok in zip(citations, results) if ok]


async def _run_ethics_filter(user_story: str, context: str | None = None) -> dict:
    """
    Internal helper for ethics_filter. Handles both RAG and citation modes.
    Returns the scoring dict, possibly with citations.
    Raises exceptions on error.
    """
    rag_url = os.getenv("SUPABASE_URL")

    scoring = score_story(
        content=user_story,
        dimensions_path=DEFAULT_DIMENSIONS_PATH,
        model=DEFAULT_MODEL
    )

    dim_results = scoring.get("results", {})

    if rag_url:
        # RAG mode: retrieve sources per failing/needs-improvement dimension, tag with dimension
        from eff.retrieval import get_retriever
        retriever = get_retriever()
        async def retrieve_for_dim(dim, result):
            # Use dimension name and reason as query for best relevance
            query = f"{dim}: {result.get('reason', '')}"
            # Run in thread to avoid blocking event loop if retriever is sync
            chunks = await asyncio.to_thread(retriever.retrieve, query)
            # Tag each chunk with the dimension
            return [dict(snippet=c.text, source=c.source, score=c.score, dimension=dim) for c in chunks]
        tasks = [
            retrieve_for_dim(dim, result)
            for dim, result in dim_results.items()
            if result["result"] in ("fail", "Needs Improvement")
        ]
        per_dim_chunks = await asyncio.gather(*tasks)
        # Flatten
        scoring["sources"] = [chunk for chunks in per_dim_chunks for chunk in chunks]
        return scoring

    # Citation mode: generate and verify citations per failing/needs-improvement dimension
    citation_model = os.getenv("CITATION_MODEL", DEFAULT_MODEL)

    async def gather_citations():
        tasks = [
            (dim, generate_and_verify_citations(dim, result["result"], user_story, citation_model))
            for dim, result in dim_results.items()
            if result["result"] in ("fail", "Needs Improvement")
        ]
        citations = await asyncio.gather(*(t[1] for t in tasks))
        return {dim: cits for (dim, _), cits in zip(tasks, citations)}

    sources_dict = await gather_citations()

    # Normalise to flat list with dimension field
    scoring["sources"] = [
        {**cit, "dimension": dim}
        for dim, cits in sources_dict.items()
        for cit in cits
    ]
    return scoring


@mcp.tool()
async def ethics_filter(user_story: str, context: str | None = None) -> dict:
    """
    Run the Ethics Filter Framework on a user story.

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
        CITATION_MODEL (optional) — model for citation generation (default: OPENAI_MODEL).

    Returns:
        A dict with the per-dimension scores, an enhanced story, acceptance
        criteria, a summary count, and sources (flat list with dimension field).
        - RAG mode (SUPABASE_URL set): sources are RAG chunks from the corpus.
        - Citation mode (default): sources are verified academic citations per
          failed/needs_improvement dimension.
        On configuration or runtime failure, returns
        {"error": "...", "detail": "..."} instead.
    """
    try:
        return await _run_ethics_filter(user_story, context)
    except EnvironmentError as exc:
        logger.error("Configuration error: %s", exc)
        return {"error": "configuration_error", "detail": str(exc)}
    except Exception as exc:
        logger.exception("ethics_filter failed")
        return {"error": "internal_error", "detail": str(exc)}


@mcp.tool()
def list_eff_resources() -> dict:
    """List available EFF MCP resources and their descriptions."""
    return {
        "resources": [
            {"uri": "eff://dimensions", "description": "EFF rubric and dimension definitions (JSON)"},
            {"uri": "eff://skill", "description": "EFF skill instructions and workflow (Markdown)"},
            {"uri": "eff://examples", "description": "EFF worked examples and templates (Markdown)"}
        ]
    }


@mcp.tool()
def list_bib_resources() -> list:
    """List all BibTeX entries as MCP resources with minimal metadata."""
    bib_db = get_bib_db()
    return [
        {
            "uri": f"bib://{entry.get('ID')}",
            "key": entry.get("ID"),
            "title": entry.get("title", ""),
            "doi": entry.get("doi", ""),
        }
        for entry in bib_db.entries
    ]


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


@mcp.tool()
def search_citations(query: str) -> list:
    """Search BibTeX entries for a query string in any field. Returns minimal metadata."""
    bib_db = get_bib_db()
    return [
        {
            "key": entry.get("ID"),
            "title": entry.get("title", ""),
            "author": entry.get("author", ""),
            "year": entry.get("year", ""),
            "doi": entry.get("doi", ""),
            "uri": f"bib://{entry.get('ID')}"
        }
        for entry in bib_db.entries
        if any(query.lower() in str(value).lower() for value in entry.values())
    ]


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


@mcp.resource("bib://{key}")
def get_bib_entry(key: str):
    """Serve a single BibTeX entry by key."""
    bib_db = get_bib_db()
    entry = bib_db.entries_dict.get(key)
    if entry is None:
        return {"error": "not_found", "detail": f"No entry with key '{key}'"}
    return entry


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        stream=sys.stderr,
    )
    mcp.run()


if __name__ == "__main__":
    main()