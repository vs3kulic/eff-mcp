# -*- coding: utf-8 -*-
"""LLM provider wrappers for EFF.

This module is the seam for multi-provider support. The LLMProvider Protocol
defines the contract; OpenAIProvider is the only current implementation.

Adding a new provider (e.g. Anthropic, Gemini, Ollama):
  1. Implement a class with `model: str` and `parse_structured(messages, schema) -> BaseModel`
  2. Add a branch in `get_provider()` keyed on an env var (e.g. EFF_LLM_PROVIDER)
"""
from __future__ import annotations

import json
import os
from typing import Protocol, Type, TypeVar

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

T = TypeVar("T", bound=BaseModel)

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
DEFAULT_BASE_URL = os.getenv("OPENAI_BASE_URL")


# Local development: load OPENAI_API_KEY from a JSON file if EFF_SECRET_PATH is set
_secrets_path = os.getenv("EFF_SECRET_PATH")
if _secrets_path and os.path.exists(_secrets_path):
    with open(_secrets_path, "r", encoding="utf-8") as f:
        _secrets = json.load(f)
    if "OPENAI_API_KEY" in _secrets:
        os.environ["OPENAI_API_KEY"] = _secrets["OPENAI_API_KEY"]


class LLMProvider(Protocol):
    """Provider seam — anything implementing this can plug into the scorer."""

    model: str

    def parse_structured(self, messages: list[dict], schema: Type[T]) -> T: ...


class OpenAIProvider:
    """OpenAI Responses API with pydantic-typed structured outputs."""

    def __init__(self, model: str | None = None) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY is not set.")

        kwargs: dict = {"api_key": api_key, "timeout": 30.0}
        if DEFAULT_BASE_URL:
            kwargs["base_url"] = DEFAULT_BASE_URL

        self._client = OpenAI(**kwargs)
        self.model = model or DEFAULT_MODEL

    def parse_structured(self, messages: list[dict], schema: Type[T]) -> T:
        response = self._client.responses.parse(
            model=self.model,
            input=messages,
            text_format=schema,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("Model returned no parsed structured output.")
        return parsed


def get_provider(model: str | None = None) -> LLMProvider:
    """Return the configured LLM provider.

    Currently always returns OpenAIProvider. Future: route on EFF_LLM_PROVIDER.
    """
    return OpenAIProvider(model=model)
