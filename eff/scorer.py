# -*- coding: utf-8 -*-
"""This module contains the implementation of the EFF scorer."""

from __future__ import annotations
import argparse
import json
import os
from typing import Literal
from pydantic import BaseModel, Field, create_model
from pathlib import Path

from eff.providers import DEFAULT_MODEL, get_provider
from eff.retrieval import RetrievedChunk, get_retriever


DEFAULT_DIMENSIONS_PATH = (
    Path(__file__).resolve().parent / "resources" / "dimensions.json"
)
BUILTIN_DIMENSIONS = ("utility", "fairness", "privacy", "explainability", "safety")
EXTRA_DIMENSIONS_ENV = "EFF_EXTRA_DIMENSIONS_PATH"


class DimensionScore(BaseModel):
    result: Literal["pass", "Needs Improvement", "fail"]
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str = Field(min_length=1)
    severity: Literal["low", "medium", "high"] | None = None


class ScoreResults(BaseModel):
    utility: DimensionScore
    fairness: DimensionScore
    privacy: DimensionScore
    explainability: DimensionScore
    safety: DimensionScore


class AcceptanceCriterion(BaseModel):
    dimension: str
    criterion: str


class EFFOutput(ScoreResults):
    enhanced_story: str
    acceptance_criteria: list[AcceptanceCriterion]


class ScoreSummary(BaseModel):
    passed: int
    needs_improvement: int
    failed: int


class Source(BaseModel):
    snippet: str
    source: str
    score: float


class ScoreResponse(BaseModel):
    content: str
    model: str
    results: ScoreResults
    custom_results: dict[str, DimensionScore] = {}
    summary: ScoreSummary
    enhanced_story: str
    acceptance_criteria: list[AcceptanceCriterion]
    sources: list[Source] = []
def load_extra_dimensions(path: str | None) -> dict:
    """Load and validate user-defined extra dimensions.

    Custom dimensions extend the 5 built-ins — they cannot replace them.
    Each must follow the same schema (description, rubric, scoring_notes).
    Names must be unique, not collide with built-ins, and be valid Python
    identifiers so they can become Pydantic field names.

    Returns an empty dict if `path` is falsy or the file does not exist.
    """
    if not path or not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    extras = data["dimensions"] if "dimensions" in data else data

    if not isinstance(extras, dict):
        raise ValueError("extra dimensions file must be a JSON object")

    for name in extras:
        if name in BUILTIN_DIMENSIONS:
            raise ValueError(
                f"extra dimension '{name}' collides with a built-in EFF dimension; "
                "extras can extend but not replace the 5 built-in dimensions"
            )
        if not name.isidentifier():
            raise ValueError(
                f"extra dimension name '{name}' is not a valid identifier "
                "(letters, digits, underscores; cannot start with a digit)"
            )
        entry = extras[name]
        if not isinstance(entry, dict) or "description" not in entry or "rubric" not in entry:
            raise ValueError(
                f"extra dimension '{name}' must include 'description' and 'rubric'"
            )

    return extras

def build_eff_output_class(extra_dimension_names: list[str]) -> type[BaseModel]:
    """Build a Pydantic schema for the LLM output, including any extra dimensions.

    With no extras this is equivalent to `EFFOutput`. With extras, each name
    becomes an additional `DimensionScore` field on the model, so the LLM is
    constrained to score them as part of its structured output.
    """
    if not extra_dimension_names:
        return EFFOutput

    extras_fields = {name: (DimensionScore, ...) for name in extra_dimension_names}
    return create_model(
        "EFFOutputDynamic",
        __base__=EFFOutput,
        **extras_fields,
    )


def _make_snippet(text: str, max_chars: int = 150) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars].rstrip() + "…"


