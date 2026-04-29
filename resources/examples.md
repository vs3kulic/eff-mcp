# EFF-Enhanced User Story Examples

This document shows how to transform standard user stories into EFF-enhanced stories using the Ethics Filter Framework.

## How scoring maps to rewrites


When `ethics_filter` scores a story:

- **PASS** = story is ethically sound. No changes needed.
- **BORDERLINE** = add or tighten a measurable acceptance criterion for that dimension.
- **FAIL** = add a harm clause to the story and a measurable acceptance criterion for that dimension.

| Scorer result | Rewriter action                                      |
|--------------|------------------------------------------------------|
| PASS         | No action required                                   |
| BORDERLINE   | Add a measurable acceptance criterion                |
| FAIL         | Add a harm clause + a measurable acceptance criterion|

**Example mapping:**

Scoring result: Privacy = FAIL  
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

### Acceptance criteria (use 2-5 dimensions)

- Utility: [measurable benefit]
- Fairness: [equality check]
- Privacy: [data limits]
- Explainability: [understanding proof]
- Safety: [harm prevention]

## Example 1: Personalized recommendations

**Standard user story**

> As a user, I want personalized recommendations, so that I can discover relevant products.

**Scoring result**

Privacy: FAIL (collects unnecessary personal data)  
Fairness: BORDERLINE (may favor certain demographics)

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

Privacy: FAIL (health data retention unclear)  
Explainability: FAIL (no data purpose disclosure)

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

Safety: FAIL (no injury contraindication check)  
Explainability: BORDERLINE (no recommendation reasoning)

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

Safety: FAIL (risk of unsafe advice)  
Explainability: FAIL (no AI disclosure)

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

Privacy: FAIL (opt-out unclear)  
Safety: BORDERLINE (dark pattern risk)

**EFF-enhanced user story**

> As a Yoga practitioner, I want to receive studio updates, so that I can stay informed, **without data misuse or manipulative signup**.

### Acceptance criteria

- **Privacy**: Checkbox unchecked by default. Unconfirmed signups deleted in 30 days.
- **Safety**: Decline option has equal visual weight to signup.
- **Explainability**: Form lists exact email content types.

## Quick checklist

For any user story:
1. Run `ethics_filter` → note FAIL/BORDERLINE dimensions.
2. Add harm clause for each failed dimension.
3. Write 1-2 acceptance criteria per failed dimension.
4. Use measurable thresholds where possible.