# -*- coding: utf-8 -*-
"""End-to-end test against a real Supabase project.

Run with: pytest -m integration tests/integration/test_supabase_e2e.py

Requires:
  - SUPABASE_URL and SUPABASE_KEY in environment (or .env)
  - OPENAI_API_KEY (used to embed the query)
  - The `documents` table and `match_documents` RPC must exist (see README RAG section)

Cost: one embedding call per run (~$0.00002 with text-embedding-3-small).
"""
from __future__ import annotations

import os

import pytest

from eff.retrieval import RetrievedChunk, SupabaseRetriever


@pytest.mark.integration
def test_real_supabase_retrieval_returns_well_formed_chunks():
    """Verifies retrieval works against a live Supabase project.

    Does not assume the corpus is non-empty: if no documents are indexed yet,
    the retriever should still complete cleanly and return an empty list.
    If documents exist, validates the chunk shape.
    """
    for var in ("OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"):
        if not os.getenv(var):
            pytest.skip(f"{var} not set — skipping real Supabase call")

    retriever = SupabaseRetriever()
    chunks = retriever.retrieve("ethical risks in user stories", k=3)

    assert isinstance(chunks, list)
    assert len(chunks) <= 3

    for chunk in chunks:
        assert isinstance(chunk, RetrievedChunk)
        assert chunk.text.strip()
        assert chunk.source.strip()
        assert 0.0 <= chunk.score <= 1.0