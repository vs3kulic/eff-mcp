# -*- coding: utf-8 -*-
"""Tests for severity tiers — optional user-provided application context."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from eff.scorer import (
    AcceptanceCriterion,
    DimensionScore,
    EFFOutput,
    build_messages,
    call_model,
    load_dimensions,
)

STORY = "As a user I want personalised recommendations so I can find relevant content."
DIMENSIONS_PATH = (
    Path(__file__).resolve().parent.parent / "eff" / "resources" / "dimensions.json"
)


@pytest.fixture(scope="module")
def dimensions():
    return load_dimensions(str(DIMENSIONS_PATH))


def _make_score(result: str = "pass", severity: str | None = None) -> DimensionScore:
    return DimensionScore(
        result=result,
        confidence=0.9,
        reason="Test reason.",
        severity=severity,
    )


# --- prompt construction ---

def test_build_messages_omits_severity_when_no_context(dimensions):
    messages = build_messages(STORY, dimensions, severity_context=None)
    user_prompt = messages[1]["content"]
    assert "APPLICATION CONTEXT" not in user_prompt
    assert "Set 'severity' to null for every dimension" in user_prompt


def test_build_messages_includes_severity_when_context_given(dimensions):
    messages = build_messages(
        STORY, dimensions, severity_context="patient-facing health app"
    )
    user_prompt = messages[1]["content"]
    assert "APPLICATION CONTEXT" in user_prompt
    assert "patient-facing health app" in user_prompt
    assert "'low'" in user_prompt and "'high'" in user_prompt


# --- DimensionScore field ---

def test_dimension_score_severity_optional():
    s = DimensionScore(result="pass", confidence=0.9, reason="ok")
    assert s.severity is None


def test_dimension_score_severity_accepts_levels():
    for level in ("low", "medium", "high"):
        s = DimensionScore(
            result="fail", confidence=0.9, reason="bad", severity=level
        )
        assert s.severity == level


def test_dimension_score_rejects_invalid_severity():
    with pytest.raises(Exception):
        DimensionScore(
            result="fail", confidence=0.9, reason="bad", severity="critical"
        )


# --- call_model end-to-end with severity ---

def test_call_model_passes_severity_through(dimensions):
    fake_parsed = EFFOutput(
        utility=_make_score("pass"),
        fairness=_make_score("Needs Improvement", severity="medium"),
        privacy=_make_score("fail", severity="high"),
        explainability=_make_score("pass"),
        safety=_make_score("pass"),
        enhanced_story=STORY,
        acceptance_criteria=[
            AcceptanceCriterion(dimension="privacy", criterion="x"),
        ],
    )

    with patch("eff.scorer.build_client") as mock_build:
        client = MagicMock()
        response = MagicMock()
        response.output_parsed = fake_parsed
        client.responses.parse.return_value = response
        mock_build.return_value = client

        result = call_model(
            STORY, dimensions, severity_context="patient-facing health app"
        )

    assert result.results.privacy.severity == "high"
    assert result.results.fairness.severity == "medium"
    assert result.results.utility.severity is None
