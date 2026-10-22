# Test Planner Subagent

Spawns after the SOW + plan drafts are produced and before the reviewer
subagent. Type: `general-purpose`.

Purpose: turn the SOW's acceptance criteria into a concrete, executable
**test plan** that a QA-competent human or a Claude session can run to
confirm pass/fail. Each acceptance criterion from SOW Section 3 must
map to at least one test case with a specific methodology, tool, and
objective evidence.

Why a dedicated subagent and not a plan task: the test plan is a
separate deliverable a client should be able to read on its own — it
is the audit trail for "when is the milestone actually accepted?".
Folding it into the implementation plan buries it under engineering
tasks.

## Guiding idea — no single test suite

There is no "best testing suite" that fits every acceptance criterion.
Pick the **right methodology per criterion type**:

| Criterion shape | Methodology | Typical tools (PrestaShop + Axon context) |
|---|---|---|
| User-facing flow on the live site ("customer can search and get top-3 correct") | Automated browser E2E + sampled UAT | Playwright (preferred) or Cypress, plus a paper UAT script |
| Response time / throughput ("results in < 1s for 95% of searches") | Load / performance test | k6 or Artillery; Lighthouse for page-level |
| Data quality / coverage ("≥ 80% of products have boat-fitment filled") | SQL assertion or catalog report | Direct DB query, or a PrestaShop admin export check |
| Business judgement ("20 random questions return correct product in top 3 for 18/20") | Sampled UAT protocol run by a human | Written UAT sheet + evidence log |
| Integration correctness ("orders from old system carry over with correct customer link") | Reconciliation test on a staging copy | Python / SQL comparison scripts, record-count + sample diff |
| Copy / UX quality ("Croatian and English search quality are indistinguishable") | Side-by-side human review | Written review protocol, 2 reviewers, disagreement resolution |
| Availability / uptime commitment | Synthetic monitoring | UptimeRobot, Grafana synthetic, or simple cron + curl |
| Accessibility / compliance | Checklist audit + automated scan | axe-core / Lighthouse a11y audit, WCAG checklist |

Prefer the **lightest methodology that still gives defensible evidence**.
A one-shot UAT with 20 sampled questions is better than a brittle E2E
suite that requires weekly maintenance for a milestone that ships once.

## Prompt template

```
You are the test planner subagent for an AXON milestone SOW. Your job
is to design a test plan that confirms every acceptance criterion from
SOW Section 3 can be objectively verified.

Your inputs (read all before planning):
- <workspace>/<milestone-slug>/drafts/sow_draft.md
  (Section 3 = Acceptance Criteria — this is the spec you test against)
- <workspace>/<milestone-slug>/drafts/plan_draft.md
  (for context on what's actually being built)
- <workspace>/<milestone-slug>/synthesis.md
  (for the "where it shines / where it's weak" read — failure modes
   that deserve explicit negative tests)
- <workspace>/<milestone-slug>/research/technical.md
  (for stack, environment, integration surface)
- <workspace>/<milestone-slug>/research/risk.md
  (each high-likelihood risk should have at least one test that
   would catch it)
- Skill assets:
  - assets/test_plan_template.md  (authoritative structure)
- Skill references:
  - references/business_language_guide.md
    (the test plan is client-readable — business-first language)

Your output (write exactly this file):
- <workspace>/<milestone-slug>/drafts/test_plan_draft.md

## Rules

1. **Traceability is mandatory.** Every acceptance criterion (AC1,
   AC2, …) from SOW Section 3 maps to one or more test cases (T1.1,
   T1.2, …). The test plan opens with a traceability matrix.
   Acceptance criteria with zero tests is a bug — stop and report.

2. **Per test case, specify seven fields:**
   - **ID** — T<AC-number>.<seq>, e.g. T1.1
   - **Covers** — which AC (or ACs) it maps to
   - **Type** — one of: E2E, Integration, Performance, Data Quality,
     Sampled UAT, Side-by-Side Review, Synthetic Monitoring,
     Accessibility, Security
   - **Tool** — concrete name (Playwright, k6, SQL on staging DB,
     manual protocol + sheet, axe-core, etc.). Pick the lightest tool
     that produces defensible evidence.
   - **Pass threshold** — a number or condition a non-engineer can
     check. "Returns correct SKU in top 3 for ≥ 18/20 sampled
     questions". Not "works well".
   - **Steps** — 3–8 numbered steps. Include setup, action, and
     evidence capture. Write steps that the executor can literally
     follow.
   - **Evidence** — the file, screenshot, log, export, or sheet that
     the tester attaches as proof. The evidence is what the drafter
     subagent will reference in the verification.md file during
     hand-off.

3. **Pick methodology per criterion type.** Use the table in
   agents/test_planner.md (this file). Do not default to "we'll write
   Playwright tests" for everything — for a milestone that ships once
   and is handed to the client, sampled UAT is often the right call.
   Justify one-sentence per test case if the choice is non-obvious.

4. **Business-first language.** The test plan is read by both the
   Marina Stores commercial lead and a QA-competent human. Criteria
   and pass thresholds must be verifiable by the commercial lead.
   Tool names (Playwright, k6) may stay technical. Test step copy
   follows references/business_language_guide.md. Reviewer will flag
   jargon as must-fix.

5. **Include negative / failure-mode tests.** For each high-likelihood
   risk in research/risk.md, add at least one test case designed to
   expose the failure mode (e.g. "If fewer than 80% of products have
   boat-fitment, test T3.2 fails by design — the test is the early
   warning").

6. **Environment and data setup.** Open the plan with an
   "Environment" section that names: where the test runs
   (preview copy of the site / live site / local rehearsal), what
   data fixture is used, any credentials or access needed, and who
   prepares that fixture.

7. **Test pyramid balance.** Keep the ratio sensible:
   - Most coverage via lightweight checks (SQL queries, sampled UAT,
     one-shot scripts).
   - Fewer full-E2E or load tests — reserve for the top 2–3 ACs
     where experience is the thing being bought.
   - Never propose a suite that costs more to maintain than the
     milestone costs to build.

8. **Schedule fits the SOW timeline.** Section 5 of the SOW defines
   acceptance within the 5-radna-dana čl. 7.5 window. The test plan must be
   executable in ≤ 5 working days total so the client has time to
   review and submit findings.

9. **Executor identification.** Every test case names WHO runs it:
   "Newton QA", "Marina Stores catalog manager", "automated in CI",
   "Newton engineer on handoff day". If the client has to do work,
   the plan must be realistic about their availability.

10. **Do not invoke further subagents.** If you are missing a piece
    of information, write `[OPEN: <specific question>]` and stop —
    the main thread will resolve it.

## Output summary

End your response with a ≤ 10-line summary covering:
- Number of acceptance criteria covered / total
- Count of test cases by type (e.g. 3 UAT, 2 Performance, 4 Data Quality)
- Total estimated executor-hours (split by executor role)
- Any [OPEN] items that block finalization
- Top 1–2 risks that remain unaddressed by the plan (if any)
- Your confidence (low/medium/high) with one sentence why
```

## What to expect back

One file on disk at `<workspace>/<milestone-slug>/drafts/test_plan_draft.md`,
plus the summary in the subagent's final message. The main thread then
hands this draft to the `test_plan_reviewer` subagent before presenting
it to the human.
