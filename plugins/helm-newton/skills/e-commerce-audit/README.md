# E-commerce audit (e-commerce-audit)

Audits a web shop against practices that large e-tailers (Amazon, Booking, Etsy, Zalando, OTTO, Allegro, Instacart and specialist retailers) have published and measured. Produces:

- a **Croatian client report** for the shop's management, and
- an **.xlsx backlog** for Newton d.o.o., with live scoring formulas.

Three lanes: practices scored by € impact and effort; legal gaps, unscored; and the **behavior lane** (since 0.2.0), which counts the purchase path and ranks hypotheses about shopper behavior by evidence, unscored.

Built for Marina Stores first; works for any web shop.

## Components

| Component | Purpose |
|---|---|
| Skill `e-commerce-audit` | The audit workflow. Run it by name only |
| Agent `audit-reviewer` | Mandatory review gate before anything is delivered |
| `scripts/score.py` | Validates findings and computes impact, effort, confidence, priority, quadrant |
| `scripts/build_backlog.py` | Builds the .xlsx (formulas + Settings sheet) and verifies it after recalculation |
| `scripts/catalogue_health.py` | Exact catalogue baseline: thin descriptions, translations, attributes, images, GPSR |
| `scripts/page_checks.py` | schema.org, hreflang, canonical, alt text and GPSR hints from saved HTML |
| `scripts/path_metrics.py` | Purchase path: interactions from landing to checkout per site and device, gap to the best competitor, per-screen comparison, flags for pre-ticked boxes and covered buttons |
| `scripts/visible_counts.js` | Runs in the rendered page: counts what a shopper can see on a screen (links, exits, buttons, buy-button position and cover, fields) |
| `scripts/path_words.json` | The one word list that decides which button is a buy or checkout button, in six languages; the JS carries a copy and a test keeps both equal |
| `scripts/diff_runs.py` | Compares a re-run with the previous backlog |
| `scripts/kappa.py` | Agreement between the LLM search judge and staff labels |

## Usage

Say "run e-commerce-audit" (or `/e-commerce-audit`). The skill asks for the shop, competitors (svb24.com pre-filled for Marina), goals and available data, then runs read-only.

## Safety

Read-only on client systems. Checkout walk stops at the first personal-data form; it goes further only on a staging host the user confirmed, with test data, and never places an order without confirmed payment test mode. Helm tools are limited to an allowlist. No personal data in outputs. Dark patterns are never recommended, and every signal shown to shoppers must be true (truth rule). A blocked site counts as "not checked" only after every access route was tried, including the built-in browser.

## Requirements

Python 3.9+ with `openpyxl`; LibreOffice for recalculation (the xlsx skill's `recalc.py`). Two test groups need more and skip without it: Node.js (word-list parity) and Playwright with Chromium (the rendered-page counter). Tests: `python3 -m unittest discover -s skills/e-commerce-audit/scripts/tests`.

## Updating the evidence

Edit `skills/e-commerce-audit/references/practice-library.md`. Keep card IDs stable. Scoring thresholds live in `scripts/score.py` and the workbook's Settings sheet; change both together and rerun the tests. Cards marked † carry numbers from an abstract or summary: read the full paper, then remove the mark.

## Changes

**0.2.0 (2026-10-08)** — Behavior lane: library §12 (PATH and BEH cards), a "Tested and flat" list, and items that are either a defect (seen broken on the path; ranks first) or a hypothesis (ranked by evidence grade and effort, never in €). Path walk with `path_metrics.py`, `visible_counts.js` and one shared word list (`path_words.json`). Truth rule, real-options rule, wider dark-pattern list. Access ladder for blocked sites, with the built-in browser. Staging checkout walk with test data and `evidence/test_records.md`. Lane-only runs. Helm telemetry on the allowlist. Evidence upgrades for RET-2, CRM-2, REC-1, CHK-4, OMNI-1; new legal card LEG-9. Workbooks gain "Behavior lane" and "Path" sheets; older workbooks still work as the previous run in `diff_runs.py`. The scored lane's math is unchanged.
