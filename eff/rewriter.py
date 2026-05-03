# -*- coding: utf-8 -*-
"""EFF Rewriter: rewrites a user story using the EFF scoring result."""

import argparse
import json
from typing import Dict, List


def rewrite_story(user_story: str, scoring_result: dict) -> dict:
    """
    Rewrite a user story into an EFF-enhanced version based on the scoring result.
    Returns a dict with 'enhanced_story' and 'acceptance_criteria'.
    """
    # --- Step 1: Parse scoring result ---
    results = scoring_result.get("results") or scoring_result
    if not isinstance(results, dict):
        raise ValueError("Invalid scoring_result: missing 'results' dict")

    dim_names = [
        "utility",
        "fairness",
        "privacy",
        "explainability",
        "safety",
    ]
    harm_reasons = []
    needs_improvement_criteria = []
    fail_criteria = []

    # --- Step 2: Collect harm clause and acceptance criteria ---
    for dim in dim_names:
        dim_label = dim.title()
        dim_result = results.get(dim)
        if not dim_result:
            continue
        result = dim_result.get("result")
        reason = dim_result.get("reason", "")
        if result == "fail":
            harm_reasons.append((dim_label, reason))
            fail_criteria.append((dim_label, reason))
        elif result == "Needs Improvement":
            harm_reasons.append((dim_label, reason))
            needs_improvement_criteria.append((dim_label, reason))

    # --- Step 3: Build harm clause (if any FAIL or Needs Improvement) ---
    harm_clause = None
    if harm_reasons:
        # Combine all harm reasons into a single phrase
        phrases = []
        for dim_label, reason in harm_reasons:
            # Synthesize a short harm phrase from the reason
            phrases.append(reason.strip().rstrip("."))
        # Join with 'or' if multiple
        harm_clause = " or ".join(phrases)

    # --- Step 4: Build acceptance criteria ---
    acceptance_criteria: List[Dict[str, str]] = []
    for dim_label, reason in fail_criteria + needs_improvement_criteria:
        # Synthesize a measurable/testable criterion from the reason (placeholder)
        criterion = f"Address the following: {reason.strip()}"
        acceptance_criteria.append({"dimension": dim_label, "criterion": criterion})

    # --- Step 5: Assemble enhanced story ---
    # Parse the original story for stem/benefit (simple heuristic)
    stem = user_story.strip().rstrip(".")
    if harm_clause:
        enhanced_story = f"{stem}, without {harm_clause}."
    else:
        enhanced_story = f"{stem}."

    return {
        "enhanced_story": enhanced_story,
        "acceptance_criteria": acceptance_criteria,
    }


def main():
    parser = argparse.ArgumentParser(description="Rewrite a user story using EFF scoring result.")
    parser.add_argument("user_story", help="The original user story (string)")
    parser.add_argument("scoring_result_json", help="Path to JSON file with scoring result")
    args = parser.parse_args()

    with open(args.scoring_result_json, "r", encoding="utf-8") as f:
        scoring_result = json.load(f)

    result = rewrite_story(args.user_story, scoring_result)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
