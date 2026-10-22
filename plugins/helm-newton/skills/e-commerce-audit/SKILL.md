---
name: e-commerce-audit
description: "This skill should be used only when the user invokes \"E-commerce audit\", \"e-commerce-audit\" or \"/e-commerce-audit\" by name (formerly webshop-admin), to audit a web shop against proven practices from large e-tailers and produce a Croatian client report plus an .xlsx Newton backlog prioritized by impact × effort. Do not trigger on general e-commerce questions.\n"
metadata:
  version: "0.3.0"
---

# E-commerce audit

Audit a web shop (e-tail) against practices that large e-tailers have published and measured. Produce:

1. **Client report** in Croatian, for the shop's management.
2. **Newton backlog** as .xlsx, for Newton d.o.o. to price and build.

The audit has three lanes. The **scored lane** ranks practices by € impact and effort. The **legal lane** lists compliance gaps, unscored. The **behavior lane** counts the purchase path and lists hypotheses about shopper behavior, unscored and ranked by evidence.

Recommend only good practices that Newton can build with AI help, or plain best practices. Never recommend dark patterns, even when they would test positive.

First client: Marina Stores (Lalizas Marina), PrestaShop. Marina-specific steps are marked **[Marina]**.

**The model judges; scripts count.** Never compute scores, bands, quadrants, catalogue metrics or path counts by hand, and never build the workbook by hand.

`SKILL_DIR` below means this skill's base directory (shown when the skill loads). Run scripts as `python3 "$SKILL_DIR/scripts/<name>.py"`. Work in a dedicated run folder; keep all evidence in `evidence/` inside it.

## Files in this skill

| File | Read when |
|---|---|
| `references/practice-library.md` | Step 4. Cards, grades, ground rules, behavior lane (§12), tested-and-flat list, never-cite list, sources |
| `references/scoring.md` | Step 5. How to choose inputs; the math is in `score.py`; §7 for the behavior lane |
| `references/findings-schema.md` | Before writing `catalogue.json`, `findings.json` or a walk log |
| `references/data-sources.md` | Step 3. Methods; access ladder for blocked sites; Helm allowlist for Marina |
| `references/report-template.md` | Step 7. Croatian report structure and tone |

## 0. Hard rules

1. **Read-only.** Never call a write or `propose_*` tool on client systems. Never submit an order.
   - Walk checkout only to the first personal-data form. Do not create accounts, submit forms or tick consent boxes. A real order triggers fiscalisation and stock sync.
   - Exception: on a staging host that the user confirmed at intake, the path walk continues past the first form with test data, as step 3.3 describes. Never do this on a live shop: check the host name on every screen. Never press the final order button unless the user also confirmed payment test mode; with it confirmed, place one test order and record it.
   - Storefront only. Never open the shop's back office in the browser, even if a session is logged in.
   - Competitor shops: browse and add to cart only. Never enter data.
   - [Marina] Helm: allowlisted read-only tools only (`references/data-sources.md`).
2. **Personal data minimised.** Support threads become themes. No customer names, emails or order-level personal data in outputs or evidence files.
3. **Safety-critical lines** (lifejackets, PPE, MED-marked gear, flares, EPIRBs, gas fittings) need per-SKU human sign-off in any AI-content item. `score.py` rejects safety-critical items without it.
4. **No folklore.** Never cite the never-cite list as fact.
5. **Neutral tone.** The shop may already be run or advised by Newton. Findings are opportunities, not failures. Never blame staff or prior vendors.
6. **Evidence or nothing.** Every finding cites a URL, screenshot or saved data query. `score.py` rejects findings without evidence.
7. **Review gate.** Nothing reaches the user before the `audit-reviewer` agent returns READY.
8. **Dark patterns are never recommended:** fake scarcity; countdown timers, even for a real deadline; pre-ticked add-ons; hidden costs; confirmshaming; forced accounts; fake discounts; decoys; invented popularity. They often test positive; that changes nothing.
9. **Truth rule.** Recommend a signal to the shopper (stock, popularity, deadline, seal, price comparison) only when live shop data makes it true at the moment it shows. Name that data in `truth_source`. A deadline is a clock time in plain text. A signal the shop already shows without such data is a defect to report, not a practice done. Ask the client or check the shop's data before you say so; when nobody can confirm either way, list the card in `not_checked`.
10. **Real options only.** Options shown side by side must each be an existing product at its real price, with its own sales, and none may be dominated by another (equal or worse on every listed attribute at an equal or higher price). An option listed so that nobody picks it is banned.
11. **Exhaust access before "not checked".** When a site blocks a tool, work down the access ladder in `references/data-sources.md`, including the built-in browser. Write "not checked" only after every rung failed, and name the rungs tried.

