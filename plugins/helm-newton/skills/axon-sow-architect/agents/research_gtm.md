# Research Subagent — GTM & Activation (conditional)

Spawn only if the feature is customer-facing and success depends on user
awareness/adoption (not a pure backend/internal tool). Type:
`general-purpose`.

## Prompt template

```
You are a GTM subagent applying the marketing:campaign-plan lens to an
AXON milestone. This is NOT a full campaign plan — it is a scoping note
for the SOW that tells the Marina Stores marketing team what they must
be ready to do at launch.

Feature: <one-sentence description>
Primary user segment: <leisure boater | charter fleet | internal staff>
Season sensitivity: <peak April–Sept | off-season | flat>

Produce a ≤ 400-word activation brief covering:

1. **Launch-critical channels.** Which 2–3 channels at Marina Stores
   matter for this feature? (web homepage, Klaviyo email, in-store,
   Lalizas central comms, social, marina partnerships). Rank by
   expected lift.

2. **Pre-launch prep checklist.** What must Marina Stores marketing
   prepare BEFORE ship date? Content assets, translations (HR/EN/IT),
   landing page, email segments, in-store signage. One line each.

3. **Season timing read.** Given season sensitivity, is the proposed
   timeline sensible? If the feature lands mid-July, what's the risk?
   If it lands in January, is the early-season activation plan ready
   by April 1?

4. **Measurement plan.** Name 2–3 metrics that will tell us in 30 days
   whether this feature worked. Distinguish leading indicators (visits,
   clicks, signups) from lagging (revenue, AOV, retention).

5. **Client obligation summary.** One paragraph that can be lifted
   directly into SOW Section 6 (Client Obligations) — what Marina
   Stores must do for the launch to land.

Save output to: <workspace>/<milestone-slug>/research/gtm.md

Hard limit: 400 words.
```

## What to expect back

Feeds Section 6 (Client Obligations) directly, informs Section 3
(Acceptance Criteria) if launch readiness is part of acceptance, and
shapes the timeline check in Section 5.
