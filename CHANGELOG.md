# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] — 2026-05-09

### Added

- **Audit logging** ([eff/audit.py](eff/audit.py)) — when `EFF_AUDIT_LOG_PATH`
  is set, every successful `ethics_filter` call appends a JSONL row capturing
  the original story, the model used, all per-dimension scores, the enhanced
  story, the acceptance criteria, the retrieved sources, and a UTC timestamp.
  Disabled by default; failures are logged to stderr but never propagate to the
  MCP host.
- **Custom dimensions** — new `EFF_EXTRA_DIMENSIONS_PATH` env variable lets
  teams extend the 5 built-in EFF dimensions with domain-specific ones (e.g.
  `sustainability`, `accessibility`, `regulatory_compliance`). Extras are scored
  alongside the built-ins and appear under `custom_results` in the response. The
  5 built-ins cannot be replaced. Includes validation against name collisions
  and invalid identifiers.
- **Severity tiers** — `ethics_filter` now accepts an optional `context`
  parameter (a short description of the application domain). When provided,
  every `DimensionScore` carries a `severity` field of `low` / `medium` / `high`
  / `null`, weighted to that context. The same Privacy concern can thus be
  high-severity in a health app and low-severity in a chat app.
- **Example custom-dimensions templates** — [examples/extras/](examples/extras/)
  ships a `sustainability.json` template (sustainability + accessibility) plus a
  README explaining how to copy and adapt it.

### Changed

- `ScoreResponse` gains two fields: `custom_results: dict[str, DimensionScore]`
  and `severity: Literal["low","medium","high"] | None` on every
  `DimensionScore`. Both have safe defaults — existing consumers see no
  behaviour change unless they opt in.
- README quickstart reordered: `uvx eff-mcp` is now the recommended path, source
  install is the contributor path. The PyPI badge links to the live release.

---

## [0.2.1] — 2026-05-09

### Fixed

- Indexing script (`scripts/index_papers.py`) now reads the embedding model from
  `OPENAI_EMBEDDING_MODEL` (env) or `--embedding-model` (CLI), instead of
  hardcoding `text-embedding-3-small`. The retrieval side already supported this
  — without the fix, overriding the model on the server would silently break
  retrieval because indexing and retrieval used different embedding spaces.

---

## [0.2.0] — 2026-05-08

### Added

- **`get_skill_instructions` MCP tool** — exposes `eff://skill` as a callable
  tool so MCP hosts that never issue `resources/read` (e.g. Claude Desktop) can
  still retrieve the EFF system-prompt block in a regular tool call.
- **`get_dimensions_rubric` MCP tool** — exposes `eff://dimensions` as a tool,
  returning the full rubric JSON on demand.
- **`get_examples` MCP tool** — exposes `eff://examples` as a tool, returning
  worked transformations and templates on demand.
- **Python 3.13 CI support** — GitHub Actions matrix extended to
  `["3.11", "3.12", "3.13"]`.
- **Retrieval seam** ([eff/retrieval.py](eff/retrieval.py)) — `Retriever`
  Protocol with `NullRetriever` (default, no RAG) and `SupabaseRetriever`
  (pgvector + OpenAI embeddings).
- **Optional RAG over source literature** — when
  `EFF_RETRIEVAL_PROVIDER=supabase` is set, retrieved passages are injected into
  the scoring prompt and the LLM is instructed to cite them. Each response
  includes a `sources` array with snippets so citation markers (`[1]`, `[5]`, …)
  are traceable.
- **PDF indexing script** ([scripts/index_papers.py](scripts/index_papers.py)) —
  extracts, chunks, embeds, and inserts a folder of PDFs into the Supabase
  `documents` table. Reads credentials from `.env`.

### Changed

- internal resource handler renamed from `get_examples` to
  `get_examples_resource` to avoid a name collision with the new `get_examples`
  tool.

### Server hardening

- 30-second timeout on the OpenAI client.
- Structured error responses (`{"error": ..., "detail": ...}`) for configuration
  and runtime failures, instead of bubbling raw exceptions to the MCP host.
- Logging on stderr (stdout is the MCP transport — must remain clean).

---

## [0.1.0] — 2026-05-08

First public release of the EFF MCP server.

### Added

- **`ethics_filter` MCP tool** — single-call refinement that returns
  per-dimension scores, an enhanced user story with a synthesized harm clause,
  and measurable acceptance criteria.
- **`list_resources` MCP tool** — lists the URIs and descriptions of available
  EFF resources.
- **MCP resources** — `eff://dimensions` (rubric JSON), `eff://skill`
  (system-prompt block for agents), `eff://examples` (worked transformations).
- **Provider seam** ([eff/providers.py](eff/providers.py)) — `LLMProvider`
  Protocol and `OpenAIProvider` implementation. Other providers (Anthropic,
  Gemini, Azure, Ollama) plug in via a single branch in `get_provider()`.
- **Console script** — `eff-mcp` registered via `pyproject.toml` for direct
  invocation by MCP hosts.
- **Tests** — 38 unit tests (no network) and 2 opt-in integration tests
  (`pytest -m integration`) against real OpenAI and Supabase.
- **CI** — GitHub Actions runs the unit suite on Python 3.11 and 3.12 for every
  push and pull request.
- **Documentation** — README covers quickstart, MCP host configuration, local
  development with the FastMCP inspector and `.mcp.json`, RAG setup with the
  Supabase schema and RLS policy guidance, and downstream code generation.

### Notes

- Default model is `gpt-5.4-mini`. Override with `OPENAI_MODEL` environment
  variable.
- For OpenAI-compatible endpoints (Azure OpenAI, local proxies), set
  `OPENAI_BASE_URL`.
- `supabase` is bundled as a core dependency. Install the optional `[indexing]`
  extra (`pip install -e '.[indexing]'`) to use the PDF indexing script.

[0.3.0]: https://github.com/vs3kulic/eff-mcp/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/vs3kulic/eff-mcp/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/vs3kulic/eff-mcp/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/vs3kulic/eff-mcp/releases/tag/v0.1.0
