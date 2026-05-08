# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-05-08

### Added

- **`get_skill_instructions` MCP tool** — exposes `eff://skill` as a callable
  tool so MCP hosts that never issue `resources/read` (e.g. Claude Desktop)
  can still retrieve the EFF system-prompt block in a regular tool call.
- **`get_dimensions_rubric` MCP tool** — exposes `eff://dimensions` as a tool,
  returning the full rubric JSON on demand.
- **`get_examples` MCP tool** — exposes `eff://examples` as a tool, returning
  worked transformations and templates on demand.
- **Python 3.13 CI support** — GitHub Actions matrix extended to
  `["3.11", "3.12", "3.13"]`.

### Changed

- internal resource handler renamed from `get_examples` to `get_examples_resource`
  to avoid a name collision with the new `get_examples` tool.

---

## [0.1.0] — 2026-05-08

First public release of the EFF MCP server.

### Added

- **`ethics_filter` MCP tool** — single-call refinement that returns per-dimension
  scores, an enhanced user story with a synthesized harm clause, and measurable
  acceptance criteria.
- **`list_resources` MCP tool** — lists the URIs and descriptions of available
  EFF resources.
- **MCP resources** — `eff://dimensions` (rubric JSON), `eff://skill`
  (system-prompt block for agents), `eff://examples` (worked transformations).
- **Provider seam** ([eff/providers.py](eff/providers.py)) — `LLMProvider`
  Protocol and `OpenAIProvider` implementation. Other providers (Anthropic,
  Gemini, Azure, Ollama) plug in via a single branch in `get_provider()`.
- **Retrieval seam** ([eff/retrieval.py](eff/retrieval.py)) — `Retriever`
  Protocol with `NullRetriever` (default, no RAG) and `SupabaseRetriever`
  (pgvector + OpenAI embeddings).
- **Optional RAG over source literature** — when `EFF_RETRIEVAL_PROVIDER=supabase`
  is set, retrieved passages are injected into the scoring prompt and the LLM
  is instructed to cite them. Each response includes a `sources` array with
  snippets so citation markers (`[1]`, `[5]`, …) are traceable.
- **PDF indexing script** ([scripts/index_papers.py](scripts/index_papers.py)) —
  extracts, chunks, embeds, and inserts a folder of PDFs into the Supabase
  `documents` table. Reads credentials from `.env`.
- **Console script** — `eff-mcp` registered via `pyproject.toml` for direct
  invocation by MCP hosts.
- **Tests** — 38 hermetic unit tests (no network) and 2 opt-in integration
  tests (`pytest -m integration`) against real OpenAI and Supabase.
- **CI** — GitHub Actions runs the unit suite on Python 3.11 and 3.12 for every
  push and pull request.
- **Documentation** — README covers quickstart, MCP host configuration, local
  development with the FastMCP inspector and `.mcp.json`, RAG setup with the
  Supabase schema and RLS policy guidance, and downstream code generation.

### Server hardening

- 30-second timeout on the OpenAI client.
- Structured error responses (`{"error": ..., "detail": ...}`) for
  configuration and runtime failures, instead of bubbling raw exceptions to
  the MCP host.
- Logging on stderr (stdout is the MCP transport — must remain clean).

### Notes

- Default model is `gpt-5.4-mini`. Override with `OPENAI_MODEL` environment
  variable.
- For OpenAI-compatible endpoints (Azure OpenAI, local proxies), set
  `OPENAI_BASE_URL`.
- `supabase` is bundled as a core dependency. Install the optional
  `[indexing]` extra (`pip install -e '.[indexing]'`) to use the PDF indexing
  script.

[0.2.0]: https://github.com/vs3kulic/eff-mcp/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/vs3kulic/eff-mcp/releases/tag/v0.1.0