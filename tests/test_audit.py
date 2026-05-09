# -*- coding: utf-8 -*-
"""Tests for eff.audit — append-only invocation log."""
from __future__ import annotations

import json

import pytest

from eff.audit import ENV_VAR, log_invocation


def test_no_op_when_env_var_unset(monkeypatch, tmp_path):
    monkeypatch.delenv(ENV_VAR, raising=False)
    log_invocation({"content": "test"})
    assert list(tmp_path.iterdir()) == []


def test_writes_jsonl_when_env_var_set(monkeypatch, tmp_path):
    log_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv(ENV_VAR, str(log_path))

    log_invocation({"content": "first"})
    log_invocation({"content": "second"})

    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2

    first = json.loads(lines[0])
    assert first["content"] == "first"
    assert "timestamp_utc" in first
    assert first["timestamp_utc"].endswith("+00:00")


def test_creates_parent_directory(monkeypatch, tmp_path):
    log_path = tmp_path / "logs" / "audit.jsonl"
    monkeypatch.setenv(ENV_VAR, str(log_path))

    log_invocation({"content": "test"})

    assert log_path.exists()


def test_failure_does_not_propagate(monkeypatch, tmp_path):
    """Pointing at a path that cannot be written must not crash the caller."""
    blocker = tmp_path / "blocker"
    blocker.write_text("not-a-directory")
    log_path = blocker / "audit.jsonl"
    monkeypatch.setenv(ENV_VAR, str(log_path))

    log_invocation({"content": "test"})


def test_record_preserves_payload_fields(monkeypatch, tmp_path):
    log_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv(ENV_VAR, str(log_path))

    payload = {
        "content": "story text",
        "model": "gpt-5.4-mini",
        "summary": {"passed": 3, "needs_improvement": 2, "failed": 0},
    }
    log_invocation(payload)

    record = json.loads(log_path.read_text(encoding="utf-8"))
    assert record["content"] == "story text"
    assert record["model"] == "gpt-5.4-mini"
    assert record["summary"]["passed"] == 3
