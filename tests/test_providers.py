# -*- coding: utf-8 -*-
"""Tests for eff.providers — the LLM provider seam."""
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from eff.providers import OpenAIProvider, get_provider


class _DummySchema(BaseModel):
    answer: str


def test_openai_provider_without_key_raises(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(EnvironmentError, match="OPENAI_API_KEY"):
        OpenAIProvider()


def test_openai_provider_uses_default_model(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    p = OpenAIProvider()
    assert p.model  # whatever DEFAULT_MODEL is, must be non-empty


def test_openai_provider_accepts_custom_model(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    p = OpenAIProvider(model="gpt-4o-mini")
    assert p.model == "gpt-4o-mini"


def test_parse_structured_returns_parsed(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    p = OpenAIProvider()

    expected = _DummySchema(answer="42")
    fake_response = MagicMock()
    fake_response.output_parsed = expected
    p._client = MagicMock()
    p._client.responses.parse.return_value = fake_response

    result = p.parse_structured([{"role": "user", "content": "hi"}], _DummySchema)
    assert result is expected
    p._client.responses.parse.assert_called_once()
    call_kwargs = p._client.responses.parse.call_args.kwargs
    assert call_kwargs["model"] == p.model
    assert call_kwargs["text_format"] is _DummySchema


def test_parse_structured_raises_on_none(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    p = OpenAIProvider()

    fake_response = MagicMock()
    fake_response.output_parsed = None
    p._client = MagicMock()
    p._client.responses.parse.return_value = fake_response

    with pytest.raises(ValueError, match="no parsed structured output"):
        p.parse_structured([], _DummySchema)


def test_get_provider_returns_openai(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    assert isinstance(get_provider(), OpenAIProvider)


def test_get_provider_passes_model_through(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    p = get_provider(model="custom-model")
    assert p.model == "custom-model"