def load_dimensions(dimensions_path: str) -> dict:
    if not os.path.exists(dimensions_path):
        raise FileNotFoundError(f"dimensions.json not found at: {dimensions_path}")

    with open(dimensions_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dimensions = data["dimensions"] if "dimensions" in data else data
    required = {"utility", "fairness", "privacy", "explainability", "safety"}
    missing = required - set(dimensions.keys())
    if missing:
        raise ValueError(f"dimensions.json missing required dimensions: {sorted(missing)}")

    return dimensions


def build_messages(
    content: str,
    dimensions: dict,
    context: list[RetrievedChunk] | None = None,
    severity_context: str | None = None,
) -> list[dict]:
    rubric_json = json.dumps(dimensions, indent=2)

    system_prompt = (
        "You are an expert evaluator for the Ethics Filter Framework (EFF). "
        "Assess the provided content against the supplied rubric. "
        "For each dimension, use the rubric and scoring_notes to assign one result: pass, Needs Improvement, or fail. "
        "Be conservative when information is missing or unclear. "
        "If justification for pass is not explicit, prefer Needs Improvement. "
        "Return only structured output as specified."
    )

    literature_section = ""
    context_section = ""
    if context:
        formatted = "\n\n".join(
            f"[{i+1}] {chunk.source}\n{chunk.text}" for i, chunk in enumerate(context)
        )
        literature_section = (
            "RELEVANT LITERATURE (use these passages to ground your reasoning; "
            "cite the bracketed index in the reason field when you rely on a passage):\n"
            f"{formatted}\n\n"
        )
        context_section = literature_section

    severity_section = ""
    severity_instructions = (
        "- Set 'severity' to null for every dimension (no application context provided).\n"
    )
    if severity_context:
        severity_section = (
            "APPLICATION CONTEXT:\n"
            f"{severity_context}\n\n"
            "Use this context to weight the severity of any non-pass results: a "
            "Privacy concern in a health app is more severe than the same concern "
            "in a chat app. Severity is independent of confidence — it grades the "
            "magnitude of the concern in this context, not how sure you are.\n\n"
        )
        severity_instructions = (
            "- For each dimension, set 'severity' as follows:\n"
            "  - null when result is 'pass' (no concern to grade)\n"
            "  - 'low' when the concern is minor or largely hypothetical in this context\n"
            "  - 'medium' when the concern is real but mitigable\n"
            "  - 'high' when the concern is serious and demands action before shipping\n"
        )

    user_prompt = (
        "Evaluate the following content using the EFF rubric (JSON below).\n\n"
        f"{literature_section}"
        f"{severity_section}"
        f"{context_section}"
        "CONTENT:\n"
        f"{content}\n\n"
        "RUBRIC:\n"
        f"{rubric_json}\n\n"
        "Instructions:\n"
        "- For each dimension, use the rubric and scoring_notes to guide your judgment.\n"
        "- Do not invent details not present in the content.\n"
        "- Confidence must be a float between 0.0 and 1.0.\n"
        "- Reason must be brief, specific, and defensible.\n"
        "- Use 'Needs Improvement' instead of 'borderline' if the justification for pass is not explicit.\n"
        f"{severity_instructions}"
        "\n"
        "For enhanced_story:\n"
        "- Reproduce the original story verbatim.\n"
        "- If any dimension is not 'pass', append ', without [harm phrase].' where the harm phrase is a concise, natural-language synthesis of the core risks — do NOT copy reasons verbatim.\n"
        "- If all dimensions pass, reproduce the story unchanged.\n"
        "\n"
        "For acceptance_criteria:\n"
        "- Include one entry per dimension that is not 'pass'.\n"
        "- Each criterion must be specific and testable, not a restatement of the problem.\n"
        "- Good example: 'The system must display a privacy notice listing what is collected, for what purpose, and for how long, before first use.'\n"
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_client(model: str = DEFAULT_MODEL) -> object:
    """Build and return a configured OpenAI client. Exposed for testing/patching."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set.")
    from openai import OpenAI
    kwargs: dict = {"api_key": api_key, "timeout": 30.0}
    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def call_model(
    content: str,
    dimensions: dict,
    model: str = DEFAULT_MODEL,
    extra_dimensions: dict | None = None,
    severity_context: str | None = None,
) -> ScoreResponse:
    client = build_client(model=model)
    retriever = get_retriever()
    context = retriever.retrieve(content)

    extra_dimensions = extra_dimensions or {}
    extra_names = list(extra_dimensions.keys())
    merged = {**dimensions, **extra_dimensions}

    output_schema = build_eff_output_class(extra_names)
    messages = build_messages(
        content,
        merged,
        context=context,
        severity_context=severity_context,
    )
    response = client.responses.parse(
        model=model,
        input=messages,
        text_format=output_schema,
    )
    parsed = response.output_parsed
    if parsed is None:
        raise ValueError("Model returned no parsed structured output.")

    results = ScoreResults(
        utility=parsed.utility,
        fairness=parsed.fairness,
        privacy=parsed.privacy,
        explainability=parsed.explainability,
        safety=parsed.safety,
    )
    custom_results = {name: getattr(parsed, name) for name in extra_names}
    all_scores = list(results.model_dump().values()) + [
        s.model_dump() for s in custom_results.values()
    ]
    summary = ScoreSummary(
        passed=sum(1 for x in all_scores if x["result"] == "pass"),
        needs_improvement=sum(1 for x in all_scores if x["result"] == "Needs Improvement"),
        failed=sum(1 for x in all_scores if x["result"] == "fail"),
    )

    sources = [
        Source(
            snippet=_make_snippet(chunk.text),
            source=chunk.source,
            score=chunk.score,
        )
        for chunk in context
    ]

    return ScoreResponse(
        content=content,
        model=model,
        results=results,
        custom_results=custom_results,
        summary=summary,
        enhanced_story=parsed.enhanced_story,
        acceptance_criteria=parsed.acceptance_criteria,
        sources=sources,
    )


def score_story(
    content: str,
    dimensions_path: str = str(DEFAULT_DIMENSIONS_PATH),
    model: str = DEFAULT_MODEL,
    extra_dimensions_path: str | None = None,
    context: str | None = None,
) -> dict:
    dimensions = load_dimensions(dimensions_path)
    extras = load_extra_dimensions(
        extra_dimensions_path or os.getenv(EXTRA_DIMENSIONS_ENV)
    )
    result = call_model(
        content=content,
        dimensions=dimensions,
        model=model,
        extra_dimensions=extras,
        severity_context=context,
    )
    return result.model_dump()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the EFF scorer on a user story.")
    parser.add_argument(
        "content",
        nargs="?",
        default="As a user I want recommendations so I can find content.",
        help="The content or user story to score.",
    )
    parser.add_argument(
        "--dimensions",
        default=DEFAULT_DIMENSIONS_PATH,
        help="Path to dimensions.json",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Model name to use",
    )

    args = parser.parse_args()

    try:
        result = score_story(
            content=args.content,
            dimensions_path=args.dimensions,
            model=args.model,
        )
        json_output = json.dumps(result, indent=2, ensure_ascii=False)
        print(json_output)
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
        json_output = json.dumps({"error": error}, indent=2)
        print(json_output)
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
