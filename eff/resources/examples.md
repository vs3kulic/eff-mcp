# EFF-Enhanced User Story Examples

This document shows how to transform standard user stories into EFF-enhanced stories using the Ethics Filter Framework.

## How scoring maps to rewrites

When `ethics_filter` scores a story:

- **pass** — story is ethically sound on this dimension. No changes needed.
- **Needs Improvement** — add a measurable acceptance criterion for that dimension.
- **fail** — add a harm clause to the story AND a measurable acceptance criterion for that dimension.

| Scorer result      | Rewriter action                                       |
|--------------------|-------------------------------------------------------|
| pass               | No action required                                    |
| Needs Improvement  | Add a measurable acceptance criterion                 |
| fail               | Add a harm clause + a measurable acceptance criterion |

**Example mapping:**

Scoring result: Privacy = fail
↓
Enhanced story: "...without exposing my private data..."
↓
Acceptance criteria:
- Privacy: Only [list] data fields are stored. No data older than 30 days is retained.

## The five EFF dimensions

All acceptance criteria use these five dimensions:

- **Utility**: Does it deliver real value?
- **Fairness**: Does it treat all groups equally?
- **Privacy**: Does it protect personal data?
- **Explainability**: Can users understand why/how it works?
- **Safety**: Does it prevent harm?

## Pattern

**Standard user story**

> As a [role], I want [feature], so that [benefit].

**EFF-enhanced user story**

> As a [role], I want [feature], so that [benefit], **without [harm clause]**.

### Acceptance criteria (for each non-passing dimension)

- Utility: [measurable benefit]
- Fairness: [equality check]
- Privacy: [data limits]
- Explainability: [understanding proof]
- Safety: [harm prevention]

## Example 1: Personalized recommendations

**Standard user story**

> As a user, I want personalized recommendations, so that I can discover relevant products.

**Scoring result**

Privacy: fail (collects unnecessary personal data)
Fairness: Needs Improvement (may favor certain demographics)

**EFF-enhanced user story**

> As a user, I want personalized recommendations, so that I can discover relevant products, **without exposing my private data or receiving biased suggestions**.

### Acceptance criteria

- **Utility**: At least 80% of recommendations receive a click-through or positive rating.
- **Fairness**: No demographic group receives recommendations with < 70% relevance (measured by CTR parity).
- **Privacy**: Only anonymized behavior data is used. No PII is stored or shared.
- **Explainability**: Users can tap "Why this?" to see a 1-sentence explanation.

## Example 2: Yoga questionnaire

**Standard user story**

> As a Yoga practitioner, I want to complete a questionnaire about my preferences, so that the system understands my needs.

**Scoring result**

Privacy: fail (health data retention unclear)
Explainability: fail (no data purpose disclosure)

**EFF-enhanced user story**

> As a Yoga practitioner, I want to complete a questionnaire about my preferences, so that the system understands my needs, **without my sensitive health data being used beyond the stated purpose**.

### Acceptance criteria

- **Privacy**: Only essential fields collected. Data deleted after 90 days.
- **Privacy**: Pre-questionnaire notice lists data purpose and retention.
- **Explainability**: 85% of users correctly identify data purpose in a post-survey.
- **Utility**: 80% questionnaire completion rate.

## Example 3: Yoga class recommendations

**Standard user story**

> As a Yoga practitioner, I want class recommendations based on my questionnaire, so that I can find suitable classes.

**Scoring result**

Safety: fail (no injury contraindication check)
Explainability: Needs Improvement (no recommendation reasoning)

**EFF-enhanced user story**

> As a Yoga practitioner, I want class recommendations based on my questionnaire, so that I can find suitable classes, **without being steered toward contraindicated classes**.

### Acceptance criteria

- **Safety**: 0 contraindicated classes recommended for users reporting injuries.
- **Utility**: 80% of recommendations rated ≥ 4/5 post-session.
- **Explainability**: Each recommendation shows "Based on your [goals/level/injuries]".

## Example 4: AI pro-tips

**Standard user story**

> As a Yoga practitioner, I want personalized pro-tips based on my questionnaire, so that I can enhance my practice.

**Scoring result**

Safety: fail (risk of unsafe advice)
Explainability: fail (no AI disclosure)

**EFF-enhanced user story**

> As a Yoga practitioner, I want personalized pro-tips based on my questionnaire, so that I can enhance my practice, **without receiving unsafe advice or hidden AI manipulation**.

### Acceptance criteria

- **Safety**: 99% of unsafe tips (pain encouragement, medical advice) blocked by filter.
- **Explainability**: All tips visibly tagged "AI-generated".
- **Utility**: ≥ 75% thumbs-up relevance rating.

## Example 5: Newsletter signup

**Standard user story**

> As a Yoga practitioner, I want to receive studio updates, so that I can stay informed.

**Scoring result**

Privacy: fail (opt-out unclear)
Safety: Needs Improvement (dark pattern risk)

**EFF-enhanced user story**

> As a Yoga practitioner, I want to receive studio updates, so that I can stay informed, **without data misuse or manipulative signup**.

### Acceptance criteria

- **Privacy**: Checkbox unchecked by default. Unconfirmed signups deleted in 30 days.
- **Safety**: Decline option has equal visual weight to signup.
- **Explainability**: Form lists exact email content types.

## Quick checklist

For any user story:
1. Call `ethics_filter(user_story)`.
2. For each `fail` or `Needs Improvement` dimension: include the acceptance criterion in the Definition of Done.
3. Use the `enhanced_story` to replace the original in the backlog.
