# Test Plan — `{{milestone_name}}` (`{{milestone_tag}}`)

> This test plan confirms the acceptance criteria in SOW `{{sow_number}}`
> v`{{sow_version}}`, Section 3. Every acceptance criterion below is
> mapped to one or more test cases with objective pass/fail thresholds
> and captured evidence. A commercial lead should be able to read this
> plan and tell, for each test, whether it passed or failed.
>
> **Language discipline.** Criteria and pass thresholds are written in
> business language that a commercial lead can verify. Tool names
> (Playwright, k6, SQL, etc.) stay technical — they identify the
> instrument, not the standard.

---

## 0. Environment and Preconditions

| Field | Value |
|---|---|
| **Where tests run** | `{{test_environment}}` (e.g. preview copy of Marina Stores / live site / local rehearsal against a snapshot) |
| **Data fixture** | `{{data_fixture}}` (e.g. "full catalogue export as of 2026-05-01, plus a tagged sample of 500 customer questions") |
| **Access needed** | `{{access_list}}` (admin, preview-site URL, staging DB read-only) |
| **Fixture owner** | `{{fixture_owner}}` (who prepares the data) |
| **Test window** | `{{test_window_dates}}` — ≤5 days execution, then the client's 5-radna-dana čl. 7.5 window |

---

## 1. Traceability Matrix

One row per acceptance criterion from SOW Section 3. Every AC must
have at least one test case.

| AC ID | Acceptance criterion (short) | Test cases | Executor | Estimated effort |
|---|---|---|---|---|
| AC1 | `{{ac1_short}}` | `{{ac1_test_cases}}` | `{{ac1_executor}}` | `{{ac1_effort}}` |
| AC2 | `{{ac2_short}}` | `{{ac2_test_cases}}` | `{{ac2_executor}}` | `{{ac2_effort}}` |
| AC3 | `{{ac3_short}}` | `{{ac3_test_cases}}` | `{{ac3_executor}}` | `{{ac3_effort}}` |
| ... | ... | ... | ... | ... |

**Gap check.** If any AC has zero test cases, that is a defect in this
plan. Do not ship this document with empty rows.

---

## 2. Test Case Catalogue

Each test case uses the seven-field format. Fill every field.

### T1.1 — `{{test_1_1_name}}`

- **Covers:** AC1
- **Type:** `{{test_1_1_type}}` (E2E / Integration / Performance / Data Quality / Sampled UAT / Side-by-Side Review / Synthetic Monitoring / Accessibility / Security)
- **Tool:** `{{test_1_1_tool}}` (concrete — e.g. "Playwright 1.42 on Chromium", "k6 0.49 against preview", "manual protocol on a printed sheet")
- **Pass threshold:** `{{test_1_1_threshold}}` (objective — a number or condition, not a soft verb)
- **Steps:**
  1. `{{test_1_1_step_1}}`
  2. `{{test_1_1_step_2}}`
  3. `{{test_1_1_step_3}}`
  4. `{{test_1_1_step_4}}`
- **Evidence:** `{{test_1_1_evidence}}` (the file, log, export, or sheet that attaches to the verification record)

### T1.2 — `{{test_1_2_name}}`

- **Covers:** AC1
- **Type:** `{{test_1_2_type}}`
- **Tool:** `{{test_1_2_tool}}`
- **Pass threshold:** `{{test_1_2_threshold}}`
- **Steps:**
  1. `{{test_1_2_step_1}}`
  2. `{{test_1_2_step_2}}`
  3. `{{test_1_2_step_3}}`
- **Evidence:** `{{test_1_2_evidence}}`

<!-- Continue T2.1, T2.2, T3.1, ... one per covered AC. -->

---

## 3. Negative / Failure-Mode Tests

For each high-likelihood risk listed in the SOW Section 10, at least
one test case is designed to expose the failure mode before sign-off.

| Risk (short) | Test case(s) that would catch it | Evidence if triggered |
|---|---|---|
| `{{risk_1_short}}` | `{{risk_1_tests}}` | `{{risk_1_evidence}}` |
| `{{risk_2_short}}` | `{{risk_2_tests}}` | `{{risk_2_evidence}}` |

---

## 4. Test Schedule

The plan must fit inside the delivery-to-acceptance span: ≤5 days execution,
then the client's 5-radna-dana čl. 7.5 window. Target
completion of test execution in ≤ 5 working days to leave the client
5 working days for review, findings, and written objection.

| Day | Activity | Owner |
|---|---|---|
| Day 1 | Environment setup, fixture load, smoke test | Newton QA |
| Day 2 | Automated test suite run + Data Quality checks | Newton QA |
| Day 3 | Sampled UAT by Marina Stores catalog manager | Marina Stores |
| Day 4 | Side-by-side reviews + performance test | Newton QA + Marina Stores |
| Day 5 | Consolidate evidence into verification.md + hand-off | Newton QA |
| Day 6–10 | Client review + written objection window (Ugovor čl. 7.5 — 5 radnih dana) | Marina Stores |

Adjust dates to the SOW Section 5 calendar.

---

## 5. Evidence and Hand-off

All evidence is consolidated into
`Marina store/Axon/Milestones/{{milestone_slug}}/verification.md` on
the last execution day. The verification file follows this structure
(one section per AC):

```
## AC1 — <short name>
- Tests executed: T1.1, T1.2
- Result: PASS / FAIL
- Evidence:
  - [Playwright run log](./evidence/T1_1_playwright.log)
  - [UAT sheet](./evidence/T1_2_uat.pdf)
- Notes:
```

Client acceptance (explicit or deemed per Ugovor čl. 7.5) is triggered
by the hand-off of this verification file.

---

## 6. Assumptions Baked Into This Plan

List the assumptions that, if false, invalidate test results. Example
starting points:

- The fixture reflects the catalogue the client sees on the live site
  (not a stale export).
- The preview copy of the site has the same integrations active as
  production (or any missing integration is explicitly noted below).
- The Marina Stores catalog manager is available for `{{uat_hours}}`
  hours across the test window to run UAT.

`{{assumptions_list}}`

---

## 7. Out of Scope for Testing

Some things are explicitly NOT tested by this plan and are not part
of acceptance (they may be covered by other SOWs or by production
monitoring):

`{{out_of_scope_testing}}` — examples: full load-testing at peak
season traffic, browser compatibility on browsers < 2% share, mobile
app behaviour (if the milestone is web-only), accessibility audit
beyond automated scan.

---

## 8. Open Questions

`{{open_questions}}` — anything the test planner flagged as `[OPEN: …]`
that the commercial lead or working-level contact must resolve before
test execution begins.
