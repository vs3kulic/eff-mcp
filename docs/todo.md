# EFF MCP Server — Project TODO

## Phase 1 — Framework Design (Product Work)

- [x] Define final list of EFF dimensions (confirm: Utility, Fairness, Privacy, Explainability, Safety)
- [x] Write rubric per dimension — what is a PASS, FAIL, borderline?
- [x] Write trigger conditions — when should EFF be invoked by an agent?
- [x] Document the harm clause format — exact template syntax agents must follow
- [x] Write 3–5 example transformations (baseline → EFF-enhanced User Story)

_Output: `eff/resources/dimensions.json`, `eff/resources/examples.md`, `eff/resources/SKILL.md`_

---

## Phase 2 — SKILL.md (Agent Routing Instructions)

- [x] Write `SKILL.md` — the routing document agents read to know when and how to invoke EFF
- [x] Include: trigger conditions, step-by-step invocation instructions, output format
- [x] Include: what to do if a dimension fails, what to surface to the user
- [x] Review: does this read like acceptance criteria? It should.

_This is pure product/BA work. No coding required._

---

## Phase 3 — Scorer (Plain Python, No MCP Yet)

- [x] Create `eff/scorer.py`
- [x] Implement `score_story(content, dimensions_path, model)` as a standalone function
- [x] Use OpenAI client (or compatible) — model configurable via `OPENAI_MODEL` env var
- [x] Return structured output via Pydantic: `DimensionScore` with `result`, `confidence`, `reason` per dimension
- [x] Test scorer in isolation with `python -m eff.scorer "story text"` — no MCP involved
- [x] Iterate on prompts until scoring feels consistent and defensible
- [x] Handle errors gracefully (API timeout 30s, malformed response, missing key)

_Output: working `eff/scorer.py` you can test with `python` directly_

---

## Phase 4 — MCP Server (Wrap the Scorer)

- [x] Create `eff/server.py` using FastMCP
- [x] Load `dimensions.json` per call via `score_story()`
- [x] Expose `ethics_filter(user_story)` as an MCP tool (returns scores + enhanced story + acceptance criteria)
- [x] Expose `eff://dimensions` as an MCP resource
- [x] Expose `eff://skill` as an MCP resource (serves `SKILL.md`)
- [x] Expose `eff://examples` as an MCP resource (serves `examples.md`)
- [x] Test: run server locally via `python -m eff.server`
- [x] Test: connect to Claude Desktop or another MCP host via stdio config

_Output: working local MCP server, testable in a real agent environment_

---

## Phase 5 — Configuration and Packaging

- [x] Config via environment variables:
  - `OPENAI_API_KEY` (required)
  - `OPENAI_MODEL` (optional, default: `gpt-5.4-mini`)
  - `OPENAI_BASE_URL` (optional, for Azure / local providers)
  - `EFF_RETRIEVAL_PROVIDER` (optional, `none` or `supabase`)
  - `SUPABASE_URL`, `SUPABASE_KEY` (required if using supabase retriever)
- [x] Write `pyproject.toml` — package name, entrypoint, dependencies, optional `[rag]` and `[dev]` extras
- [x] Write `server.json` — MCP registry manifest with namespace `io.github.vajosekulic/eff-mcp`
- [x] Confirm entrypoint: `eff-mcp` console script works after `pip install -e .`

---

## Phase 6 — Quality and Robustness

- [ ] Write at least one test per dimension edge case in `tests/` (e.g. empty story, story that clearly passes all)
- [ ] Test edge cases: empty story, missing rubric key, API failure (mock provider raising exception)
- [ ] Confirm server starts cleanly with missing optional env vars
- [x] Confirm server fails clearly with missing required env vars (not silently) — `EnvironmentError` raised, logged, returned as structured `{"error": ...}`

---

## Phase 7 — Documentation Finalization

- [x] Update README Quickstart with final package name and exact commands
- [ ] Fix research citation — verify author names and year before publishing
- [ ] Add `CONTRIBUTING.md` if open to external contributions
- [x] Add `LICENSE` file
- [ ] Add `CHANGELOG.md` (start with `v0.1.0`)

---

## Phase 8 — Publish

- [ ] Publish package to PyPI (`pip install eff-mcp`)
- [ ] Tag release `v0.1.0` on GitHub
- [ ] Submit `server.json` to official MCP Registry via `mcp-publisher` CLI
- [ ] Wait for Glama auto-index (3–7 days)
- [ ] Submit manually to PulseMCP (`hello@pulsemcp.com`)
- [ ] Submit manually to MCP.so

---

## Deferred / v2

- [ ] Define severity tiers — same dimension, different weight per context (e.g. health data vs. chat)
- [ ] Support additional model providers (Anthropic, Azure OpenAI, Ollama) — seam already built in `eff/providers.py`
- [ ] Add remote HTTP transport (Streamable HTTP) for hosted deployment
- [ ] Consider BYOK pass-through pattern for multi-tenant use
- [ ] Extend dimensions — allow custom rubrics via config
- [ ] Add audit log output (structured JSON per invocation)
