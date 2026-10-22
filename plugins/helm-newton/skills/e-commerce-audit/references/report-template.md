# Client report (Croatian)

## Tone rules

- Plain, neutral Croatian. Short sentences, one idea each. Formal "Vi".
- Croatian number format: 10.000 €, 2,5 %, 7. listopada 2026.
- English term in parentheses on first use only: "stopa pretraga bez rezultata (zero-result rate)". No calques.
- "Prilike" (opportunities), never "nedostaci" (failures). Never blame staff or prior vendors. One exception: a defect on the purchase path is named plainly as "greška", with what was seen and what "fixed" means, and still without blame.
- No Newton prices (what the work would cost), no Newton effort figures, no internal scores. Use € impact bands and plain words for confidence ("snažni dokazi", "umjereni dokazi", "hipoteza za testiranje").
- Cite the source company and evidence strength for each recommendation, briefly.
- Every claim traceable to `scored.json` or evidence. No folklore statistics.
- Behavior-lane items are hypotheses. Write "pretpostavka" and "očekujemo", never "dokazano povećava". Give a study figure only when the library card has no † mark; never promise that figure for this shop.

## Sections

1. **Sažetak** — one page. 3–5 biggest opportunities with € bands. One sentence on method and data limits.
2. **Što već dobro radi** — practices found done. Short list.
3. **Usklađenost** — legal-lane items found: rule, what was checked, what to do. Not ranked. Placed above all recommendations.
4. **Brze pobjede** — `summary.report_quick_wins` from `scored.json`, max 10. For each: what, why (source company, evidence strength), how success is measured. Never include "test first" items.
5. **Plan: Sada / Sljedeće / Kasnije** — Sada = quick wins; Sljedeće = big bets with strong evidence; Kasnije = big bets that need a test first. Show bundles as one line each.
6. **Put do kupnje i ponašanje kupaca** — three parts, after an opening line that says which shop version was walked (live or pre-launch), with which product and category, on which devices, and against which competitors.
   - *Put u brojkama:* the `path` rows from `scored.json` as one small table (client desktop, client mobile, each competitor), plus the gap to the best competitor (`path.json` → `gaps_to_first_checkout_form`). State where each walk stopped and which browser ran it. A cell the script left out is "nije usporedivo" when `path.json` → `not_like_for_like` names it, and "nije mjereno" otherwise; add one sentence that says what each site's first checkout screen is. Never compare screens of different kinds in the text.
   - *Uočene greške na putu do kupnje:* every item in `summary.behavior_defects`, in that order. For each: what was seen, where (screen and device), and what "fixed" means. No hypothesis wording: these are faults, stated plainly and without blame.
   - *Pretpostavke za provjeru:* the items in `summary.behavior_top`, in that order, max 7. For each: what was observed (with the number), the hypothesis, evidence strength in plain words (A = "snažni dokazi iz terenskih pokusa", B = "umjereni dokazi", C = "pretpostavka bez terenskih dokaza"), and how it will be measured. Say once that the shop's traffic does not allow A/B tests, so each change is measured before and after.
   - No € bands in this section. Items done well go in section 2.
7. **Usporedba s konkurencijom** — key differences vs named competitors, with screenshots.
8. **Tjedni pokazatelji** — 5–8 input metrics with today's baseline values. Include one path metric.
9. **Što nije provjereno** — missing data (e.g. GA4, Search Console), sites that stayed blocked after every access route was tried, where each path walk stopped, declined validation call, and how this affects confidence.
10. **Izvori** — linked sources.

On a re-run, add **Napredak od prošle analize** after Sažetak: items improved, regressed, and baseline changes (from `scored.json` → `diff`).

## Useful Croatian terms

| English | Croatian |
|---|---|
| Quick win | brza pobjeda |
| Product page | stranica proizvoda |
| Checkout | završetak kupnje (naplata); "blagajna" only when quoting the shop's own label |
| Cart drawer | bočni prikaz košarice |
| Path walk | prolazak kroz kupnju |
| POS | maloprodajni sustav (POS) |
| Trust seal | oznaka povjerenja |
| Search with no results | pretraga bez rezultata |
| Attribute completeness | potpunost atributa |
| Return rate | stopa povrata |
| Proxy metric | posredni pokazatelj |
| Randomized rollout | nasumično uvođenje po proizvodima |
| Purchase path | put do kupnje |
| Interaction (click, field, choice) | radnja kupca (klik, polje, odabir) |
| Hypothesis | pretpostavka |
| Defect on the purchase path | greška na putu do kupnje |
| Low-stock signal | oznaka niske zalihe |
| Popularity signal | oznaka najprodavanijeg |
| Pay after delivery | plaćanje nakon isporuke (po računu) |
| Before/after measurement | mjerenje prije i poslije |

## Lane-only report

When only the behavior lane ran (`findings` is empty), the report has these sections, in this order:

1. **Sažetak** — what was walked, the three most important defects and hypotheses, and one sentence saying that the scored and legal lanes were not run.
2. **Put do kupnje i ponašanje kupaca** — section 6 above, in full.
3. **Što nije provjereno** — every `not_checked` row.
4. **Izvori** — the studies behind the hypotheses listed.

No € impact figure or band appears anywhere in a lane-only report. Shop prices quoted as evidence of a defect are fine.
