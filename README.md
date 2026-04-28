# Ethics Filter Framework (EFF) — MCP Capability

This repository packages the Ethics Filter Framework (EFF) as a Model Context Protocol (MCP) capability for agent-based requirements engineering. It is designed for integration with agent platforms (e.g., OpenClaw) that support MCP, enabling automated User Story refinement and ethical risk surfacing during agile development.

---

## Why EFF?

In AI-intensive software development, User Stories are often the last actionable control point for surfacing and addressing ethical risks before code generation. Once requirements are handed off to agents or LLMs, missing constraints and stakeholder harms can propagate directly into implementation. EFF exists to make these risks explicit and actionable at the requirements level — before they become technical debt or real-world failures.

The goal is not to apply ethics after code generation, but to introduce ethical constraints at the specification stage, where AI-assisted development is still controllable.

---

## What EFF Does

EFF is a requirements-engineering method grounded in Value-Based Engineering (ISO/IEC/IEEE 24748-7000:2022). It:

- Identifies stakeholder risks and links them to explicit values
- Rewrites User Stories to include a harm clause
- Generates measurable acceptance criteria for each ethical dimension
- Provides a rubric for consistent, auditable requirements refinement

---

## The Five Dimensions

EFF operationalizes five core ethical dimensions derived from IEEE 7000:

| Dimension | What it checks |
|---|---|
| **Utility** | The feature provides meaningful benefit to the intended user |
| **Fairness** | The feature avoids unjustified discrimination or unequal treatment |
| **Privacy** | The feature respects confidentiality, data minimization, and purpose limitation |
| **Explainability** | The feature communicates relevant reasons, logic, or data practices clearly enough for informed use |
| **Safety** | The feature avoids harmful, unsafe, or policy-violating outcomes |

---

## Example Transformation

**Baseline User Story:**
> As a user, I want personalized recommendations so that I can find relevant content.

**EFF-enhanced User Story:**
> As a user, I want personalized recommendations so that I can find relevant content,
> without causing harm to stakeholders through opaque profiling or misuse of personal data.

**Acceptance criteria:**
- **Privacy:** Only fields classified as essential for generating recommendations are collected. All data is deleted or anonymized within 90 days of submission.
- **Explainability:** Before first use, a plain-language notice explains what data is collected, for what purpose, and for how long it will be stored.
- **Utility:** At least 80% of users who start the flow complete it. At least 75% report the recommendations are relevant in a post-interaction survey.

---

## How EFF is Exposed via MCP

This repository exposes EFF as an MCP-compatible capability. Agents can:

- Integrate EFF refinement into their requirements engineering workflows
- Retrieve EFF instructions and ethical dimension definitions
- Access example transformations and acceptance criteria templates
- Invoke evaluation logic for draft stories or requirements

---

## Intended Workflow

1. **Draft User Story**: An agent or user submits a baseline User Story
2. **EFF Refinement**: The agent invokes EFF via MCP to:
   - Identify missing ethical constraints
   - Rewrite the story with a harm clause
   - Generate acceptance criteria for each relevant dimension
3. **Implementation Spec**: The refined, ethically bounded User Story is returned as a safer specification for downstream implementation

---

## Quickstart (for MCP Hosts / Agent Integrators)

> **This server is intended to be self-hosted by the team or organization using it. Each deployment requires its own model provider credentials. This repository does not provide hosted inference.**

**Prerequisites:** Python 3.11+, an OpenAI-compatible API key.

**1. Clone and install:**

```bash
git clone https://github.com/your-org/eff-mcp
cd eff-mcp
pip install -e .
```

**2. Set your model credentials:**

```bash
export OPENAI_API_KEY=sk-...
# Optional:
# export OPENAI_MODEL=gpt-4o-mini
# export OPENAI_BASE_URL=https://api.openai.com/v1
```

**3. Point your MCP host at the server:**
For stdio-based hosts (e.g. Claude Desktop, OpenClaw, Cursor):

```json
{
  "mcpServers": {
    "eff": {
      "command": "python",
      "args": ["-m", "eff_mcp.server"]
    }
  }
}
```

4. Your agent can now access EFF instructions, dimensions, and evaluation logic via MCP.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
