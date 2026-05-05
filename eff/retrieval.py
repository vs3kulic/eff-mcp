# -*- coding: utf-8 -*-
"""Retrieval seam for EFF.

The Retriever Protocol defines the contract for plugging in a literature
retrieval backend. NullRetriever is the default no-op (returns no chunks,
prompt is unchanged from the rubric-only version). SupabaseRetriever uses
pgvector + OpenAI embeddings.

Adding a new retriever:
  1. Implement a class with `retrieve(query, k) -> list[RetrievedChunk]`
  2. Add a branch in `get_retriever()` keyed on EFF_RETRIEVAL_PROVIDER
"""
from __future__ import annotations

import os
from typing import Protocol

from openai import OpenAI
from pydantic import BaseModel

DEFAULT_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
DEFAULT_RETRIEVAL_K = int(os.getenv("EFF_RETRIEVAL_K", "5"))


class RetrievedChunk(BaseModel):
    text: str
    source: str
    score: float


class Retriever(Protocol):
    def retrieve(self, query: str, k: int = DEFAULT_RETRIEVAL_K) -> list[RetrievedChunk]: ...


class NullRetriever:
    """No-op retriever. Returned when RAG is not configured — preserves today's behavior."""

    def retrieve(self, query: str, k: int = DEFAULT_RETRIEVAL_K) -> list[RetrievedChunk]:
        return []


class SupabaseRetriever:
    """Supabase pgvector retriever with OpenAI embeddings.

    Expects a Postgres function named `match_documents` (configurable via
    SUPABASE_RPC) that takes (query_embedding vector, match_count int) and
    returns rows with at least: content text, source text, similarity float.

    See README "RAG" section for the SQL schema and RPC definition.
    """

    def __init__(
        self,
        url: str | None = None,
        key: str | None = None,
        rpc_name: str | None = None,
        embedding_model: str | None = None,
    ) -> None:
        try:
            from supabase import create_client
        except ImportError as e:
            raise ImportError(
                "SupabaseRetriever requires the 'supabase' package. "
                "Install with: pip install 'eff-mcp[rag]'"
            ) from e

        url = url or os.getenv("SUPABASE_URL")
        key = key or os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise EnvironmentError("SUPABASE_URL and SUPABASE_KEY must be set.")

        self._client = create_client(url, key)
        base_url = os.getenv("OPENAI_BASE_URL")
        openai_kwargs: dict = {}
        if base_url:
            openai_kwargs["base_url"] = base_url
        self._openai = OpenAI(**openai_kwargs)
        self._rpc_name = rpc_name or os.getenv("SUPABASE_RPC", "match_documents")
        self._embedding_model = embedding_model or DEFAULT_EMBEDDING_MODEL

    def _embed(self, text: str) -> list[float]:
        response = self._openai.embeddings.create(
            input=text,
            model=self._embedding_model,
        )
        return response.data[0].embedding

    def retrieve(self, query: str, k: int = DEFAULT_RETRIEVAL_K) -> list[RetrievedChunk]:
        embedding = self._embed(query)
        response = self._client.rpc(
            self._rpc_name,
            {"query_embedding": embedding, "match_count": k},
        ).execute()

        rows = response.data or []
        return [
            RetrievedChunk(
                text=row.get("content", ""),
                source=row.get("source", "unknown"),
                score=float(row.get("similarity", 0.0)),
            )
            for row in rows
        ]


def get_retriever() -> Retriever:
    """Return the configured retriever.

    EFF_RETRIEVAL_PROVIDER:
      - unset / "none" → NullRetriever (default, no RAG)
      - "supabase"     → SupabaseRetriever
    """
    provider = os.getenv("EFF_RETRIEVAL_PROVIDER", "none").lower()
    if provider == "supabase":
        return SupabaseRetriever()
    return NullRetriever()
