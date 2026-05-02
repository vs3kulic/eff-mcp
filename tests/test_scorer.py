# -*- coding: utf-8 -*-
"""Tests for eff.scorer — unit tests with mocked OpenAI responses."""

from __future__ import annotations
import json
import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from eff.scorer import (
    DimensionScore,
    ScoreResults,
    ScoreSummary,
    ScoreResponse,
    build_messages,
    load_dimensions,
    call_model,
    score_story,
)

DIMENSIONS_PATH = Path(__file__).resolve().parent.parent / "resources" / "dimensions.json"

STORY = "As a user I want personalised recommendations so I can find relevant content."

############
# FIXTURES #
############

@pytest.fixture(scope="session")
def dimensions():
    return load_dimensions(DIMENSIONS_PATH)


@pytest.fixture
def all_pass_results():
    def make_score(result: str) -> DimensionScore:
        return DimensionScore(result=result, confidence=0.9, reason="Test reason.")
    return ScoreResults(**{dim: make_score("pass") for dim in ("utility", "fairness", "privacy", "explainability", "safety")})


@pytest.fixture
def mock_client(all_pass_results):
    with patch("eff.scorer.build_client") as mock_build:
        client = MagicMock()
        response = MagicMock()
        response.output_parsed = all_pass_results
        client.responses.parse.return_value = response
        mock_build.return_value = client
        yield client


##############
# TEST CASES #
##############

def make_score(result: str) -> DimensionScore:
    return DimensionScore(result=result, confidence=0.9, reason="Test reason.")


def make_results(**overrides) -> ScoreResults:
    defaults = {dim: make_score("pass") for dim in ("utility", "fairness", "privacy", "explainability", "safety")}
    defaults.update(overrides)
    return ScoreResults(**defaults)


def mock_response(results: ScoreResults) -> MagicMock:
    response = MagicMock()
    response.output_parsed = results
    return response


# --- load_dimensions ---

def test_load_dimensions_returns_all_five(dimensions):
    assert set(dimensions.keys()) == {"utility", "fairness", "privacy", "explainability", "safety"}


def test_load_dimensions_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_dimensions("/nonexistent/path/dimensions.json")


def test_load_dimensions_missing_key_raises(tmp_path):
    bad = tmp_path / "dimensions.json"
    bad.write_text(json.dumps({"dimensions": {"utility": {}, "fairness": {}}}))
    with pytest.raises(ValueError, match="missing required dimensions"):
        load_dimensions(str(bad))


# --- build_messages ---

def test_build_messages_returns_system_and_user(dimensions):
    messages = build_messages(STORY, dimensions)
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"


def test_build_messages_includes_content(dimensions):
    messages = build_messages(STORY, dimensions)
    assert STORY in messages[1]["content"]


# --- Per-dimension scoring (mocked) ---

@pytest.mark.parametrize("dimension", ["utility", "fairness", "privacy", "explainability", "safety"])
def test_dimension_pass(dimension, dimensions, mock_client):
    response = call_model(STORY, dimensions)
    score = getattr(response.results, dimension)
    assert score.result == "pass"
    assert 0.0 <= score.confidence <= 1.0
    assert score.reason


@pytest.mark.parametrize("dimension", ["utility", "fairness", "privacy", "explainability", "safety"])
def test_dimension_fail(dimension, dimensions):
    results = make_results(**{dimension: make_score("fail")})
    with patch("eff.scorer.build_client") as mock_build:
        client = MagicMock()
        client.responses.parse.return_value = mock_response(results)
        mock_build.return_value = client

        response = call_model(STORY, dimensions)

    score = getattr(response.results, dimension)
    assert score.result == "fail"


@pytest.mark.parametrize("dimension", ["utility", "fairness", "privacy", "explainability", "safety"])
def test_dimension_needs_improvement(dimension, dimensions):
    results = make_results(**{dimension: make_score("Needs Improvement")})
    with patch("eff.scorer.build_client") as mock_build:
        client = MagicMock()
        client.responses.parse.return_value = mock_response(results)
        mock_build.return_value = client

        response = call_model(STORY, dimensions)

    score = getattr(response.results, dimension)
    assert score.result == "Needs Improvement"


# --- Summary counts ---

def test_summary_counts_all_pass(dimensions, mock_client):
    response = call_model(STORY, dimensions)
    assert response.summary.passed == 5
    assert response.summary.needs_improvement == 0
    assert response.summary.failed == 0


def test_summary_counts_mixed(dimensions):
    results = make_results(
        privacy=make_score("fail"),
        safety=make_score("Needs Improvement"),
    )
    with patch("eff.scorer.build_client") as mock_build:
        client = MagicMock()
        client.responses.parse.return_value = mock_response(results)
        mock_build.return_value = client

        response = call_model(STORY, dimensions)

    assert response.summary.passed == 3
    assert response.summary.needs_improvement == 1
    assert response.summary.failed == 1


# --- Edge cases ---

def test_call_model_raises_on_no_parsed_output(dimensions):
    with patch("eff.scorer.build_client") as mock_build:
        client = MagicMock()
        response = MagicMock()
        response.output_parsed = None
        client.responses.parse.return_value = response
        mock_build.return_value = client

        with pytest.raises(ValueError, match="no parsed structured output"):
            call_model(STORY, dimensions)


def test_build_client_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from eff.scorer import build_client
    with pytest.raises(EnvironmentError, match="OPENAI_API_KEY"):
        build_client()
