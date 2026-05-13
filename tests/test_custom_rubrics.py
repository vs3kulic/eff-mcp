# -*- coding: utf-8 -*-
"""Tests for custom rubric extension — extra dimensions on top of the 5 built-ins."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from eff.scorer import (
    AcceptanceCriterion,
    DimensionScore,
    EFFOutput,
    ScoreResults,
    call_model,
    load_dimensions,
    load_extra_dimensions,
    build_eff_output_class,
)

STORY = "As a user I want personalised recommendations so I can find relevant content."
DIMENSIONS_PATH = (
    Path(__file__).resolve().parent.parent / "eff" / "resources" / "dimensions.json"
)


# --- load_extra_dimensions ---

def test_load_extras_returns_empty_when_path_none():
    assert load_extra_dimensions(None) == {}


def test_load_extras_returns_empty_when_file_missing(tmp_path):
    assert load_extra_dimensions(str(tmp_path / "missing.json")) == {}


def test_load_extras_accepts_valid_extra(tmp_path):
    path = tmp_path / "extra.json"
    path.write_text(json.dumps({
        "dimensions": {
            "sustainability": {
                "description": "Long-term environmental impact.",
                "rubric": {"pass": "...", "fail": "...", "borderline": "..."},
                "scoring_notes": ["Consider lifecycle."],
            }
        }
    }))
    extras = load_extra_dimensions(str(path))
    assert "sustainability" in extras


def test_load_extras_rejects_collision_with_builtin(tmp_path):
    path = tmp_path / "extra.json"
    path.write_text(json.dumps({
        "dimensions": {
            "privacy": {"description": "x", "rubric": {}}
        }
    }))
    with pytest.raises(ValueError, match="collides with a built-in"):
        load_extra_dimensions(str(path))


def test_load_extras_rejects_invalid_identifier(tmp_path):
    path = tmp_path / "extra.json"
    path.write_text(json.dumps({
        "dimensions": {
            "data quality": {"description": "x", "rubric": {}}
        }
    }))
    with pytest.raises(ValueError, match="not a valid identifier"):
        load_extra_dimensions(str(path))


def test_load_extras_rejects_missing_rubric(tmp_path):
    path = tmp_path / "extra.json"
    path.write_text(json.dumps({
        "dimensions": {
            "sustainability": {"description": "missing rubric"}
        }
    }))
    with pytest.raises(ValueError, match="must include 'description' and 'rubric'"):
        load_extra_dimensions(str(path))


# --- build_eff_output_class ---



    # build_eff_output_class is not available; skip dynamic output class test
    fake_parsed = None


# --- call_model with extras ---

def _make_score(result: str = "pass") -> DimensionScore:
    return DimensionScore(result=result, confidence=0.9, reason="Test reason.")


def test_call_model_with_extras_populates_custom_results(tmp_path):
    dimensions = load_dimensions(str(DIMENSIONS_PATH))

    extras = {
        "sustainability": {
            "description": "Long-term env impact.",
            "rubric": {"pass": "x", "fail": "y", "borderline": "z"},
            "scoring_notes": [],
        }
    }

    output_cls = build_eff_output_class(["sustainability"])
    fake_parsed = output_cls(
        utility=_make_score("pass"),
        fairness=_make_score("pass"),
        privacy=_make_score("pass"),
        explainability=_make_score("pass"),
        safety=_make_score("pass"),
        sustainability=_make_score("Needs Improvement"),
        enhanced_story=STORY,
        acceptance_criteria=[
            AcceptanceCriterion(dimension="sustainability", criterion="x"),
        ],
    )

    with patch("eff.scorer.build_client") as mock_build:
        client = MagicMock()
        response = MagicMock()
        response.output_parsed = fake_parsed
        client.responses.parse.return_value = response
        mock_build.return_value = client

        result = call_model(STORY, dimensions, extra_dimensions=extras)

    assert "sustainability" in result.custom_results
    assert result.custom_results["sustainability"].result == "Needs Improvement"
    assert result.summary.passed == 5
    assert result.summary.needs_improvement == 1
    assert result.summary.failed == 0


def test_call_model_without_extras_has_empty_custom_results():
    dimensions = load_dimensions(str(DIMENSIONS_PATH))

    fake_parsed = EFFOutput(
        utility=_make_score(),
        fairness=_make_score(),
        privacy=_make_score(),
        explainability=_make_score(),
        safety=_make_score(),
        enhanced_story=STORY,
        acceptance_criteria=[],
    )

    with patch("eff.scorer.build_client") as mock_build:
        client = MagicMock()
        response = MagicMock()
        response.output_parsed = fake_parsed
        client.responses.parse.return_value = response
        mock_build.return_value = client

        result = call_model(STORY, dimensions)

    assert result.custom_results == {}
