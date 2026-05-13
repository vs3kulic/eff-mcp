# -*- coding: utf-8 -*-
"""Combined-feature test — RAG + Custom Dimensions + Severity active together.

Each of the three features has its own focused test file. This file checks the
seam between them: that activating all three at once produces a coherent
response (citations land in `sources`, custom dimension is scored, severity
is set on both built-in and custom dimensions, summary counts include both).
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from eff.retrieval import RetrievedChunk
from eff.scorer import (
    AcceptanceCriterion,
    DimensionScore,
    call_model,
    load_dimensions,
    build_eff_output_class,
)

DIMENSIONS_PATH = (
    Path(__file__).resolve().parent.parent / "eff" / "resources" / "dimensions.json"
)


class _StubRetriever:
    """Returns a fixed list of chunks; mimics SupabaseRetriever interface."""

    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        self._chunks = chunks

    def retrieve(self, query: str, k: int = 5) -> list[RetrievedChunk]:
        return self._chunks


def test_rag_custom_severity_combined(monkeypatch):
    chunks = [
        RetrievedChunk(
            text="Health data must be processed under purpose limitation.",
            source="ieee_7000.pdf",
            score=0.81,
        ),
        RetrievedChunk(
            text="Patient consent must be informed and revocable.",
            source="hipaa_overview.pdf",
            score=0.74,
        ),
    ]
    # Override the conftest autouse fixture for this test only.
    monkeypatch.setattr("eff.scorer.get_retriever", lambda: _StubRetriever(chunks))

    dimensions = load_dimensions(str(DIMENSIONS_PATH))
    extras = {
        "clinical_safety": {
            "description": "Whether the feature can trigger or worsen clinical harm.",
            "rubric": {
                "pass": "Mechanisms are in place to detect and mitigate clinical risk.",
                "fail": "The feature can plausibly trigger clinical harm with no safeguards.",
                "borderline": "Risks are acknowledged but mitigation is partial or untested.",
            },
            "scoring_notes": ["Consider acute and chronic harm pathways."],
        }
    }

    output_cls = build_eff_output_class(["clinical_safety"])
    fake_parsed = output_cls(
        utility=DimensionScore(
            result="pass", confidence=0.9, reason="Direct benefit.", severity=None
        ),
        fairness=DimensionScore(
            result="pass", confidence=0.85, reason="Equitable across groups.", severity=None
        ),
        privacy=DimensionScore(
            result="fail",
            confidence=0.95,
            reason="Health data retention not specified [1].",
            severity="high",
        ),
        explainability=DimensionScore(
            result="Needs Improvement",
            confidence=0.8,
            reason="Patient cannot see who accessed their data [2].",
            severity="medium",
        ),
        safety=DimensionScore(
            result="pass", confidence=0.87, reason="No direct safety risk.", severity=None
        ),
        clinical_safety=DimensionScore(
            result="Needs Improvement",
            confidence=0.82,
            reason="No mechanism to flag urgent symptoms before session.",
            severity="medium",
        ),
        enhanced_story=(
            "As a patient, I want to share my diagnosis with my therapist, "
            "without unclear data retention or missing safeguards for urgent symptoms."
        ),
        acceptance_criteria=[
            AcceptanceCriterion(dimension="privacy", criterion="Retention is bounded and disclosed."),
            AcceptanceCriterion(dimension="clinical_safety", criterion="Urgent-symptom flag before share."),
        ],
    )

    with patch("eff.scorer.build_client") as mock_build:
        client = MagicMock()
        response = MagicMock()
        response.output_parsed = fake_parsed
        client.responses.parse.return_value = response
        mock_build.return_value = client

        result = call_model(
            content="As a patient, I want to share my diagnosis with my therapist.",
            dimensions=dimensions,
            extra_dimensions=extras,
            severity_context="patient-facing health app handling diagnostic data",
        )

    # RAG: retrieved chunks land in `sources` with snippets, source filenames, scores.
    assert len(result.sources) == 2
    assert result.sources[0].source == "ieee_7000.pdf"
    assert result.sources[1].source == "hipaa_overview.pdf"
    assert result.sources[0].snippet
    assert 0.0 <= result.sources[0].score <= 1.0

    # Custom dimensions: clinical_safety appears in custom_results, NOT in results.
    assert "clinical_safety" in result.custom_results
    assert result.custom_results["clinical_safety"].result == "Needs Improvement"

    # Severity: set on both built-in and custom dimensions.
    assert result.results.privacy.severity == "high"
    assert result.results.utility.severity is None
    assert result.custom_results["clinical_safety"].severity == "medium"

    # Summary counts include both built-in and custom dimensions.
    assert result.summary.passed == 3
    assert result.summary.needs_improvement == 2
    assert result.summary.failed == 1
