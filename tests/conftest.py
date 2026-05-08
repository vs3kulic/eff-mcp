# -*- coding: utf-8 -*-
"""Global test configuration — keeps the suite hermetic.

The unit tests in this package must run without API keys, network, or Supabase.
This file enforces that:
  - `eff.scorer.get_retriever` is forced to return a NullRetriever, so tests
    cannot accidentally hit Supabase even if `.env` has EFF_RETRIEVAL_PROVIDER
    set in the developer's environment.
  - Tests that need real services should live in a separate `tests/integration/`
    directory and bypass this fixture.
"""
from __future__ import annotations

import pytest

from eff.retrieval import NullRetriever


@pytest.fixture(autouse=True)
def _force_null_retriever(monkeypatch, request):
    """Force NullRetriever for unit tests — never reach external services.

    Integration tests (marked with @pytest.mark.integration) opt out of this
    so they can hit real Supabase / OpenAI.
    """
    if request.node.get_closest_marker("integration"):
        return
    monkeypatch.setattr("eff.scorer.get_retriever", lambda: NullRetriever())
