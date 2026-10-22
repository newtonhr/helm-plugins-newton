# Data contracts

## findings.json (input to score.py)

```json
{
  "meta": {"shop": "Marina Stores", "url": "https://...", "audit_date": "2026-10-07",
           "languages": ["hr", "en"], "competitors": ["svb24.com"], "data_available": ["Helm"],
           "not_available": ["GA4", "Search Console"]},
  "findings": [ <finding>, ... ],
  "legal": [{"id": "LEG-3", "rule": "...", "checked": "...", "finding": "...", "evidence": "...", "action": "..."}],
  "behavior": [ <behavior item>, ... ],
  "path": [{"metric": "Interactions to first checkout form", "values": {"client desktop": 9, "awn desktop": 6}}],
  "baseline": [{"metric": "...", "value": 0.18, "date": "2026-10-07", "method": "..."}],
  "competitors": [{"feature": "Shipping cost on product page", "values": {"client": "no", "svb24": "yes"}}],
  "not_checked": [{"item": "GA4 funnel", "reason": "no export yet", "effect": "impact bands estimated"}],
  "sources": [{"card": "CHK-1", "source": "Baymard", "url": "https://...", "rigor": "B"}]
}
```

### finding

| Field | Type | Required for | Notes |
|---|---|---|---|
| id | string | all | Library ID (CAT-1), bundle ID (BND-QRY) or NEW-n. Unique |
| title | string | all | Short, English (backlog is internal) |
| kind | "item" / "bundle" / "child" | all | Default "item" |
| bundle | string | child only | Parent bundle ID. Error on any other kind |
| cards | list | optional | Defaults to [id]; bundles get their children's cards |
| status | "done" / "partial" / "missing" / "n/a" | all | Bundle status is derived from children |
| finding | string | all | What was seen, with numbers |
| evidence | string | item, child (required) | URL, screenshot file in evidence/, or saved data query file |
| origin | string | item, bundle | already in client plan / in progress / new / client can do alone |
| timing | string | item, bundle | fix now / fold into migration |
| margin_base_eur | number | active item, child (required) | Estimate when data is missing and set estimated=true |
| effect_low, effect_high | fraction 0–1 | optional | 0.02 = 2%, never 2. Omit both if no measured lift |
| estimated | bool | optional | Set true if margin is approximate |
| rigor | "A" / "B" / "C" / "Policy" / "C until verified" | active item, child | |
| transfer | 0.4 / 0.7 / 1.0 | active item, child | Any other value is an error; capped cards are capped by the script |
| newton_days, client_days | number | active item, bundle | |
| run_cost_month | number | optional | € per month |
| ai_role, data_tools, proxy_metric, test_design, acceptance_criteria, notes | string | item, bundle | |
| safety_critical | bool | optional | Requires "per-SKU" in acceptance criteria (bundles inherit it from children) |

### behavior item (unscored lane)

| Field | Type | Required for | Notes |
|---|---|---|---|
| id | string | all | PATH-n or BEH-n from library §12, or NEWB-n. Unique; never also in `findings` |
| kind | "hypothesis" / "defect" | optional | Default "hypothesis". A defect was seen broken on the path; it ranks first and has no grade |
| title | string | active | Short, English |
| status | "done" / "partial" / "missing" / "n/a" | all | |
| observation | string | active | What was measured, with numbers. PATH numbers come from `path.json` |
| evidence | string | all | `path.json`, screenshot in evidence/, saved page, URL or data query |
| hypothesis | string | active hypothesis | "If we change X, then Y moves, because Z" |
| grade | "A" / "B" / "C" | active hypothesis | The library card's grade (`score.py` rejects any other). NEWB-n is C unless `source_url` is set. Not allowed on a defect. PATH-3 is defect-only |
| effort | "S" / "M" / "L" | active | Up to 3 / up to 10 / more person-days |
| source, source_url | string | optional | Study behind the grade. `source_url` is required for a NEWB-n graded A or B |
| truth_source | string | BEH-1, -2, -3, -5, -10 unless n/a | Live shop data behind the signal, and its refresh rate. Required for `done` too |
| measure | string | active | One proxy metric. No money amount |
| test_design, acceptance_criteria, origin, notes | string | optional | |

Not allowed: `margin_base_eur`, `effect_low`, `effect_high`, `impact_eur`. `score.py` adds `lane_rank` (1 = first; empty for done and n/a).

### path

`path` is `path.json` → `comparison`, copied unchanged: a list of `{"metric": text, "values": {walk: number}}`. Never the whole file. Copy `path.json` → `baseline_rows` into `baseline`.

