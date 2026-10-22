# STATEMENT OF WORK

**(Special Work Agreement — pursuant to the Ugovor o poslovnoj suradnji)**

| Field | Value |
|---|---|
| **SOW number** | `{{sow_number}}` (format: SOW-NNN) |
| **Version** | `{{sow_version}}` |
| **Effective date** | `{{effective_date_dd_mm_yyyy}}` |
| **Ugovor reference** | Framework Cooperation Agreement between Newton d.o.o. and Lalizas Marine d.o.o. |

---

## 1. Milestone

| Field | Value |
|---|---|
| **Milestone name** | `{{milestone_name}}` |
| **Tag** | `{{milestone_tag}}` (e.g. M3 / M4 / ...) |
| **Deliverable description** | `{{deliverable_description}}` |

`{{deliverable_bullets}}` — 3–6 concrete deliverables, each a noun phrase
describing an artifact the Client will receive. Write in business language —
what the Client will be able to see, demo, or hand to an auditor. Avoid
engineering nouns. Example: "New search on the Marina Stores site, live on
a preview copy, covering the full product catalog." not "Deployed Axon
Search v1 on staging environment."

---

## 2. Scope Assumptions and Boundaries

### 2.1 Assumptions

The fixed price below rests on the following assumptions. If any assumption
proves materially incorrect, price and timeline may be adjusted by written
agreement.

`{{assumptions_list}}` — each assumption should be **load-bearing**: if it
turned out false, the scope or price would change. Aim for 3–6 assumptions.
Each assumption must be verifiable by a business reader — they should be
able to say "yes, that's true" or "no, that's not true" without asking an
engineer. Examples the user should adapt, not copy:

- The Marina Stores product catalogue contains fewer than 50,000 active
  products.
- At least 80% of products already have boat-fitment information filled
  in. If fewer, additional cataloguing is a separate effort.
- Marina Stores provides a tagged sample of 500 real customer questions
  within two weeks of kickoff, used to tune the search.

### 2.2 Out of Scope

The following are NOT included in this milestone and, if required, will
require a separate SOW or written agreement:

`{{out_of_scope_list}}` — should name **realistic temptations**, i.e. things
a reasonable stakeholder might assume are included. Write in plain
business terms, not engineering specifications. 3–6 items. Good examples:

- Translation of the search results into Italian and German (single-language
  Croatian/English for this milestone).
- Personalised results per returning customer (same results regardless of
  who is logged in).
- Analytics dashboard showing what customers searched for (separate
  milestone).

---

## 3. Acceptance Criteria

The deliverable is considered complete when all of the following are met:

`{{acceptance_criteria_list}}` — each criterion must be independently
testable BY A BUSINESS READER. A commercial lead (not an engineer) must
be able to say pass/fail. No engineering verbs. 3–7 criteria. Good
examples:

- A catalogue manager picks 20 real customer questions at random and the
  new search returns the correct product in the top 3 results for at
  least 18 of them.
- On a typical shop page, results appear in under one second for 95% of
  searches, measured across one full day of live traffic.
- The search works in both Croatian and English with no noticeable
  quality difference — confirmed by a side-by-side review of 10 queries
  in each language.

---

## 4. Acceptance Procedure

The procedure defined in čl. 7.5 of the Ugovor o poslovnoj suradnji applies:

1. Provider delivers the deliverable and notifies Client in writing, inviting
   review.
2. Client has 5 working days (radnih dana) to submit a written, reasoned
   objection (Izvještaj o nedostacima) or written acceptance. If neither is
   received within that window, the deliverable is deemed accepted.
3. Justified defects (deliverable ≠ agreed specification) are remedied free
   of charge within at most 10 working days (čl. 7.6). Requests beyond the
   agreed specification are Changes — see Section 9.
4. Acceptance is the trigger for invoicing (see Section 7).

---

## 5. Timeline

| Field | Value |
|---|---|
| **Work start date** | `{{start_date_dd_mm_yyyy}}` |
| **Estimated completion** | `{{end_date_dd_mm_yyyy}}` |
| **Delivery mechanism** | `{{delivery_mechanism}}` (e.g. Git repository / staging environment / demo + documentation) |

**Client-caused delay.** If Client fails to meet its obligations under
Section 6 within the agreed timeframes, the delivery timeline is extended by
the equivalent number of working days of delay. If Client-caused delay
exceeds 30 working days, Provider is entitled to invoice work performed to
date at the overflow rate of EUR 40 per hour.