## 1. Intake

Ask once (AskUserQuestion where available). Missing data lowers confidence; it never blocks the run.

- Shop URL, markets and languages.
- **Competitors to benchmark — always ask.** [Marina] Pre-fill svb24.com; ask for others.
- Client's 12-month goals, if known.
- Data available: platform access, GA4 export, Search Console export, return reasons, support inbox. If GA4 or Search Console is missing, continue and list it under "not checked".
- Staging host where the path walk may pass the first form with test data? If yes, confirm it is cut off from fiscalisation, POS and stock sync, and customer email. Payment test mode? Default: neither.
- Previous backlog .xlsx and previous `health.json`, if this is a re-run.

Report language: Croatian unless told otherwise. Set up a task list for the run.

## 2. Context load

Reuse existing work; do not re-audit it.

- [Marina] Read memory `/areas/axon-marina-stores.md`. Search past chats for: Axon master plan, SEO/AI audit, PrestaShop 9 migration, My Boat, AI search. List work already planned or in progress.
- Other clients: ask for prior audits and roadmaps.

This list sets each finding's **origin** tag.

## 3. Collect

Follow `references/data-sources.md`. Run collectors as parallel sub-agents, except browser work: one browser session is shared, so run browser collectors one at a time. Collectors return findings with evidence, and save every data query result they rely on (as a small .json or .csv, no personal data) in `evidence/`, so the reviewer can check it.

1. **Catalogue baseline.** Normalise the catalogue export to `catalogue.json`, then run:
   `python3 "$SKILL_DIR/scripts/catalogue_health.py" catalogue.json --langs hr,en,... -o health.json`
   On a re-run add `--expected-keys previous_health.json` so attribute completeness stays comparable.
2. **Storefront walk** in a real browser, desktop and mobile. Sample: top 10 revenue SKUs + 10 random, per language; home; 3 categories; cart; checkout to the first personal-data form. Screenshot every finding into `evidence/`.
3. **Path walk** in a real browser, one site at a time. It measures the road from landing to payment.
   - Scenario "known item": load the home page, reach one in-stock top-10 product through category navigation, open its page, add it to the cart, start checkout. Take the shortest route the site offers: when a drawer or pop-up leads straight to checkout, use it, and review the full cart page separately (name its saved HTML under `pages` in the walk log). Use the same scenario and a like product on every site, and write the browser that ran the walk into the log's `browser` field.
   - Devices: desktop (1280 px wide) and mobile (about 390 px wide). When the user's Chrome window cannot be resized, use the built-in browser's mobile preset or a headless browser in the workspace. Read-only steps may run in the headless browser; say in the log which browser ran which walk.
   - Name the audited shop's walks `"site": "client"` and each competitor by its name; `path_metrics.py` needs that to find the gap.
   - Client: stop at the first personal-data form and set `reached_first_form`. On a confirmed staging host, continue through every screen to the payment step with test data: name "Test Audit", email `audit@example.com`, an obviously fake phone number, street "Test Audit 1" with a valid postcode. Log only steps you performed; describe a screen you saw but did not complete in `stopped_reason` and in the item's observation. If the session's own safety check blocks a form submit, stop there, record it, and ask the user to click that one step. Submit the checkout forms as a guest and tick only the boxes the shop requires; never register an account. Stop before the final order button unless payment test mode is confirmed. Write every record the walk created (guest customer, carts, orders) to `evidence/test_records.md`, with the host and time. No staging walk, no file.
   - Competitors: stop at the first personal-data form. Follow the access ladder when a site blocks.
   - Answer the cookie banner with the most private choice and do not log that click. On the client only, add one extra pass per device as a new visitor: open the product page, leave the banner unanswered, run `visible_counts.js`, try add-to-cart, and run it again on the cart drawer or cart. Store these as screens named "…, cookie banner unanswered".
   - Log each interaction a shopper needs in `path_walk_<site>_<device>.json` (schema in `findings-schema.md`). Screenshot the product page, the cart and each checkout screen at both widths into `evidence/`.
   - On each of those screens run `scripts/visible_counts.js` in the rendered page (pass the file's text to the browser's script tool, or `page.evaluate`) and store its result under `screens` in the walk log, with a `name` and a `kind` from the lists in `findings-schema.md`. It counts what a shopper can see: links and exits, buttons, where the buy or checkout button sits and whether something covers it, fields, pre-ticked boxes. If `scrolled_from` in the result is not 0, run the script a second time and store the second result: the page had not yet reacted to the jump to the top. On a page that scrolls inside a box and not in the window, scroll that box to the top first. Never count these by eye or with your own script. A count of 0 primary buttons is a word match that failed or a real gap: look at the screenshot before you file it.
   - Sites open checkout differently: one shows a guest form at once, another a login-or-guest gate. Give each first screen its `kind`. The script compares screens of the same kind only and lists the rest under `not_like_for_like`; say so in the report instead of comparing them yourself.
   - Optionally save the HTML of the cart and checkout screens in `pages/path/`. Their markup counts include everything the page hides with CSS, so they are hints only.
   - Run `python3 "$SKILL_DIR/scripts/path_metrics.py" --walks path_walk_*.json --pages-dir pages/path --date <audit date> -o path.json`.
   - `pre_ticked_flags` in `path.json`: a pre-ticked marketing or add-on box breaks hard rule 8. Report it (LEG-6 for marketing consent). A pre-ticked "same address for the invoice" box is fine.
   - `covered_primary_flags`: judge each by its button text. A button behind an open drawer is covered on purpose. A buy or checkout button under a cookie banner or chat bubble is a defect (PATH-3).
   - For the lane, also note on one category page how many options show before any filter, and on the product page which true signals exist (stock, popularity, dispatch cut-off, seal) and which payment options are named.
   - [Marina] Call `telemetry_funnel` for step drop-off and field-level abandons. Empty lists mean no data.
