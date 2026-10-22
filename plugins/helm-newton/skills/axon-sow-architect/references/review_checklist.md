# Review Checklist

This is the checklist the reviewer subagent applies to SOW + plan drafts.
It's also what you apply in Phase 6 quality checks before shipping.

## SOW structural checks

- [ ] Every `[placeholder]` from the template is resolved.
- [ ] The milestone title is specific, not generic ("Axon Search v1" not
      "Search feature").
- [ ] The milestone oznaka (M-tag) is present and matches the roadmap.
- [ ] SOW number, version, and effective date are filled.
- [ ] Reference to the Ugovor o poslovnoj suradnji (v4) is exact.

## Scope clarity

- [ ] The deliverable description (Section 1) is unambiguous — a third
      party should know exactly what's being built.
- [ ] Assumptions (Section 2.1) are each load-bearing. If removing one
      doesn't change price or scope, it's commentary — cut.
- [ ] Out-of-scope (Section 2.2) names real temptations. Things like
      "out of scope: support for Mars base" are filler. Good items are
      ones a stakeholder might plausibly assume are included.
- [ ] The boundary between this milestone and adjacent milestones
      (previous and next on the roadmap) is explicit.

## Acceptance criteria

- [ ] Each criterion is independently testable — a third party could say
      pass/fail without asking follow-ups.
- [ ] Criteria reflect the **job-to-be-done**, not the feature
      description. ("User finds correct part in ≤ 3 interactions" beats
      "Search returns results.")
- [ ] Number of criteria: 3–7. Fewer than 3 = underspecified. More than
      7 = either too granular or the scope is actually multiple
      milestones.
- [ ] No criterion depends on subjective judgment ("looks professional",
      "feels fast") without a measurable proxy.

## Commercial checks

- [ ] Fixed price is a whole reasonable number — not a false-precision
      figure like €9,347.
- [ ] Price has a defensible derivation in the synthesis memo (hours per
      step × hourly rate with roles). No day counts anywhere client-facing.
- [ ] Price = hour math × 02_CJENIK rates (€75 / €62.50 / €43.75 per hour)
      **plus** the single 10–15% uplift. Exactly one uplift, never two.
      Blended rate lands in €57–70/h (≈ €457–560/day), or up to €72/h when the
      hour mix explains it. Outside the band in either direction the cause is named
      (arithmetic, or an honest role mix) and taken to Grgur — below the floor with
      the sacrificed margin in euros in the plan. The rate is an arithmetic control
      only; it cannot detect an inflated scope.
- [ ] The /2 Claude Code pass was applied; coordination, dry-run and training were
      halved only with a stated reason.
- [ ] The internal plan lists what the anti-gold-plating pass cut, with hours.
- [ ] No price is presented as a discount off a larger "full value" figure.
- [ ] Client document carries "Procjena rada" (steps in business names +
      hours) and "Cijena i način rada" (fixed PZ vs hours × 40 €/h + difference
      table), both marked bez PDV-a and placed after the risks, and its last
      question is the client's choice of working mode.
- [ ] If the document still carries questions, the PZ amount says the final
      figure is confirmed after the answers — never a bare "fiksno".
- [ ] No guarantee depends on a third party; no unverified claim about how the
      client's people work today.
- [ ] Price aligns with the budget envelope from the interview, or a
      clear statement of why it doesn't.
- [ ] Section 7 contains a payment plan (čl. 7.2) — phase invoicing proposed for PZ > €6,000; no advance assumed.
- [ ] Section 8 states the nedostatak/promjena split (defects free ≤10 radnih dana; changes = new PZ or hourly) and
      unmodified.

## Contract (Ugovor v4) alignment

- [ ] Section 12 (Applicable contract terms) echoes Ugovor v4 articles correctly —
      IP, confidentiality, liability cap, GDPR, termination, law.
- [ ] No clause in the PZ contradicts the Ugovor silently. If a PZ term
      overrides a contract term, it must say so explicitly (the Ugovor permits
      this for scope-specific overrides).
- [ ] GDPR / DPA implications are noted where applicable.

## Timeline checks

- [ ] Start and end dates are specific (not "Q2 2026").
- [ ] Timeline is feasible at the declared price and team capacity.
- [ ] Client obligations (Section 6) are listed with concrete deadlines
      that make the timeline achievable.
- [ ] Dependencies that block start are called out in Section 10 as
      well as Section 6.

## Risk and dependencies

- [ ] At least 2 meaningful risks or dependencies are listed.
- [ ] Each has a mitigation or escalation path (not just named, but
      handled).
- [ ] The Lalizas portability question is explicitly addressed somewhere
      (even if the answer is "Croatia-only, accepted").

## Implementation plan checks

- [ ] Plan opens with "Required context to execute" — enough that a
      future Claude session can pick up cold.
- [ ] Each step carries an hour figure. Steps above 8 h are split, or the
      reason they are indivisible is stated.
- [ ] Each task has: action, verification, output.
- [ ] Dependencies between tasks are explicit.
- [ ] At least one checkpoint where a human reviews intermediate
      output (don't let Claude run end-to-end without human eyes).
- [ ] Plan references the SOW acceptance criteria as the definition of
      done.

## First-principles residue

- [ ] No red-flag phrases from `first_principles_framework.md`
      (AI-powered, seamless, best practice, etc.) survive in the SOW.
- [ ] The "don't build it" counter-case is addressed somewhere — either
      in synthesis or as a note to the user. If it's silent, the
      feature hasn't earned its place.

## Reviewer output format

The reviewer returns a redline report with three sections:

```markdown
# Redlines for <milestone-slug>

## Must-fix (blocks delivery)
- <line reference> — <problem> — <suggested fix>

## Should-fix (degrades quality materially)
- <line reference> — <problem> — <suggested fix>

## Nice-to-have (marginal improvement)
- <line reference> — <problem> — <suggested fix>

## Design questions (surface to user)
- <question> — <why it matters>
```

Must-fix and should-fix are applied automatically. Design questions go
to the user. Nice-to-have becomes a quick yes/no.
