[![PyPI](https://img.shields.io/pypi/v/eff-mcp.svg?cacheSeconds=1)](https://pypi.org/project/eff-mcp/)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-blueviolet)
![FastMCP](https://img.shields.io/badge/FastMCP-ready-orange)

# Ethics Filter Framework (EFF) — MCP Capability

This repository packages the Ethics Filter Framework (EFF) as a Model Context
Protocol (MCP) capability for agent-based requirements engineering. It is
designed for integration with agent platforms (e.g., OpenClaw) that support MCP,
enabling automated User Story refinement and ethical risk surfacing during agile
development.

---

## What EFF Does

EFF is a requirements-engineering method grounded in Value-Based Engineering
(ISO/IEC/IEEE 24748-7000:2022). It:

- Identifies stakeholder risks and links them to explicit values
- Rewrites User Stories to include a harm clause
- Generates measurable acceptance criteria for each ethical dimension
- Provides a rubric for consistent, auditable requirements refinement

---

## The Five Dimensions

EFF operationalizes five core ethical dimensions derived from IEEE 7000:

| Dimension          | What it checks                                                                                      |
| ------------------ | --------------------------------------------------------------------------------------------------- |
| **Utility**        | The feature provides meaningful benefit to the intended user                                        |
| **Fairness**       | The feature avoids unjustified discrimination or unequal treatment                                  |
| **Privacy**        | The feature respects confidentiality, data minimization, and purpose limitation                     |
| **Explainability** | The feature communicates relevant reasons, logic, or data practices clearly enough for informed use |
| **Safety**         | The feature avoids harmful, unsafe, or policy-violating outcomes                                    |

---

## Example Transformation

**Baseline User Story:**

> As a user, I want personalized recommendations so that I can find relevant
> content.

**EFF-enhanced User Story:**

> As a user, I want personalized recommendations so that I can find relevant
> content, without causing harm to stakeholders through opaque profiling or
> misuse of personal data.

**Acceptance criteria:**

- **Privacy:** Only fields classified as essential for generating
  recommendations are collected. All data is deleted or anonymized within 90
  days of submission.
- **Explainability:** Before first use, a plain-language notice explains what
  data is collected, for what purpose, and for how long it will be stored.
- **Utility:** At least 80% of users who start the flow complete it. At least
  75% report the recommendations are relevant in a post-interaction survey.

---

## How EFF is Exposed via MCP

This repository exposes EFF as an MCP-compatible capability via the following tools:

| Tool | Description |
| ---- | ----------- |
| `ethics_filter` | Scores a User Story across the five EFF dimensions, returns an enhanced story with a harm clause and measurable acceptance criteria. Requires `OPENAI_API_KEY`. |
| `list_resources` | Lists the URIs and descriptions of available EFF resources. |
| `get_skill_instructions` | Returns the EFF skill instructions and agent workflow (`eff://skill`). |
| `get_dimensions_rubric` | Returns the full EFF rubric and dimension definitions as JSON (`eff://dimensions`). |
| `get_examples` | Returns worked transformation examples and acceptance-criteria templates (`eff://examples`). |

Resources are also exposed under the `eff://` URI scheme (`eff://skill`,
`eff://dimensions`, `eff://examples`) for MCP hosts that support
`resources/read`. The three `get_*` tools above are provided as a fallback for
hosts that call `resources/list` but never `resources/read` (e.g. Claude
Desktop).

---

## Quickstart (for MCP Hosts / Agent Integrators)

> **This server is self-hosted. Each deployment uses its own model provider
> credentials — this repository does not provide hosted inference.**

**Prerequisites:** an OpenAI API key (or an OpenAI-compatible endpoint via
`OPENAI_BASE_URL`). For the recommended install you also need [`uv`](https://docs.astral.sh/uv/getting-started/installation/);
for the from-source install you need Python 3.11+.

### Option A — Run via `uvx` (recommended)

No clone, no virtualenv, no Python toolchain to manage — `uvx` fetches the
package from PyPI and runs the server on demand. Add this to your MCP host
config (Claude Desktop, Claude Code `.mcp.json`, Cursor, OpenClaw, …):

```json
{
  "mcpServers": {
    "eff": {
      "command": "uvx",
      "args": ["eff-mcp"],
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "OPENAI_MODEL": "gpt-5.4-mini"
      }
    }
  }
}
```

Reload your MCP host. First start downloads the package and creates an
isolated environment (~5–10 s); subsequent starts are instant.

### Option B — Install from source (for contributors / hacking on the server)

```bash
git clone https://github.com/vs3kulic/eff-mcp
cd eff-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Then point your MCP host at the local console script:

```json
{
  "mcpServers": {
    "eff": {
      "command": "/absolute/path/to/.venv/bin/eff-mcp",
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "OPENAI_MODEL": "gpt-5.4-mini"
      }
    }
  }
}
```

The `.venv/` folder is gitignored — every developer creates their own.

### Notes on credentials

Pass credentials via the `env` block — most MCP hosts do not inherit your shell
environment, so `export OPENAI_API_KEY=...` in `.zshrc` will not be visible to
the server.

**Optional environment variables:**

- `OPENAI_MODEL` — model name (default: `gpt-5.4-mini`)
- `OPENAI_BASE_URL` — for OpenAI-compatible providers (Azure, local, etc.)

Your agent can now access EFF instructions, dimensions, and evaluation logic via
MCP.

---

## Local Development & Testing

### Interactive browser inspector

Spin up the FastMCP inspector to call tools and read resources in a browser UI —
no MCP host required.

If you haven't set up the virtual environment yet:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

Then start the inspector:

```bash
source .venv/bin/activate   # if not already active
fastmcp dev inspector eff/server.py
```

The resource-reader tools (`get_skill_instructions`, `get_dimensions_rubric`,
`get_examples`, `list_resources`) and the `eff://` resources work without an
API key. Only `ethics_filter` requires `OPENAI_API_KEY` to be set in your
shell.

### Claude Code (VS Code extension)

Create a `.mcp.json` file in the project root — Claude Code picks it up
automatically on reload:

```json
{
  "mcpServers": {
    "eff": {
      "command": "/absolute/path/to/.venv/bin/eff-mcp",
      "env": {
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

Reload VS Code (`Cmd+Shift+P` → `Developer: Reload Window`). The `eff` tools
become available immediately in the Claude Code chat — no separate trust dialog
needed.

> **Note:** `.mcp.json` is already gitignored — it contains your API key.

### Run tests

The suite is split into **unit tests** (hermetic, fast) and **integration
tests** (hit real OpenAI / Supabase, opt-in).

**Unit tests** — default. No API calls, no network:

```bash
pip install -e '.[dev]'
pytest
```

38 tests, well under a second. Run on every push via GitHub Actions.

**Integration tests** — opt-in. Require real credentials and incur cost:

```bash
pytest -m integration
```

Two end-to-end tests:

- `test_openai_e2e.py` — full scoring pipeline against the real OpenAI API
  (~$0.001 per run, requires `OPENAI_API_KEY`).
- `test_supabase_e2e.py` — retrieval against a live Supabase project
  (~$0.00002 per run, requires `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`).

Tests skip themselves cleanly if their required env vars are not set.

---

## RAG over Source Literature (Optional)

EFF can ground its scoring in passages retrieved from a vector store of relevant
academic literature (the EFF paper, IEEE 7000, ISO/IEC/IEEE 24748-7000, etc.).
When enabled, retrieved passages are injected into the scoring prompt and the
LLM is instructed to cite them in its `reason` field.

**Currently supported backend:** Supabase (Postgres + pgvector). Other vector
stores require implementing the `Retriever` Protocol in
[eff/retrieval.py](eff/retrieval.py).

The `supabase` package is bundled with the server, so no extra install step is
needed — RAG is enabled purely via environment variables (see below).

**Supabase schema** (run once in your Supabase SQL editor):

```sql
create extension if not exists vector;

create table documents (
  id bigserial primary key,
  content text not null,
  source text not null,
  embedding vector(1536) not null
);

create function match_documents(query_embedding vector(1536), match_count int)
returns table (id bigint, content text, source text, similarity float)
language sql stable as $$
  select id, content, source, 1 - (embedding <=> query_embedding) as similarity
  from documents
  order by embedding <=> query_embedding
  limit match_count;
$$;
```

The `vector(1536)` dimension matches OpenAI's `text-embedding-3-small`. Change
it if you use a different embedding model.

**Row-Level Security:** Supabase enables RLS on new tables by default, which
blocks the `anon` key from inserting or selecting. Two options:

1. **Use the `service_role` key for indexing**, the `anon` key for retrieval.
   This is the recommended split — `service_role` bypasses RLS and is meant for
   server/admin operations; `anon` is meant for public reads.
2. **Or add explicit policies for the `anon` key** if you want a single key:

   ```sql
   create policy "anon can insert documents"
     on documents for insert to anon with check (true);

   create policy "anon can read documents"
     on documents for select to anon using (true);
   ```

   Note: any client with this key can then read and write the table — fine for
   a private corpus, not advisable for a public deployment.

**Enable in the MCP host config:**

```json
{
  "mcpServers": {
    "eff": {
      "command": "eff-mcp",
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "EFF_RETRIEVAL_PROVIDER": "supabase",
        "SUPABASE_URL": "https://<project>.supabase.co",
        "SUPABASE_KEY": "<anon-key>"
      }
    }
  }
}
```

**Optional RAG environment variables:**

- `EFF_RETRIEVAL_PROVIDER` — `none` (default) or `supabase`
- `SUPABASE_RPC` — RPC function name (default: `match_documents`)
- `OPENAI_EMBEDDING_MODEL` — embedding model (default: `text-embedding-3-small`)
- `EFF_RETRIEVAL_K` — chunks per query (default: `5`)

**Citations in the response:** When RAG is enabled, each `ethics_filter`
response includes a `sources` array with the retrieved chunks (snippet, source
filename, similarity score). Citation markers like `[1]` or `[5]` in the
`reason` fields refer to entries in this array — `[1]` is `sources[0]`, `[5]`
is `sources[4]`, etc.

### Indexing your paper corpus

A small helper script is provided to index a folder of PDFs into the `documents`
table.

Create a `.env` file in the project root with your credentials (gitignored):

```bash
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_KEY=<anon-key>
```

Then install the extras and run the script:

```bash
pip install -e '.[indexing]'
python scripts/index_papers.py path/to/papers/
```

The script extracts text from each PDF, chunks it (default: 1000 chars with 200
char overlap), embeds the chunks with `text-embedding-3-small`, and inserts them
into Supabase in batches.

Optional flags:

- `--chunk-size N` (default: 1000)
- `--overlap N` (default: 200)
- `--batch-size N` (default: 50, embeddings per API call)
- `--clear` (delete existing rows before indexing — useful for re-indexing)

---

## Severity (Optional)

By default, EFF reports a binary-ish result per dimension (`pass` /
`Needs Improvement` / `fail`) without weighing how serious that result is in
the application's actual context. A Privacy concern in a patient-facing
health app is not the same as the same concern in a casual chat tool — the
severity is context-dependent.

When the caller passes a `context` string to `ethics_filter`, the LLM
additionally classifies the severity of any non-pass result as `low`,
`medium`, or `high` in that context.

**Usage from an MCP host:**

```
ethics_filter(
  user_story="As a patient, I want personalised dietary recommendations.",
  context="patient-facing health app handling dietary and medical history"
)
```

**Output shape:**

```json
{
  "results": {
    "privacy": {
      "result": "fail",
      "confidence": 0.92,
      "reason": "Health data retention is not specified.",
      "severity": "high"
    },
    "fairness": {
      "result": "pass",
      "confidence": 0.85,
      "reason": "...",
      "severity": null
    }
  }
}
```

**Rules:**

- Severity is `null` when `result` is `pass` (nothing to grade).
- Severity is `null` for every dimension when no `context` is given (default).
- Severity is independent of `confidence` — confidence measures how sure the
  evaluator is, severity measures how serious the concern is.

This is useful for triage: the same `Needs Improvement` rating is a low-
priority backlog item in one product and a sprint-blocker in another.

---

## Custom Dimensions (Optional)

The 5 built-in EFF dimensions (Utility, Fairness, Privacy, Explainability,
Safety) are non-negotiable — they are the core of the methodology. But teams
in specific domains often need additional dimensions: sustainability,
accessibility, regulatory compliance, security posture, etc.

Custom dimensions **extend** the built-ins; they cannot replace them. Once
configured, the LLM scores them alongside the 5 defaults and they appear in
the response under `custom_results`.

**Define your extras in a JSON file** with the same shape as the built-in
rubric:

```json
{
  "dimensions": {
    "sustainability": {
      "description": "The feature's long-term environmental and resource impact.",
      "rubric": {
        "pass": "Resource use is bounded and proportionate to value delivered.",
        "fail": "The feature creates substantial unbounded resource consumption.",
        "borderline": "Resource impact is unclear or only partially mitigated."
      },
      "scoring_notes": [
        "Consider compute, storage, energy, and lifecycle effects.",
        "Be conservative when telemetry is missing."
      ]
    },
    "accessibility": {
      "description": "Equitable usability across abilities, devices, and contexts.",
      "rubric": {
        "pass": "Meets WCAG 2.2 AA across primary flows.",
        "fail": "Excludes users with common assistive needs.",
        "borderline": "Partial coverage; key flows untested."
      },
      "scoring_notes": ["Assess against WCAG 2.2 AA where applicable."]
    }
  }
}
```

**Naming rules:**

- Names must be unique and not collide with the 5 built-ins.
- Names must be valid Python identifiers (letters, digits, underscores; no
  spaces, no leading digit) so they can become Pydantic field names.

**Enable via `EFF_EXTRA_DIMENSIONS_PATH`:**

```json
{
  "mcpServers": {
    "eff": {
      "command": "eff-mcp",
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "EFF_EXTRA_DIMENSIONS_PATH": "/etc/eff/extras.json"
      }
    }
  }
}
```

**Output shape:** the response keeps `results` as the typed 5 built-ins, and
adds a `custom_results` map for the extras:

```json
{
  "results": { "utility": {...}, "fairness": {...}, ... },
  "custom_results": {
    "sustainability": { "result": "Needs Improvement", "confidence": 0.8, "reason": "..." },
    "accessibility": { "result": "pass", "confidence": 0.9, "reason": "..." }
  },
  "summary": { "passed": 5, "needs_improvement": 1, "failed": 0 }
}
```

The summary counts include both built-in and custom dimensions.

---

## Audit Logging (Optional)

EFF can record every successful `ethics_filter` invocation as an append-only
JSONL file. Each line captures the original story, the model used, the
per-dimension scores, the enhanced story, the acceptance criteria, the
retrieved sources, and a UTC timestamp.

This is intended as an auditable trail — the methodology is built around
defensible, reviewable refinement decisions, and the log lets a team show
*"this is the exact evaluation that produced this enhanced story"* months
later.

**Enable by setting one environment variable:**

```json
{
  "mcpServers": {
    "eff": {
      "command": "eff-mcp",
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "EFF_AUDIT_LOG_PATH": "/var/log/eff/audit.jsonl"
      }
    }
  }
}
```

The directory is created if it does not exist. The file is opened in append
mode, so concurrent invocations append safely line-by-line.

**Disabled by default:** if `EFF_AUDIT_LOG_PATH` is unset, no file is written
and there is no overhead. Failures while writing the log are logged to stderr
but never propagate to the MCP host — an audit failure must not break a
scoring call.

**Inspecting entries:**

```bash
tail -n 1 /var/log/eff/audit.jsonl | jq .
```

---

## Code Generation from EFF Output

EFF returns the enhanced user story and acceptance criteria as structured data,
which can be used directly as input for code generation pipelines.

**How it works:**

1. Call `ethics_filter(user_story)` to get the EFF output.
2. Pass `enhanced_story` and `acceptance_criteria` to a code generation model as
   requirements.
3. The model produces code that already satisfies the ethical constraints —
   consent flows, data retention logic, AI disclosure labels, etc.

**Example prompt built from EFF output:**

```
Generate a React component based on the following requirements.

User Story: As a Yoga practitioner, I want to receive studio updates so I can stay informed, without data misuse or manipulative signup.

Acceptance Criteria:
- Privacy: Checkbox unchecked by default. Unconfirmed signups deleted in 30 days.
- Safety: Decline option has equal visual weight to signup.
- Explainability: Form lists exact email content types.

Return only the component code.
```

**Why this is useful:**

- Ethical requirements from EFF flow directly into code — no manual translation
  step.
- Privacy, fairness, and explainability constraints are enforced from the first
  line of implementation, not retrofitted later.

---

## References

- Sekulic, Vajo (JKU Linz), Sekulic, Verena (Universität Wien), Herda, Tomas
  (Austrian Post), Zhang, Zheying (Tampere University). (2026).
  [Adding Ethics to Agile: The Ethics Filter Framework (EFF)](https://www.researchgate.net/publication/404070751_Adding_Ethics_to_Agile_The_Ethics_Filter_Framework_EFF).
  ResearchGate.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for
details.