4. **Page checks.** Save the HTML of sampled pages (Helm `fetch_storefront_url` or browser), then run:
   `python3 "$SKILL_DIR/scripts/page_checks.py" --dir pages/ -o pages.json`
   GPSR hints come with snippets; confirm each by eye. `found: false` is not evidence of absence: a LEG-2 gap must rest on the `catalogue_health.py` GPSR fields or on a screenshot.
5. **Search test.** Real queries first (on-site search log, Search Console, support emails); synthetic queries fill gaps: product names, part numbers, abbreviations (SS, A4, 316, M8, 12V), symptoms ("bilge pump not starting"), the same queries in each language. ~50 per language. Record zero-result queries. Judge relevance with an LLM (Exact / Substitute / Complement / Irrelevant). Ask staff to label ~100 pairs for Croatian when possible, then run `python3 "$SKILL_DIR/scripts/kappa.py" labels.csv --lang hr`. Below 0.7, call relevance scores directional.
6. **Commerce data:** margins by category, AOV, top movers, dead stock, stockouts, return reasons, support themes. Margins feed the € inputs. [Marina] `telemetry_overview` also returns on-site searches and zero-result terms for the search test.
7. **Technical:** schema.org Product/Offer with shipping and returns, hreflang and canonicals, faceted-navigation crawl control, Merchant Center feed quality if accessible, WCAG 2.1 AA basics, cookie consent before analytics tags, lab speed (LCP, INP, TTFB) on 5 page types — "lab only" without field data. For depth invoke `marketing-skills:seo-audit`, `marketing-skills:schema-markup`, `design:accessibility-review`, `marketing-skills:page-cro`; map their output to library IDs. Behavior and layout ideas from those skills go to the behavior lane and pass the same rules.
8. **Competitor benchmark:** same checklist on each named competitor, no form entry. Keep only differences that matter. A blocked competitor goes down the access ladder (hard rule 11); log every rung in `evidence/access_log.md`.
9. **Baseline rows.** Take `health.json` → `baseline` and `path.json` → `baseline_rows`, then add: zero-result rate and relevance per language, lab speed per page type, return rate and pre-sale questions per week when available. Date every row.

## 4. Match

Read `references/practice-library.md`. For every card set status **done / partial / missing / n/a** with evidence. Findings outside the library get IDs NEW-1, NEW-2… and rigor C unless an outside A/B source is cited. OS-* cards are methods, not findings. Legal-lane items (LEG-*) go in the `legal` list, never in `findings`. On a re-run keep previous IDs.

