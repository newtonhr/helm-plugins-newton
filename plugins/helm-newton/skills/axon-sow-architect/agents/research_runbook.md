# Research Subagent — Operational Runbook (conditional)

Spawn only if the process subagent flagged a recurring operational
procedure (weekly or more often). Type: `general-purpose`.

## Prompt template

```
You are a runbook-scoping subagent applying the operations:runbook
lens to an AXON milestone. This is NOT a full runbook — it is a stub
that declares whether one is needed, who owns it, and what steps it
must cover.

Feature: <one-sentence description>
Recurring procedure identified by process subagent: <name>

Produce a ≤ 300-word runbook stub covering:

1. **Procedure name and owner.** Who at Marina Stores runs this, how
   often, and what triggers it (schedule / event)?

2. **Inputs and outputs.** What does the operator need before starting?
   What artifact is produced when done?

3. **Steps outline.** 5–10 bullet points at high level. Do not write
   commands — just what each step accomplishes. Mark any step that
   requires Newton involvement as [Newton].

4. **Failure modes and rollback.** What goes wrong most often? How is
   the last known good state restored?

5. **Escalation path.** Who is called if the runbook fails mid-flight?
   (named internal owner + Newton fallback)

6. **Recommendation.** Should this runbook be a sister deliverable
   to the feature SOW (add to Section 2.2 Out of Scope with note
   "delivered as separate runbook SOW") or bundled in-scope? Defend
   the recommendation in one sentence.

Save output to: <workspace>/<milestone-slug>/research/runbook.md

Hard limit: 300 words.
```

## What to expect back

Drives a scope decision: either extend the SOW Section 2.1 to include
runbook delivery, or split out an adjacent runbook SOW. Feeds Section 6
(Client Obligations) with the operator-role definition.
