# Example Custom Dimensions

Files in this directory are templates for the `EFF_EXTRA_DIMENSIONS_PATH`
feature. They follow the same JSON shape as the built-in
[`eff/resources/dimensions.json`](../../eff/resources/dimensions.json) — each
extra dimension declares a `description`, a `rubric` with `pass` / `fail` /
`borderline` guidance, and `scoring_notes` to nudge the evaluator toward
consistent judgments.

## Available templates

- [`sustainability.json`](sustainability.json) — adds `sustainability` and
  `accessibility` dimensions for products with environmental and inclusivity
  concerns.

## How to use

Point `EFF_EXTRA_DIMENSIONS_PATH` at one of these files (or a copy you have
adapted to your domain) in your MCP host config:

```json
{
  "mcpServers": {
    "eff": {
      "command": "uvx",
      "args": ["eff-mcp"],
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "EFF_EXTRA_DIMENSIONS_PATH": "/absolute/path/to/sustainability.json"
      }
    }
  }
}
```

The custom dimensions will be scored alongside the 5 built-in EFF dimensions
(Utility, Fairness, Privacy, Explainability, Safety) on every `ethics_filter`
call. Extras appear in the response under `custom_results` rather than
`results`.

## Naming rules

- Names must be valid Python identifiers (letters, digits, underscores; no
  spaces or hyphens; cannot start with a digit).
- Names must not collide with the 5 built-ins.

## Writing your own

Copy one of these files and edit the `dimensions` block. Keep the rubric
grounded — vague rubrics produce vague scores.
