Perfect draft. Here's the **final, production-ready `SKILL.md`** with minor tightening:

```markdown
# SKILL.md — EFF Rewriter

## Purpose

This skill rewrites a standard agile user story into an EFF-enhanced user story using the Ethics Filter Framework. It is the second step in the EFF pipeline, called after `ethics_filter` has scored the story.

## Inputs

- `user_story` — the original user story in standard agile format
- `scoring_result` — the output of `ethics_filter`, containing a result (`pass`, `borderline`, `fail`), a confidence score, and a reason for each of the five dimensions

## Rewriting rules

### Step 1 — Read the scoring result


For each of the five dimensions (Utility, Fairness, Privacy, Explainability, Safety), note the result:

- `pass` → no action needed for this dimension
- `borderline` → add a measurable acceptance criterion for this dimension
- `fail` → add a harm clause to the story stem AND a measurable acceptance criterion for this dimension

### Step 2 — Write the harm clause


A harm clause is a short phrase appended to the story stem after the benefit clause, but **only for dimensions that scored `fail`**:

> "...so that [benefit], **without [harm]**."

Rules for writing the harm clause:
- Only add a harm clause if at least one dimension scored `fail`.
- One harm clause per story, even if multiple dimensions failed — combine them into a single, readable phrase.
- Ground the clause in the specific reasons given by the scorer, do not invent new risks.
- Keep it concise — one sentence, plain language.
- Address the most severely failed dimension first.

**Examples:**
- Privacy FAIL → *"without my sensitive health data being used beyond the stated purpose"*
- Safety FAIL → *"without receiving unsafe advice or being steered toward contraindicated classes"*
- Fairness FAIL + Privacy FAIL → *"without exposing my private data or receiving biased suggestions"*

### Step 3 — Write the acceptance criteria


Write one to two acceptance criteria per `fail` or `borderline` dimension. Each criterion must be:

- **Measurable** — include a quantitative threshold where possible (e.g., "at least 80%", "no older than 90 days", "block rate ≥ 99%")
- **Testable** — a tester should be able to validate it as part of the Definition of Done
- **Grounded** — derived from the scorer's reason, not invented independently

Use the following templates as a starting point, adapted to the specific context:

- **Utility:** "At least [X]% of users achieve [outcome], and the average satisfaction score is at least [Y]/5."
- **Fairness:** "The difference in [error/success] rate between any two protected groups does not exceed [δ] percentage points."
- **Privacy:** "Only the following data fields are stored: [list]. No data older than [T] days is retained, and data is processed solely for [stated purpose]."
- **Explainability:** "At least [X]% of users can correctly answer [N] comprehension questions about why the system produced a given output."
- **Safety:** "The system produces no outputs that violate the defined safety policy. The observed violation rate is below [ε]%."

### Step 4 — Assemble the output

Return the enhanced user story in this format:

```
**EFF-Enhanced User Story**

As a [role], I want [feature], so that [benefit], without [harm clause].

**Acceptance Criteria**

- [Dimension]: [criterion]
- [Dimension]: [criterion]
...
```

Only include dimensions that scored `fail` or `borderline`. Do not add acceptance criteria for dimensions that passed — the story is already sound on those.

## What to avoid

- **Do not invent risks** not flagged by the scorer. The harm clause and acceptance criteria must be traceable to the scoring result.
- **Do not add a harm clause** for `borderline` dimensions — only for `fail`.
- **Do not use vague language** in acceptance criteria — "should be transparent" is not testable; "users see a privacy notice before submitting" is.
- **Do not repeat the scorer's reasoning verbatim** — synthesize it into plain, actionable language.
- **Do not rename the five dimensions** — always use: Utility, Fairness, Privacy, Explainability, Safety.

## Quick reference

```
| Scorer result | Rewriter action                                      |
|--------------|------------------------------------------------------|
| PASS         | No action required                                   |
| BORDERLINE   | Add a measurable acceptance criterion                |
| FAIL         | Add a harm clause + a measurable acceptance criterion|
```

## See also

- `examples.md` — Full worked examples showing scoring → harm clause → acceptance criteria
- `dimensions.json` — The rubric definitions used by `ethics_filter`
```
