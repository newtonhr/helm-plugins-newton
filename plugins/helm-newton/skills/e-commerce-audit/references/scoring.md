# Scoring inputs

`score.py` does all arithmetic. This file says how to choose its inputs. The same rules sit as live formulas in the .xlsx (Settings sheet holds the thresholds); `build_backlog.py verify` proves the two agree.

## Contents
1. What the scripts compute
2. Impact inputs (margin base, effect, estimated)
3. Confidence inputs (rigor, transfer)
4. Effort inputs
5. Bundles
6. Tags, measurement, acceptance criteria
7. Behavior lane (unscored)

## 1. What the scripts compute

| Output | Rule |
|---|---|
| Impact €/yr | margin base × (effect low + effect high) / 2 |
| Bundle impact | largest active child + 50% of each other active child |
| Impact band | 1 < 2,000 € ≤ 2 < 10,000 € ≤ 3 < 25,000 € ≤ 4 < 50,000 € ≤ 5 |
| Effort band | person-days ≤3 →1, ≤10 →2, ≤20 →3, ≤40 →4, else 5; +1 if run cost > 300 €/month; max 5 |
| Rigor weight | A 1.0 · B 0.7 · C 0.4 · Policy 0.4 · C until verified 0.4 |
| Est. factor | 0.7 if estimated, else 1 |
| Confidence | rigor weight × transfer × est. factor |
| Priority | impact band × confidence ÷ effort band |
| Quadrant | Quick win: impact ≥3, effort ≤2 · Big bet: impact ≥3, effort ≥3 · Fill-in: impact ≤2, effort ≤2 · Skip: impact ≤2, effort ≥3 |
| Test first | confidence < 0.3 → never in the report's quick wins |
| PR/FAQ needed | effort band ≥ 4 |
| Transfer caps | CAT-1, CAT-2, REC-2 capped at 0.4 automatically |
| Defaults | missing effect → 1–3% and estimated. Missing margin base → ERROR (estimate one instead) |
| Enabler children | SRC-2, SRC-9 inside a bundle get margin base 0: no impact credit |
| Behavior lane | `behavior` items are validated and ranked: defects first (effort S→L), then hypotheses (grade A→C, effort S→L, ID). No €, no bands, no quadrant |
| Hard errors | no evidence; effects not fractions (>1) or low > high; transfer not 0.4/0.7/1.0; non-numeric numbers; negative days; safety-critical without "per-SKU" in acceptance criteria; `bundle` field on a non-child; a BEH-, PATH- or NEWB- ID in `findings`; a lane item with a € field, no hypothesis, no evidence, or (truth-rule cards) no `truth_source` |

## 2. Impact inputs

- **Margin base (€/yr):** required for every active item and child. Gross margin of the part of the business the change touches. Without margin data, estimate it (total web margin × share affected) and set estimated. Examples: search changes → margin of orders that used search (or total web margin × search share); thin descriptions → margin of the treated SKUs; checkout → total web margin. Use the shop's own margin data (Marina: `pos_margin_report`). State the base in the finding text.
- **Effect range:** the card's measured lift, scaled down when transfer is low. Do not invent precision.
  - Card has a measured outcome (A rigor): use it as the high end; low end half of it.
  - Card has no measured lift (most B/C cards; Baymard failure rates are not lifts): leave effect empty. The script sets 1–3% and marks estimated.
- **Estimated:** true when margin data is approximate, or the effect is a default. Never set it false to raise a score.

## 3. Confidence inputs

