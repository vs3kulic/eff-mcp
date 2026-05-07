# -*- coding: utf-8 -*-
"""End-to-end test against the real OpenAI API.

Run with: pytest -m integration tests/integration/test_openai_e2e.py

Requires: OPENAI_API_KEY in environment (or .env).
Cost: one structured-output call per run (~$0.001 with gpt-5.4-mini).
"""
from __future__ import annotations

import os

import pytest

from eff.scorer import DEFAULT_DIMENSIONS_PATH, score_story


@pytest.mark.integration
def test_real_openai_scoring_returns_well_formed_response():
    """Verifies the full scoring pipeline against a real LLM call.

    Validates that the configured model accepts our structured-output schema
    and that every field of `ScoreResponse` is populated correctly.
    """
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set — skipping real OpenAI call")

    result = score_story(
        content="As a user, I want personalized recommendations so I can find relevant content.",
        dimensions_path=str(DEFAULT_DIMENSIONS_PATH),
    )

    assert set(result.keys()) >= {
        "content",
        "model",
        "results",
        "summary",
        "enhanced_story",
        "acceptance_criteria",
    }

    for dim in ("utility", "fairness", "privacy", "explainability", "safety"):
        score = result["results"][dim]
        assert score["result"] in ("pass", "Needs Improvement", "fail")
        assert 0.0 <= score["confidence"] <= 1.0
        assert score["reason"].strip()

    summary = result["summary"]
    assert summary["passed"] + summary["needs_improvement"] + summary["failed"] == 5

    assert result["enhanced_story"].strip()
    assert isinstance(result["acceptance_criteria"], list)
