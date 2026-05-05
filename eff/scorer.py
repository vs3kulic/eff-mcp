# -*- coding: utf-8 -*-
"""This module contains the implementation of the EFF scorer."""

from __future__ import annotations
import argparse
import json
import os
from typing import Literal
from pydantic import BaseModel, Field
from pathlib import Path

from eff.providers import DEFAULT_MODEL, get_provider
from eff.retrieval import RetrievedChunk, get_retriever

DEFAULT_DIMENSIONS_PATH = (
    Path(__file__).resolve().parent / "resources" / "dimensions.json"
)


class DimensionScore(BaseModel):
    result: Literal["pass", "Needs Improvement", "fail"]
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str = Field(min_length=1)


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


class ScoreResponse(BaseModel):
    content: str
    model: str
    results: ScoreResults
    summary: ScoreSummary
    enhanced_story: str
    acceptance_criteria: list[AcceptanceCriterion]


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

    context_section = ""
    if context:
        formatted = "\n\n".join(
            f"[{i+1}] {chunk.source}\n{chunk.text}" for i, chunk in enumerate(context)
        )
        context_section = (
            "RELEVANT LITERATURE (use these passages to ground your reasoning; "
            "cite the bracketed index in the reason field when you rely on a passage):\n"
            f"{formatted}\n\n"
        )

    user_prompt = (
        "Evaluate the following content using the EFF rubric (JSON below).\n\n"
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


def call_model(content: str, dimensions: dict, model: str = DEFAULT_MODEL) -> ScoreResponse:
    client = build_client(model=model)
    retriever = get_retriever()
    context = retriever.retrieve(content)
    messages = build_messages(content, dimensions, context=context)
    response = client.responses.parse(
        model=model,
        input=messages,
        text_format=EFFOutput,
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
    summary = ScoreSummary(
        passed=sum(1 for x in results.model_dump().values() if x["result"] == "pass"),
        needs_improvement=sum(1 for x in results.model_dump().values() if x["result"] == "Needs Improvement"),
        failed=sum(1 for x in results.model_dump().values() if x["result"] == "fail"),
    )

    return ScoreResponse(
        content=content,
        model=model,
        results=results,
        summary=summary,
        enhanced_story=parsed.enhanced_story,
        acceptance_criteria=parsed.acceptance_criteria,
    )


def score_story(
    content: str,
    dimensions_path: str = str(DEFAULT_DIMENSIONS_PATH),
    model: str = DEFAULT_MODEL,
) -> dict:
    dimensions = load_dimensions(dimensions_path)
    result = call_model(content=content, dimensions=dimensions, model=model)
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