**Behavior lane.** Give every PATH-* and BEH-* card (library §12) a status with evidence too, and write each one into the `behavior` list, never into `findings`. An active item states the observation with numbers, a one-sentence hypothesis, the card's grade, effort S/M/L and one measure. Something the walk saw broken, blocked or wrong (a wrong total, a covered buy button, a mislabelled step, a signal with no live data behind it) is `kind: "defect"`: no hypothesis, no grade, and it ranks first. A layout judgement (position, size, colour, competing buttons) is never a defect. A card you could not check gets no item: list it in `not_checked` with the reason. Ideas outside §12 get NEWB-1, NEWB-2… at grade C. Before writing any layout idea, check the "Tested and flat" list: a change on it is not filed at all, neither as a hypothesis nor as a defect. Drop any idea that needs a banned pattern (hard rules 8–10).

**Lane-only run.** When the user asks only for the purchase path or behavior lane, run steps 1, 2, 3.3, the Behavior-lane matching above, 5, 7, 8 and 9 with `findings` empty. The report then has the lane-only sections that `report-template.md` lists. Say in the report and in the delivery message that the scored and legal lanes were not run.

Use the known bundles (BND-ATTR, BND-QRY, BND-FIT, BND-RANK) when two or more members are active. A bundle is a parent row; members are `child` rows. A single active member is a normal item.

## 5. Score

1. Read `references/scoring.md` and set inputs. Every active item and child needs a margin base: when data is missing, estimate it (e.g. total web margin × share affected) and set `estimated: true`.
2. Write `findings.json` (schema in `findings-schema.md`), including `meta`, `legal`, `behavior`, `path`, `baseline`, `competitors`, `not_checked`, `sources`. Copy `path.json` → `comparison` into `path`, and `path.json` → `baseline_rows` into `baseline`, both unchanged. Lane inputs: `scoring.md` §7.
3. Run `python3 "$SKILL_DIR/scripts/score.py" findings.json -o scored.json`. Fix every ERROR and rerun. Read every WARNING; fix inputs where it shows a mistake. The script also validates and ranks the behavior lane; it never gives the lane a € figure.
4. **Re-run only:** `python3 "$SKILL_DIR/scripts/diff_runs.py" previous_backlog.xlsx scored.json`
5. Report content comes from `scored.json`: `summary.report_quick_wins` is the Brze pobjede list; `summary.test_first` items never appear there. `path`, `summary.behavior_defects` and `summary.behavior_top` fill the report's purchase-path section, in that order.

## 6. Validate with the client

Offer a 30-minute call with client staff before the final report: supplier content rights, approval capacity (adjust client days), labels for the search judge. If declined, list it under "Što nije provjereno". After any input change, rerun steps 5.3 and 5.4.

## 7. Build outputs

1. **Backlog:**
   - `python3 "$SKILL_DIR/scripts/build_backlog.py" build scored.json -o <shop>-backlog-<date>.xlsx`
   - Recalculate with the xlsx skill's `recalc.py` (claude.ai path: `python3 /mnt/skills/public/xlsx/scripts/recalc.py <file>.xlsx 60`).
   - `python3 "$SKILL_DIR/scripts/build_backlog.py" verify scored.json <file>.xlsx`
   - Ship only when recalc reports zero errors and verify reports `ok`.
2. **Client report:** follow `references/report-template.md`. Write it first as `report.md` in the run folder, then create the doc from it (docs connector / Docs artifact type when available; otherwise .docx via the docx skill).

## 8. Review gate

Start the `audit-reviewer` agent (from this plugin). Give it the paths to: `scored.json`, the .xlsx, `report.md`, `path.json` with the walk logs and `pages/path/`, the `evidence/` folder (with `access_log.md` and `test_records.md`), and `SKILL_DIR`. Say when the run is lane-only. Fix everything it flags, rerun the scripts if inputs changed, update the doc from `report.md`, and send the fixes back for confirmation. Deliver only after READY.

## 9. Deliver

Short message: report link, the .xlsx attached, "review passed", what was not checked (with the access routes tried for any blocked site), and the contents of `evidence/test_records.md` when a staging walk ran. No recap. If the user asks, pass chosen items to `axon-sow-architect` for SOW and pricing.
