![Status](https://img.shields.io/badge/status-active-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-blueviolet)
![FastMCP](https://img.shields.io/badge/FastMCP-ready-orange)


# Ethics Filter Framework (EFF) — MCP Capability

This repository packages the Ethics Filter Framework (EFF) as a Model Context Protocol (MCP) capability for agent-based requirements engineering. It is designed for integration with agent platforms (e.g., OpenClaw) that support MCP, enabling automated User Story refinement and ethical risk surfacing during agile development.

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

## Code Generation from EFF Output

EFF returns the enhanced user story and acceptance criteria as structured data, which can be used directly as input for code generation pipelines.

**How it works:**
1. **Input:** You give the user story and the EFF acceptance criteria to an AI model or agent.
2. **Prompt:** You ask the model to write code (for example, a React component or a backend API) that does what the story says and follows all the acceptance criteria.
3. **Output:** The model gives you code that is ready to use, and it already includes the ethical rules from EFF.

**Why this is helpful:**
- The EFF acceptance criteria become part of the requirements for the code, so values like fairness, privacy, and explainability are included from the start.
- For example:
  - If there is a Privacy rule, the code might ask users for consent or delete old data.
  - If there is an Explainability rule, the code might show a message explaining how it works or add helpful comments.


### Example: Using EFF Output for Code Generation

Here’s a simple JavaScript example showing how to use EFF output to generate code with an LLM (like Claude):

```js
// 1. Run the EFF filter on your user story
const storyResponse = await fetch("https://your-eff-api/ethics_filter", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    user_story: "As a Yoga practitioner, I want to receive the latest updates related to the yoga studio so that I can stay informed about studio-related events."
  })
});

const { results, summary } = await storyResponse.json();

// 2. Build a prompt from the EFF output
const effPrompt = `
Generate a React component based on the following requirements.

User Story: As a Yoga practitioner, I want to receive studio updates so I can stay informed.

Acceptance Criteria (from EFF analysis):
- Fairness: Updates must be accessible to all user groups regardless of device or ability.
- Privacy: Disclose what data is collected, how it is delivered, and how long it is retained.
- Explainability: Make clear to the user what sources and criteria determine the updates shown.

Return only the component code.
`;

// 3. Send to Claude API for code generation
const codeResponse = await fetch("https://api.anthropic.com/v1/messages", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    model: "claude-sonnet-4-20250514",
    max_tokens: 1000,
    messages: [{ role: "user", content: effPrompt }]
  })
});

const { content } = await codeResponse.json();
console.log(content[0].text); // Your ethically-informed component
```

> **Note:** Replace the API endpoints with your actual EFF server and Claude API URLs. Handle API keys securely.

---

## References

- Sekulic Vajo (JKU Linz), Sekulic Verena (Universität Wien), Zhang Zheying (Tampere University), Herda Tomas (Austrian Post). (2026). [Adding Ethics to Agile: The Ethics Filter Framework (EFF)](https://www.researchgate.net/publication/404070751_Adding_Ethics_to_Agile_The_Ethics_Filter_Framework_EFF). ResearchGate.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
