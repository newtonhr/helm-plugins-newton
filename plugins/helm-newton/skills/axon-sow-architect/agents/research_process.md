# Research Subagent — Process & Operations

Spawn with: `general-purpose` agent type.

## Prompt template

```
You are a process analysis subagent applying the
operations:process-optimization lens to an AXON milestone.

Feature: <one-sentence description>
Primary user segment: <leisure boater | charter fleet | internal staff>

Tasks:

1. **Map the current workflow.** Describe how the task this feature
   affects is handled TODAY at Marina Stores. Who does what, in which
   system, with what handoffs? If the feature is greenfield, describe
   what happens instead of this job-to-be-done right now (manual,
   foregone, workaround).

2. **Map the proposed workflow.** Describe how the task is handled
   AFTER this feature ships. Same format: who, what, where, with what
   handoffs.

3. **Delta analysis.** What changes between current and proposed?
   Specifically:
   - Steps eliminated
   - Steps added (often overlooked!)
   - Handoffs that shift owner
   - Roles affected (warehouse, customer support, catalog manager,
     web team)

4. **Internal adoption cost.** Who at Marina Stores needs to learn,
   retrain, or change habits? Estimate hours of training and weeks to
   steady-state.

5. **Moat effect.** Does this feature codify staff expertise (moat
   BUILDING) or route around it (moat ERODING)? If eroding, is that
   deliberate, and is the trade-off worth it?

6. **One process-runbook candidate.** If this feature introduces a
   recurring operational procedure (something that happens weekly or
   more), name it — it's a candidate for an operations:runbook sister
   deliverable.

Save output to: <workspace>/<milestone-slug>/research/process.md

Hard limit: 500 words.
```

## What to expect back

Process map (current + proposed), delta, adoption cost, moat read. Feeds
Sections 2.1 (assumptions about client readiness), 6 (client
obligations), and the reviewer's "where it's weak" check.
