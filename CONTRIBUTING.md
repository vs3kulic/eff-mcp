# Contributing to eff-mcp

Thanks for your interest in contributing. This is a focused project — contributions that extend the EFF rubric, improve scoring quality, or add robustness are most welcome.

## What's in scope

- Improvements to scoring prompts or rubric definitions (`resources/dimensions.json`, `resources/SKILL.md`)
- New example transformations (`resources/examples.md`)
- Bug fixes in scorer or rewriter logic
- Tests (`tests/`)
- Documentation fixes

## What's out of scope (for now)

- Additional model providers (deferred to v2)
- Remote/HTTP transport (deferred to v2)
- Custom rubric support via config (deferred to v2)

## Getting started

```bash
git clone https://github.com/vs3kulic/eff-mcp
cd eff-mcp
conda activate <your-env>
pip install -e .
```

Set your `OPENAI_API_KEY` environment variable, then run the server:

```bash
python -m eff.server
```

## Making changes

1. Fork the repo and create a branch
2. Make your changes
3. Test manually — at minimum run `python -m eff.server` and verify the tool works end-to-end
4. Open a pull request with a clear description of what changed and why

## Rubric changes

Changes to scoring dimensions or rubric language have downstream effects on scoring consistency. If you propose rubric changes, include before/after examples showing how the new rubric scores a story differently.

## Code style

- Python 3.11+
- No formatter enforced yet — match the style of surrounding code
- Pydantic models for all structured outputs
- No silent failures — surface errors clearly
