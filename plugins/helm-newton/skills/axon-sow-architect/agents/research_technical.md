# Research Subagent — Technical Feasibility

Spawn with: `Explore` agent type (thorough), or `general-purpose` if Explore
is not available.

## Prompt template

```
You are a technical feasibility subagent for an AXON program feature.

Feature: <one-sentence description>
Milestone tag: <M1/M2/.../ad-hoc>

The AXON stack (as of April 2026):
- PrestaShop v8 (migration to v9 is milestone M2; may or may not be done)
- Croatian-hosted, connected to Marina Stores ERP
- No analytics layer yet (being added in a parallel Change Registry effort)

Tasks:

1. Read any existing architecture / integration docs in the workspace
   at `Marina store/Axon/Technical/`. List the files you found and summarize
   their relevance to this feature in one paragraph each.

2. For the feature, enumerate:
   - Integration surfaces (PrestaShop modules, external APIs, data sources)
   - Data flows (what reads what, what writes what)
   - Storage needs (volume, retention, privacy classification)
   - Performance envelope (latency budget for user-facing paths)

3. Identify **technical preconditions**. What must be true before work
   can start? (e.g. "v9 migration complete", "catalog attributes
   normalized", "staging environment provisioned")

4. Identify **the single biggest technical risk** and a concrete
   mitigation. Don't just name it — name what you'd do on day 1 to
   de-risk.

5. Hour estimate per step by role: architecture, development, QA.
   Hours, never days. Give the manual-work figure and the halved
   Claude-Code figure side by side, and mark which steps are human-paced
   (third-party coordination, dry-run on live, training) so they are not
   halved without a reason. Flag anything you had to guess as
   HIGH-UNCERTAINTY. Also list, separately, every item you would call
   gold-plating — something neither the law, the client nor reliability
   requires — with its hours, so the drafter can cut it before pricing.

Save output to: <workspace>/<milestone-slug>/research/technical.md

Hard limit: 700 words (this one gets more space because the hour
estimate needs detail).
```

## What to fill in

- Feature description — from interview
- Milestone tag — from Phase 0
- Workspace path — from Phase 0

## What to expect back

A markdown file at `research/technical.md`. The hour estimates feed
directly into Section 7 pricing derivation, after the drafter applies the
/2 and anti-gold-plating passes.