---

## 6. Client Obligations

| Obligation | Deadline |
|---|---|
| Access to the Marina Stores site, admin area, and any source systems required for this milestone | Before work start |
| A named working-level contact empowered to answer day-to-day questions | Before work start |
| Relevant product, customer, and order data in a usable format | Before work start |
| Responses to working questions from Newton | 2 working days |
| Feedback on delivered work | 5 working days |

`{{additional_client_obligations}}` — optional extra row(s) with specific
artifacts or access needs tied to this milestone.

---

## 7. Commercial Terms

### 7.1 Fixed milestone price

| Field | Value |
|---|---|
| **Fixed price** | `{{fixed_price_eur}}` EUR (net, excluding VAT) |
| **Includes** | All work required to meet the acceptance criteria; free remedy of defects per čl. 7.6 |

### 7.2 Payment plan

`{{payment_plan}}` — required by čl. 7.2 of the contract. Default: single
invoice after acceptance. For PZs above €6,000, define phase invoicing here
(e.g. per accepted phase). This PZ is independent of the monthly Helm fee.

### 7.3 Invoicing and payment

- Invoice is issued after acceptance of the deliverable (explicit or deemed
  acceptance after the 5-working-day window), or per the payment plan above.
- Payment terms: 15 days from invoice receipt.
- Late payment, suspension and early termination terms are defined in the
  Ugovor o poslovnoj suradnji (čl. 6.6, 7.7, 20).

---

## 8. Defects and Changes

A **defect** (nedostatak) means the deliverable does not match the agreed
specification in this PZ. Defects are remedied free of charge within at
most 10 working days (čl. 7.6).

A **change** (promjena) means new functionality or an alteration beyond the
agreed scope. Changes are new work: agreed as a new Projektni Zadatak or as
rad po satu at EUR 40 per hour + VAT, subject to prior written approval
(čl. 7.4). There is no included revision round and no support obligation
after acceptance beyond the defect remedy above; ongoing autonomous support
is provided by Helm under the main contract.

---

## 9. Change Management

Any change to scope, acceptance criteria, or timeline after signature of
this PZ requires written agreement of both parties — as a new Projektni
Zadatak or as approved rad po satu (čl. 7.4). Without written agreement,
Provider is not obligated to perform work outside the defined scope.

---

## 10. Dependencies and Risks

The following external factors may impact delivery:

`{{dependencies_and_risks_list}}` — each item should be specific and
written in plain business language. Name the risk, then one sentence on
why it matters and one sentence on how it will be handled. Examples:

- **Catalogue quality.** If fewer than 80% of products have boat-fitment
  information, the new search will return poor results. We rehearse the
  search against the current catalogue in Week 1 and flag early if the
  quality bar is not met.
- **Dependency on the M1 catalogue cleanup milestone.** This milestone
  cannot start in earnest until M1 is accepted. If M1 slips by more than
  5 working days, we reset the start date in writing.

If any dependency blocks for more than 5 working days, the parties will
agree in writing on a timeline adjustment.

---

## 11. Key Contacts

|  | Newton d.o.o. | Lalizas Marine d.o.o. |
|---|---|---|
| **Project lead** | `{{newton_pm_name}}` | `{{lalizas_pm_name}}` |
| **Working-level contact** | `{{newton_tech_name}}` | `{{lalizas_tech_name}}` |
| **E-mail** | `{{newton_email}}` | `{{lalizas_email}}` |

---

## 12. Applicable Ugovor Terms

All terms of the Ugovor o poslovnoj suradnji apply to this SOW, including, without limitation:

- Intellectual property (Ugovor Article 7)
- Confidentiality (Ugovor Article 8)
- Liability cap (Ugovor Article 9)
- GDPR and data protection (Ugovor Article 10)
- Early termination and kill fee (Ugovor Article 6)
- Governing law and dispute resolution (Ugovor Article 12)

In case of conflict between the Ugovor o poslovnoj suradnji and this SOW, the terms of this SOW
apply for the scope of this milestone.

---

## Signatures

By signing, both parties confirm agreement with the terms of this Statement
of Work.

| NEWTON d.o.o. | Lalizas Marine d.o.o. |
|---|---|
| Place: Split | Place: Split |
| Date: ______________________ | Date: ______________________ |
| | |
| ______________________________ | ______________________________ |
| Andrea Grisogono | Ivan Boban |
| Director / CEO | Director / CEO |
