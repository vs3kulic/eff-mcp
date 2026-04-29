# EFF MCP Server — Project TODO

## Phase 1 — Framework Design (Product Work)

- [x] Define final list of EFF dimensions (confirm: Utility, Fairness, Privacy, Explainability, Safety)
- [x] Write rubric per dimension — what is a PASS, FAIL, borderline?
- [ ] Define severity tiers — same dimension, different weight per context (e.g. health data vs. chat)
- [ ] Write trigger conditions — when should EFF be invoked by an agent?
- [x] Document the harm clause format — exact template syntax agents must follow
- [x] Write 3–5 example transformations (baseline → EFF-enhanced User Story)

_Output: `resources/dimensions.json`, `resources/examples.md`, `resources/SKILL.md` (first draft)_

---

## Phase 2 — SKILL.md (Agent Routing Instructions)

- [ ] Write `SKILL.md` — the routing document agents read to know when and how to invoke EFF
- [ ] Include: trigger conditions, step-by-step invocation instructions, output format
- [ ] Include: what to do if a dimension fails, what to surface to the user
- [ ] Review: does this read like acceptance criteria? It should.

_This is pure product/BA work. No coding required._

---

## Phase 3 — Scorer (Plain Python, No MCP Yet)

- [ ] Create `eff_mcp/scorer.py`
- [ ] Implement `score_dimension(content, dimension, rubric)` as a standalone function
- [ ] Use OpenAI client (or compatible) — model configurable via env var
- [ ] Return structured JSON: `{ "pass": bool, "confidence": float, "reason": string }`
- [ ] Test scorer in isolation with `python scorer.py` — no MCP involved yet
- [ ] Iterate on prompts until scoring feels consistent and defensible
- [ ] Handle errors gracefully (API timeout, malformed response, missing key)

_Output: working `scorer.py` you can test with `python` directly_

---

## Phase 4 — MCP Server (Wrap the Scorer)

- [ ] Create `eff_mcp/server.py` using FastMCP
- [ ] Load `dimensions.json` at startup
- [ ] Expose `ethics_filter(content, dimensions)` as an MCP tool
- [ ] Expose `eff://dimensions` as an MCP resource
- [ ] Expose `eff://skill` as an MCP resource (serves `SKILL.md`)
- [ ] Expose `eff://examples` as an MCP resource (serves `examples.md`)
- [ ] Test: run server locally via `python -m eff_mcp.server`
- [ ] Test: connect to Claude Desktop or another MCP host via stdio config

_Output: working local MCP server, testable in a real agent environment_

---

## Phase 5 — Configuration and Packaging

- [ ] All config via environment variables:
  - `OPENAI_API_KEY` (required)
  - `OPENAI_MODEL` (optional, default: `gpt-4o-mini`)
  - `OPENAI_BASE_URL` (optional, for compatible providers)
- [ ] Write `pyproject.toml` — package name, entrypoint, dependencies
- [ ] Write `server.json` — MCP registry manifest with namespace `io.github.yourusername/eff-mcp`
- [ ] Confirm entrypoint: `python -m eff_mcp.server` works after `pip install -e .`
- [ ] Add `.env.example` file documenting required env vars

---

## Phase 6 — Quality and Robustness

- [ ] Write at least one test per dimension in `tests/`
- [ ] Test edge cases: empty story, missing rubric key, API failure
- [ ] Confirm scorer returns valid JSON even when model output is malformed
- [ ] Confirm server starts cleanly with missing optional env vars
- [ ] Confirm server fails clearly with missing required env vars (not silently)

---

## Phase 7 — Documentation Finalization

- [ ] Update README Quickstart with final package name and exact commands
- [ ] Fix research citation — verify author name and year before publishing
- [ ] Add `CONTRIBUTING.md` if open to external contributions
- [ ] Add `LICENSE` file
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

- [ ] Support additional model providers (Anthropic, Azure OpenAI, Ollama)
- [ ] Add remote HTTP transport (Streamable HTTP) for hosted deployment
- [ ] Consider BYOK pass-through pattern for multi-tenant use
- [ ] Extend dimensions — allow custom rubrics via config
- [ ] Add audit log output (structured JSON per invocation)
