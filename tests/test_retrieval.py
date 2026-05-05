# -*- coding: utf-8 -*-
"""Tests for eff.retrieval — the RAG seam."""
import pytest

from eff.retrieval import (
    NullRetriever,
    RetrievedChunk,
    get_retriever,
)


def test_null_retriever_returns_empty():
    r = NullRetriever()
    assert r.retrieve("anything") == []
    assert r.retrieve("anything", k=10) == []


def test_get_retriever_default_is_null(monkeypatch):
    monkeypatch.delenv("EFF_RETRIEVAL_PROVIDER", raising=False)
    assert isinstance(get_retriever(), NullRetriever)


def test_get_retriever_explicit_none(monkeypatch):
    monkeypatch.setenv("EFF_RETRIEVAL_PROVIDER", "none")
    assert isinstance(get_retriever(), NullRetriever)


def test_get_retriever_unknown_provider_falls_back_to_null(monkeypatch):
    monkeypatch.setenv("EFF_RETRIEVAL_PROVIDER", "pinecone")
    assert isinstance(get_retriever(), NullRetriever)


def test_retrieved_chunk_validates():
    chunk = RetrievedChunk(text="hello", source="paper.pdf", score=0.9)
    assert chunk.text == "hello"
    assert chunk.source == "paper.pdf"
    assert chunk.score == 0.9


def test_retrieved_chunk_rejects_invalid():
    with pytest.raises(Exception):
        RetrievedChunk(text="hello", source="paper.pdf", score="not-a-float")


def test_supabase_retriever_without_creds_raises(monkeypatch):
    """With provider=supabase but missing creds: raises ImportError if supabase not
    installed, EnvironmentError if it is. Either is the right behavior."""
    monkeypatch.setenv("EFF_RETRIEVAL_PROVIDER", "supabase")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    with pytest.raises((EnvironmentError, ImportError)):
        get_retriever()
