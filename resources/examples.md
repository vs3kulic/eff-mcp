# Example EFF-Enhanced User Stories

## Standard User Story

> As a user, I want to receive personalized recommendations, so that I can discover relevant products.

## EFF-Enhanced User Story

> As a user, I want to receive personalized recommendations, so that I can discover relevant products, **without exposing my private data or receiving biased suggestions**.

### Acceptance Criteria (EFF Dimensions)

- **Utility**: Recommendations increase user engagement by at least 10% over baseline.
- **Fairness**: No group receives systematically less relevant recommendations (measured by click-through rate parity).
- **Privacy**: No personally identifiable information is stored or shared with third parties.
- **Explainability**: Users can view a summary of why a recommendation was made.
- **Safety**: Recommendations do not include unsafe or policy-violating products.

---

## Another Example

> As a parent, I want parental controls, so that my child can use the app safely, **without being exposed to inappropriate content**.

### Acceptance Criteria

- **Utility**: Parental controls can be enabled/disabled by the parent at any time.
- **Safety**: Inappropriate content is filtered with 99% accuracy.
- **Explainability**: Parents receive a report of blocked content and reasons.
- **Privacy**: Child data is not shared outside the app.

---

# Appendix A: User Story Repository

## 8.1 User Stories v1
These stories were implemented as a baseline version (v1) of the Yogi web application.

**US-01: Yoga-Themed Questionnaire**
As a Yoga practitioner, I want to complete a questionnaire about my preferences so that the system understands my needs.

**US-02: Class Recommendations**
As a Yoga practitioner, I want to receive class recommendations based on my questionnaire responses so that I can easily find suitable classes.

**US-03: AI-Generated Pro-Tips**
As a Yoga practitioner, I want to receive personalized pro-tips based on my questionnaire responses so that I can enhance my practice.

**US-04: Newsletter Subscription**
As a Yoga practitioner, I want to receive the latest updates related to the yoga studio so that I can stay informed about studio-related events.

---

## 8.5 User Stories v2 (EFF-Enhanced)

**US-02 v2: Course Recommendations**
As a Yoga practitioner, I want to receive class recommendations based on my questionnaire responses so that I can easily find suitable classes without being steered toward inappropriate classes through biased algorithms.

*Acceptance Criteria:*
- **Utility:** At least 80% of recommended classes are rated ≥ 4/5 by users in a post-session feedback survey (satisfaction).
- **Safety:** For users reporting injuries or limitations (e.g., back pain, pregnancy, joint issues), classes flagged as contraindicated for a reported condition are never recommended.
- **Explainability:** The recommendation screen includes a brief explanation such as “Recommended based on your goals, experience, and limitations” plus a description justifying the selection.

**US-03 v2: AI-Generated Pro-Tips**
As a Yoga practitioner, I want to receive personalized pro-tips based on my questionnaire responses so that I can enhance my practice without manipulation through psychologically persuasive content serving business goals.

*Acceptance Criteria:*
- **Utility:** The tips achieve a relevance score of ≥ 0.75 based on distinct user feedback (thumbs up vs. thumbs down).
- **Safety:** All generated content passes through a safety filter that blocks advice encouraging pushing through pain or offering medical diagnoses; testing demonstrates a block rate of ≥ 99% for unsafe tips.
- **Explainability:** Every tip is explicitly visually tagged (e.g., “AI-Generated”) to ensure users distinguish automated suggestions from human instructor advice.
- **Autonomy:** Generated tips are strictly limited to yoga technique or mindset advice. No content includes calls to action for purchasing subscriptions, merchandise, or unlocking premium features (upselling).

**US-04 v2: Newsletter Signup**
As a Yoga practitioner, I want to receive the latest updates related to the yoga studio so that I can stay informed about studio-related events without manipulation via dark patterns or data misuse.

*Acceptance Criteria:*
- **Fairness:** Essential application information (pricing, feature overview, privacy policy) is fully accessible to the user without requiring a newsletter subscription.
- **Privacy:** The subscription checkbox is unchecked by default (opt-in). If a user initiates signup but does not confirm (double opt-in), their email address is automatically and permanently deleted from the system within 30 days.
- **Explainability:** The signup form explicitly lists the types of content to be sent (e.g., “Weekly tips,” “Product updates”). User testing confirms that at least 85% of participants correctly understand the nature and frequency of the emails before signing up.
- **Safety:** The interface avoids manipulative design (dark patterns); the option to decline or skip is presented with neutral language and equal visual prominence to the signup button (e.g., no “confirmshaming”).