- **Rigor:** the grade of the evidence behind the outcome claim, from the library. Mixed grades take the outcome-evidence grade, otherwise the lower one. "Policy" means a requirement with no sales evidence.
- **Transfer:**
  - 1.0 — same scale and category (rare).
  - 0.7 — adjacent: specialist retail, parts, B2B.
  - 0.4 — marketplace, fashion, or giant-scale only.
  - Local evidence (the shop's own data shows the problem clearly) can raise transfer one step, except capped cards.

## 4. Effort inputs

- **Newton days:** build + test + rollout, with AI help.
- **Client days:** approvals, content checks, supplier contacts, staff training. Approval of AI content is usually the bottleneck: budget ~1 day per 300 SKUs reviewed, and per-SKU review for safety-critical lines.
- **Run cost €/month:** API, hosting, maintenance. Above 300 €/month raises effort one band.
- Bundle parents carry the shared effort once. Children carry none.
- Library effort hints: S ≈ band 1, M ≈ band 2–3, L ≈ band 4–5. Use them as a sanity check on your days, not as the input.

## 5. Bundles

Known bundles (use when two or more members are active):

| Bundle | Members |
|---|---|
| BND-ATTR Attribute pipeline | CAT-1, CAT-3, CAT-5, SRC-6 (also satisfies LEG-2; no impact credit) |
| BND-QRY Query dictionary | SRC-1, SRC-4, SRC-7 |
| BND-FIT Fitment data | FIT-1, FIT-2, CAT-4, CAT-7 |
| BND-RANK Search ranking | SRC-3, SRC-5, SRC-9 |

SRC-2 (LLM judge) and SRC-9 (interleaving) are enablers: they have no own impact and belong inside a bundle. SRC-2 serves both search bundles; put its effort in the first one built. A single active member is scored as a normal item.

## 6. Tags, measurement, acceptance criteria

- **Origin:** already in client plan · in progress · new · client can do alone.
- **Timing:** fix now · fold into planned migration or rebuild.
- **Proxy metric:** one per item (zero-result rate, attribute completeness, add-to-cart, return rate on treated SKUs, response time).
- **Test design:** randomized SKU-level rollout (OS-7) for catalogue items; before/after with a dated change log for site-wide changes; A/B only for big bets with traffic. Detecting a 10% lift at 3.7% conversion needs ~41,600 users per variant.
- **Acceptance criteria:** measurable, testable, written so the client can sign off. Safety-critical items must say "per-SKU sign-off".

## 7. Behavior lane (unscored)

The purchase-path and choice cards (library §12: PATH-*, BEH-*, and NEWB-n for anything outside it) go in the `behavior` list. `score.py` rejects them from `findings`.

**Why a separate lane.** These ideas have no measured lift for a shop this size. In the € scoring they would take the default 1–3% effect, land in impact band 1 and fall under the "test first" line. That hides them without judging them. The lane shows them as what they are: hypotheses, ranked by how strong the published evidence is and how cheap the change is.

**Two kinds of item.**

- **defect** — something the walk saw broken, blocked or wrong: a wrong total, a covered buy button, a mislabelled step, a signal with no live data behind it. It needs no study and carries no grade. Defects rank first. The first defect under a card takes the card's ID; each further one is NEWB-n.
- **hypothesis** — a change that might move shopper behavior. It carries the library card's grade and a one-sentence hypothesis.

Do not dress a defect as a hypothesis, or a taste judgement as a defect. A defect must show in a screenshot or in `path.json`. Where a button sits, how big it is and what competes with it are layout judgements, never defects.

On a re-run keep every ID, NEWB-n included. A fixed defect stays in the list with status `done`.

**Inputs you choose** (schema in `findings-schema.md`):

- **status** — done / partial / missing / n/a, with evidence, like any card.
- **observation** — what was measured, with numbers. For PATH cards the numbers come from `path.json`. Never estimate a count.
- **hypothesis** — one sentence: "If we change X, then Y moves, because Z."
- **grade** — copy it from the library card; `score.py` rejects any other grade for a library card. NEWB items are C unless `source_url` cites a study.
- **effort** — S (up to 3 person-days), M (up to 10), L (more). Newton plus client days.
- **truth_source** — required for cards marked T (BEH-1, BEH-2, BEH-3, BEH-5, BEH-10), also when the status is `done`: the live shop data that makes the signal true, and how often it refreshes. For BEH-10 name the products and their unit sales over the last 12 months.
- **measure** and **test_design** — one proxy metric, and before/after with a dated log unless traffic allows more.

**What the script does.** It validates the items, ranks active ones (defects by effort; then hypotheses by grade, effort, ID), writes `lane_rank`, lists every active defect in `summary.behavior_defects` and the first seven hypotheses in `summary.behavior_top`. It never computes € for the lane, and it rejects any item that carries a € field.

**Rules.**

- Never move a lane item into `findings` to give it a € figure. If the shop's own data later shows a measured effect, cite that data in the item; it stays in the lane.
- Never present a "Tested and flat" change as a win (library, after §12).
- An idea that needs a banned pattern is dropped, not softened (SKILL.md hard rules 8–10).
- At this traffic the lane cannot be A/B tested. Say so in the report; use before/after with a dated log and the path numbers as proxies.