### Rules for the whole file

Numbers must be JSON numbers, not strings. `findings` may be an empty list only in a lane-only run (the `behavior` list must then have items).

Rules enforced by `score.py`: LEG-* and OS-* are rejected from findings; BEH-*, PATH-* and NEWB-* are rejected from findings and validated in `behavior`; children need an existing bundle; bundles need children; bundle status is derived from its children; enablers scored standalone raise a warning; `path` must be a list of comparison rows.

## catalogue.json (input to catalogue_health.py)

A JSON list, one object per product. Normalise whatever the platform exports into this shape.

```json
{
  "id": "12345",
  "category": "Anchors",
  "revenue_rank": 1,
  "texts": {"hr": {"name": "...", "description": "<p>HTML allowed</p>"}, "en": {"name": "...", "description": "..."}},
  "features": {"weight": "10 kg", "material": "galvanised steel"},
  "images": [{"alt": {"hr": "...", "en": "..."}}],
  "gpsr": {"manufacturer": "...", "eu_responsible": "...", "identifier": "...", "warnings": "..."},
  "safety_critical": false
}
```

`revenue_rank` is optional (1 = best seller); without it the image check uses the first N products. Thin-description share is counted over SKUs that have a description in that language; SKUs with none are reported separately as missing (a translation gap). Attribute completeness counts, per category, the feature keys filled on at least half of the category's products; on re-runs pass `--expected-keys previous_health.json` to freeze those keys.

## labels.csv (input to kappa.py)

`query,product,llm_label,human_label,lang` — labels E / S / C / I (or 3/2/1/0).

## Walk log (input to path_metrics.py)

One JSON file per site and device, written during the path walk: `path_walk_<site>_<device>.json`. The client site is always named `"client"`.

```json
{
  "site": "client", "device": "desktop", "scenario": "known item",
  "start": "home page", "goal": "payment step", "complete": true, "stopped_reason": "",
  "steps": [
    {"stage": "find", "type": "load", "what": "home page"},
    {"stage": "find", "type": "click", "what": "category Sidra", "page_load": true},
    {"stage": "product", "type": "click", "what": "add to cart"},
    {"stage": "cart", "type": "click", "what": "to checkout", "page_load": true, "page": "client_desktop_cart.html"},
    {"stage": "checkout", "type": "fill", "fields": 5, "required": 4, "screen": "personal", "page": "client_desktop_checkout_1.html"},
    {"stage": "checkout", "type": "select", "what": "carrier", "screen": "delivery"}
  ]
}
```

- `browser`: which browser ran the walk and at what size ("headless browser in the workspace, 1280x900"). The report states it.
- `stage`: find / product / cart / checkout, in that order.
- `type`: click, fill (one interaction per field typed; give `fields`, and `required` when known), select (dropdown, radio or checkbox choice), load (a direct page load; not an interaction).
- `page_load: true` on any step that loads a new page. `page` names the saved HTML of the screen the step ends on. `screen` names the checkout screen.
- `goal` is the payment step for the client on staging, and the first personal-data form everywhere else. `complete: true` only when the walk typed its way through checkout to the goal. A walk that stops at the first personal-data form without typing is `complete: false` with `"reached_first_form": true` (every competitor walk). A walk that reached neither is left out of every path-length row.
- Log what a shopper must do, not what you tried, and only steps you performed. Leave out scrolling, cookie-banner clicks and your own mistakes.
- `"screens": [{"name": "cart page", "stage": "cart", "kind": "cart", "counts": {…}}]` holds one `visible_counts.js` result per screen, unedited. The script returns a JSON string: parse it, so that `counts` is an object (the unparsed string is accepted too).
  - `name`: one of `product page`, `cart page`, `cart drawer`, `first form`, `checkout 1` … `checkout 5`, so baseline rows match between runs. A variant adds a condition after a comma: `cart drawer, cookie banner unanswered`.
  - `kind`: what the screen is, one of `product page`, `cart`, `cart drawer`, `guest form`, `login or guest gate`, `login wall`, `address form`, `delivery`, `payment`, `review`. A competitor's screen is compared with the client's screen on the same device only when the kinds are equal; the rest are listed under `not_like_for_like` in `path.json`. A cart or checkout screen without a `kind` raises a warning and is compared with anything.
  - The first screen listed for a stage is the one compared across sites: list the full cart page before a cart drawer.
- Optional `"pages": {"client_desktop_cart.html": "cart"}` names saved HTML that is not on the shortest path, with its stage. Markup counts are hints only.
- The audited shop's walks use `"site": "client"`; without one the script stops with an error.
