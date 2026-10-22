# Research Subagent — Risk Enumeration

Spawn with: `general-purpose` agent type.

## Prompt template

```
You are a risk enumeration subagent applying the operations:risk-assessment
mental model to an AXON milestone.

Feature: <one-sentence description>
Commercial frame (contract v4): no retainer — all work as fixed-price Projektni Zadaci; rad po satu €40/h with prior approval; Helm €700/mo autonomous support only. PZ prep free (margin +10–15% carries it); invoiced after completion, 15 days; acceptance 5 radnih dana deemed; defects free ≤10 radnih dana, changes = new PZ.

Enumerate risks across five categories. For each risk, provide:
- Name
- Likelihood (Low / Medium / High)
- Impact (Low / Medium / High)
- Mitigation (concrete action, not "monitor")
- Owner (Newton / Marina Stores / Joint)

Categories:

1. **Technical** — integration failures, data issues, performance,
   dependencies. Min 2 risks.

2. **Commercial** — scope creep, fixed-price erosion, acceptance
   disputes, change order friction, pricing sanity. Min 2 risks.

3. **Operational** — delivery timeline, client-side availability,
   knowledge gaps, handoff to internal team. Min 2 risks.

4. **Legal / Compliance** — GDPR, data residency, IP ownership,
   third-party licensing, consumer protection. Min 1 risk.

5. **Adoption** — low user uptake, internal resistance, Lalizas
   central non-adoption. Min 1 risk.

For ONE risk across all categories — the one you consider load-bearing —
provide an expanded 3-sentence analysis: why this is the single most
likely thing to derail the milestone, what would signal it early, what the
fallback is if mitigation fails.

Output format: markdown table for the main list, then the expanded
analysis below.

Save output to: <workspace>/<milestone-slug>/research/risk.md

Hard limit: 600 words.
```

## What to expect back

A risk register with at least 8 risks (2+2+2+1+1), plus one deep-dive.
Feeds SOW Section 10 (Dependencies and Risks) and the reviewer's
risk-coverage check.
