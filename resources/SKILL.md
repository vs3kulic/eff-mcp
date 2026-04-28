
# EFF SKILL: Agent Routing Instructions

## When to Apply EFF

- When drafting, reviewing, or refining User Stories for features involving AI, personal data, recommendations, or autonomous actions.
- When acceptance criteria or harm clauses are missing or unclear.

## How to Apply EFF

1. For each User Story, check if it includes an explicit harm clause ("...without causing harm to...").
2. For each ethical dimension in `dimensions.json`, suggest at least one measurable acceptance criterion.
3. Use the examples in `examples.md` as templates.
4. If a story is missing ethical constraints, recommend additions or edits.
5. When evaluating, use `scorer.py` to check draft stories or criteria for completeness and clarity.

## Output Format

Return a list of suggested harm clauses and acceptance criteria, grouped by ethical dimension.
