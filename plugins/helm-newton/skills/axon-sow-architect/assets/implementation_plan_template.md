# Implementation Plan — `{{milestone_name}}` (`{{milestone_tag}}`)

> This plan is designed to be executed by a Claude session in the AXON
> project. Open a fresh Claude conversation, attach this file, and say:
> "Execute this implementation plan." The plan is self-contained — Claude
> should not need to ask foundational questions.
>
> **Language discipline.** Sections 0 (Required Context), 1 (Goal),
> 2 (Approach), 3 (Deliverables), 6 (Checkpoints), 7 (Definition of
> Done), 9 (Rollback), and 10 (Hand-off) must be written in plain
> business language — this is what a stakeholder reviews. Section 5
> (Task Breakdown) can use precise technical language where it helps
> the executor — that section is read by Claude and the engineer on
> duty, not the client.

---

## 0. Required Context to Execute

A future Claude session needs this context. Fill it fully — do not assume
the next session has memory of this conversation.

- **Milestone:** `{{milestone_tag}}` — `{{milestone_name}}`
- **SOW reference:** `{{sow_number}}` v`{{sow_version}}`, dated `{{effective_date_dd_mm_yyyy}}`
- **Project root:** `Marina store/Axon/`
- **Relevant prior artifacts:** `{{relevant_prior_artifacts}}`
  (list file paths of prior milestone outputs this one depends on)
- **Stakeholders:**
  - Accountable: `{{accountable_person}}`
  - Working-level contact: `{{technical_contact}}`
- **Key acceptance criteria (copied from SOW Section 3):**
  `{{acceptance_criteria_list}}`
- **Hard constraints:** `{{hard_constraints}}`
  (business-first phrasing: e.g. "must ship before the season starts on
  1 June", "budget capped at €X", "the current shop version cannot be
  upgraded during this milestone")

---

## 1. Goal

One sentence describing the end state.

`{{goal_sentence}}`

## 2. Approach

2–3 sentences on the chosen strategy and the key decision points, written
in business language. This is the "why this shape" rather than "what
exactly". A commercial reader should understand the shape of the work
without reading Section 5.

`{{approach_paragraph}}`

## 3. Deliverables

Concrete artifacts produced by executing this plan.

`{{deliverables_list}}`

## 4. Tools and Access Needed

- `{{tools_needed_list}}` — MCP servers, credentials, APIs, file access

## 5. Task Breakdown

Every step below is self-contained, verifiable, and carries its hours. Anything
above 8 h is split unless it is genuinely indivisible — say so if it is.

### Task 1 — `{{task_1_name}}`
**Hours:** `{{task_1_hours}}`
**Do:** `{{task_1_do}}`
**Verify:** `{{task_1_verify}}`
**Output:** `{{task_1_output}}`
**Depends on:** none

### Task 2 — `{{task_2_name}}`
**Do:** `{{task_2_do}}`
**Verify:** `{{task_2_verify}}`
**Output:** `{{task_2_output}}`
**Depends on:** Task 1

<!-- Continue Task 3, 4, ... as needed. Each task references its dependencies by number. -->

---

## 6. Human Checkpoints

Insert at least one human-review checkpoint. Do not let a Claude session run
straight from kickoff to completion without human eyes on intermediate
output.

- **Checkpoint 1:** After Task `{{checkpoint_1_after}}`, human reviews
  `{{checkpoint_1_artifact}}` and confirms alignment with intent before
  continuing.
- **Checkpoint 2 (optional):** After Task `{{checkpoint_2_after}}`, ...

---

## 7. Definition of Done

The plan is complete when all acceptance criteria from SOW Section 3 are
met, verified, and documented. Document verification in
`Marina store/Axon/Milestones/{{milestone_slug}}/verification.md` with a
paragraph per criterion and the evidence that it passed.

---

## 8. Risks During Execution

Risks specific to plan execution (separate from SOW-level risks). How should
the executing Claude session handle each?

`{{execution_risks_list}}` — each with a suggested response.

Example:

- *Risk:* The existing catalogue data does not match the structure we
  planned for — e.g. boat-fitment fields live in a different place than
  expected.
  *Response:* Pause, document what the data actually looks like, and raise
  a design question to the human before proceeding. Do not guess at
  mappings.

---

## 9. Rollback

If the milestone must be unwound or deferred, what are the steps?

`{{rollback_steps}}`

---

## 10. Hand-off Note

When the plan is executed to completion, the executing session must update
`Marina store/Axon/Milestones/{{milestone_slug}}/verification.md` and
notify `{{handoff_recipient}}` that the milestone is ready for SOW
acceptance per Ugovor o poslovnoj suradnji čl. 7.5 (5 radnih dana).
