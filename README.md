![Status](https://img.shields.io/badge/status-active-brightgreen)
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

This repository exposes EFF as an MCP-compatible capability. Agents can:

- Integrate EFF refinement into their requirements engineering workflows
- Retrieve EFF instructions and ethical dimension definitions
- Access example transformations and acceptance criteria templates
- Invoke evaluation logic for draft stories or requirements

---

## Quickstart (for MCP Hosts / Agent Integrators)

> **This server is self-hosted. Each deployment uses its own model provider
> credentials — this repository does not provide hosted inference.**

**Prerequisites:** Python 3.11+ and an OpenAI-compatible API key.

### Option A — Install from source (current)

```bash
git clone https://github.com/vs3kulic/eff-mcp
cd eff-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

This creates a local virtual environment and installs the `eff-mcp` console script into it. The `.venv/` folder is gitignored — every developer creates their own.

### Option B — Run via `uvx` _(coming soon — pending PyPI publish)_

No clone, no virtualenv — `uvx` fetches and runs the server on demand:

```json
{
  "mcpServers": {
    "eff": {
      "command": "uvx",
      "args": ["eff-mcp"],
      "env": {
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

### MCP host configuration

For stdio-based hosts (Claude Desktop, Cursor, OpenClaw, etc.) using the source
install:

```json
{
  "mcpServers": {
    "eff": {
      "command": "eff-mcp",
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "OPENAI_MODEL": "gpt-5.4-mini"
      }
    }
  }
}
```

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

Spin up the FastMCP inspector to call tools and read resources in a browser UI — no MCP host required.

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

Resources (`eff://dimensions`, `eff://skill`, `eff://examples`) work without an API key. Tools (`ethics_filter`, `list_resources`) require `OPENAI_API_KEY` to be set in your shell.

### Claude Code (VS Code extension)

Create a `.mcp.json` file in the project root — Claude Code picks it up automatically on reload:

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

Reload VS Code (`Cmd+Shift+P` → `Developer: Reload Window`). The `eff` tools become available immediately in the Claude Code chat — no separate trust dialog needed.

> **Note:** Add `.mcp.json` to your `.gitignore` — it contains your API key.

### Run unit tests

```bash
pip install -e '.[dev]'
pytest
```

24 tests, ~0.7s, no API calls or network required.

---

## RAG over Source Literature (Optional)

EFF can ground its scoring in passages retrieved from a vector store of relevant
academic literature (the EFF paper, IEEE 7000, ISO/IEC/IEEE 24748-7000, etc.).
When enabled, retrieved passages are injected into the scoring prompt and the
LLM is instructed to cite them in its `reason` field.

**Currently supported backend:** Supabase (Postgres + pgvector).

**Install with the optional `rag` extra:**

```bash
pip install -e '.[rag]'
```

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

You are responsible for indexing your paper corpus into the `documents` table.
The indexing pipeline is out of scope for this server.

---

## Code Generation from EFF Output

EFF returns the enhanced user story and acceptance criteria as structured data,
which can be used directly as input for code generation pipelines.

**How it works:**

1. Call `ethics_filter(user_story)` to get the EFF output.
2. Pass `enhanced_story` and `acceptance_criteria` to a code generation model as requirements.
3. The model produces code that already satisfies the ethical constraints — consent flows, data retention logic, AI disclosure labels, etc.

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

- Ethical requirements from EFF flow directly into code — no manual translation step.
- Privacy, fairness, and explainability constraints are enforced from the first line of implementation, not retrofitted later.

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
