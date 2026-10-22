# Practice library (v0.3, 2026-10-08)

Cards for the match step. Each card is a practice published or measured by a large e-tailer, adapted for a mid-size, low-traffic, multilingual specialist shop. Grade = rigor of the source (A/B/C/Policy). Transfer is set per shop (see scoring.md). Effort is a hint (S/M/L). Default impact 1–5 is a starting point only; the € band from the shop's own margins replaces it.

Update this file when new evidence arrives. Keep IDs stable; add new cards with new IDs.

**† = the numbers come from an abstract or a press summary, not the full paper.** Read the full text before quoting a † number in a client report. Until then, say "published field evidence points this way" and give no figure.

## Contents
- Ground rules
- 1 Catalogue and content (CAT)
- 2 Search and discovery (SRC)
- 3 Fitment (FIT)
- 4 Product page and trust (PDP)
- 5 Cart, checkout, recommendations (CHK, CRM-2, REC)
- 6 Returns, retention, B2B (RET, CRM-1, B2B)
- 7 Service and assistants (SVC)
- 8 Discoverability (DSC, SEO)
- 9 Omnichannel, merchandising, speed (OMNI, MER, SPD)
- 10 Operating system (OS) — methods, not findings
- 11 Legal lane (LEG) — unscored, goes in the `legal` list
- 12 Purchase path and choice (PATH, BEH) — unscored, goes in the `behavior` list
- Tested and flat — changes that large test sets found near zero
- Never cite as fact
- Key sources

### Ground rules

1. Other companies' wins are hypotheses. Published idea success rates run 8–33% (Kohavi, Deng, Vermeer, KDD 2022).
2. Fix data, speed and basics before ML.
3. Self-selected assistant stats are not lift.
4. The shop is liable for what its AI says (Moffatt v Air Canada, 2024). AI answers only from the shop's own data, with a human one click away.
5. No dark patterns. In 2019 six hotel-booking sites, Booking.com among them, gave the UK CMA formal commitments not to give a false impression of availability or popularity (the CMA made no finding of a breach).
6. Dark patterns work; that is why rule 5 exists. Hiding fees until checkout raised spend about 21% on StubHub (Blake et al. 2021 †). Mild dark patterns more than doubled enrolment in a US experiment (Luguri & Strahilevitz 2021 †). "It tests positive" never makes a pattern acceptable.
7. **Truth rule.** A signal shown to the shopper (stock level, popularity, deadline, seal, price comparison) must come from live shop data and be true at the moment it is shown. No invented numbers, no ticking timers, no signal that stays up after it stops being true.
8. **Real options only.** Every option shown side by side must be an existing product at its real price, with its own sales. No option shown may be dominated: equal or worse on every listed attribute at an equal or higher price than another option shown. A decoy (an option listed so that nobody picks it) is banned, whatever the intent is called.
9. Grading a vendor's test set. A vendor's own meta-analysis of randomized A/B tests (Qubit 2017) is grade B on its own. It supports grade A only together with an independent randomized study that points the same way.

### 1 Catalogue and content

| ID | Practice | Evidence | Grade | AI role | Effort | Def. impact | Measure |
|---|---|---|---|---|---|---|---|
| CAT-1 | Write descriptions for thin listings first; leave rich ones alone | Fang et al. 2025 RCT, large marketplace: overall +2.1% sales; +6.5% for listings < 50 words (post-hoc, English-only subgroup); returns −3.9% | A | LLM drafts from supplier data; human approves | S | 4 | % SKUs < 50 words; OS-7 rollout |
| CAT-2 | Translate titles, descriptions, specs into target EU languages | Brynjolfsson, Hui & Liu, *Mgmt Science* 2019: MT quality upgrade (EN↔ES, US→LatAm) +10.9% exports. Not translation vs none; transfer to EU specs unproven | A | MT/LLM + glossary; native spot-check | M | 3 (5 only if Search Console shows foreign demand) | Coverage %; sales by country |
| CAT-3 | Extract structured attributes from supplier PDFs, labels, images | ExtractGPT ~85% F1; Instacart PARSE +10% recall with images; Walmart two-LLM verifier (accuracy, not outcome) | B | Extractor + verifier LLM; confidence gate; human queue | M | 4 | Completeness per category |
| CAT-4 | "Fits / Requires / Included" block on product pages | Baymard: users leave rather than guess; 44% of sites fail compatibility search | B | Extract from datasheets | M | 4 | % SKUs with block; compatibility questions |
| CAT-5 | Attribute completeness as quality and ranking signal | bol.com partner docs | B | LLM scores gaps | S | 3 | Completeness trend |
| CAT-6 | Multilingual alt text and image tags | Decathlon via AWS blog | C | Vision LLM batch | S | 2 | % images with alt text |
| CAT-7 | Cross-reference table OEM number → equivalents | RockAuto, AutoDoc | B | LLM extracts; human approves every match | L | 4 | Part-number search success |
| CAT-8 | Special-order long tail from supplier price lists, honest lead times | Defender, Fisheries Supply | B | LLM normalises titles | M | 3 | Special-order revenue |
| CAT-9 | Expert guides linked to product bundles | Thomann portals, AutoDoc manuals, West Advisor | B | AI drafts; named technician signs off | M | 3 | Guide → cart rate |

### 2 Search and discovery

| ID | Practice | Evidence | Grade | AI role | Effort | Def. impact | Measure |
|---|---|---|---|---|---|---|---|
| SRC-1 | Synonym, abbreviation, translation dictionary for zero-result and frequent queries | Instacart LLM rewrites: coverage 50→95%, tail complaints −50%; Fang: query rewrite +2.9% sales; Baymard: 54% of sites fail abbreviations | A | Batch LLM aliases | S | 5 | Zero-result rate |
| SRC-2 | LLM-as-judge for search relevance, re-run after each change (enabler) | Zalando ~$250/run; Allegro kappa 0.59–0.69 | B | Judge calibrated on staff labels | S | enabler | Relevance per language |
| SRC-3 | Hybrid keyword + semantic search | Amazon semantic search; Etsy +2.63% site-wide conversion | A | Multilingual embeddings | M | 4 | Search conversion |
| SRC-4 | Parse queries into category + filters | bol.com; Baymard feature-query failures 39% | B | LLM/rules | M | 3 | Refinement rate |
| SRC-5 | Boost products bought after a query | Amazon +3% revenue (B); OTTO A/B +0.56% revenue (A, not transferable at low volume) | A | Query→purchase table | M | 2 (needs volume) | Search conversion |
| SRC-6 | Intent tags per SKU for facets and search | Amazon COSMO +0.7% sales | A | LLM tags | M | 3 | Facet use |
| SRC-7 | Map symptom queries to products | Baymard: 37% of sites fail | B | LLM mapping | S | 3 | Symptom query success |
| SRC-8 | Tooltips explaining technical filters (WLL, IPX7, NMEA 2000) | Baymard: 62% don't explain | B | LLM drafts | S | 2 | Filter use |
| SRC-9 | Interleaving to compare rankings on low traffic (enabler) | Amazon, Airbnb | A | — | M | enabler | Win rate |

### 3 Fitment

| ID | Practice | Evidence | Grade | AI role | Effort | Def. impact | Measure |
|---|---|---|---|---|---|---|---|
| FIT-1 | Saved profile (vehicle/boat/engine) → fits / doesn't fit / unknown | Amazon Garage; AutoDoc; Baymard B2B: 6 of 6 sites fail compatible parts | C | LLM builds fitment table; human approval | L | 5 | Fitment coverage; "doesn't fit" returns |
| FIT-2 | Service kits per engine model | Euro Car Parts | B | LLM assembles kits | M | 4 | Kit sales; AOV |

### 4 Product page and trust

| ID | Practice | Evidence | Grade | AI role | Effort | Def. impact | Measure |
|---|---|---|---|---|---|---|---|
| PDP-1 | Shipping cost and delivery date on product page | Baymard: 64% look before add-to-cart; 43% of sites hide it | B | Rules from stock + lead time | S–M | 5 | Add-to-cart; promise hit rate |
| PDP-2 | Honest live stock and dispatch time | SVB (BOOTE shop test winner) | B | — | S | 3 | Stock accuracy |
| PDP-3 | Reviews only from real orders; post-delivery requests; keep negatives | Amazon integrity; Thomann; EU Omnibus | B | AI drafts requests | S | 4 | Reviews per top SKU |
| PDP-4 | AI summary of verified reviews | Amazon 2023 | B | LLM per language | S | 2 | — |
| PDP-5 | Respond to negative reviews; feed causes into fixes | Decathlon; Baymard: 87% never respond | B | LLM clusters, drafts | S | 3 | Response rate |
| PDP-6 | Product FAQ from support and reviews, with FAQ schema | Amazon Q&A; OTTO | B | LLM drafts; staff approve | S | 3 | Pre-sale questions |
| PDP-7 | Consistent title format per category | Bing result doesn't transfer; Fang AI ad titles −4.5% (n.s.) | C | LLM normalises | S | 1 | List → PDP clicks |
| PDP-8 | Comparison widget ("best for 6–8 m boat") | Amazon Help Me Decide (no metrics) | B | LLM grounded in attributes | M | 2 | Use |
| PDP-9 | ≥ 3 images incl. scale and in-use | Baymard product-page benchmark | B | Vision LLM flags gaps | S–M | 3 | % top SKUs ≥ 3 images |

### 5 Cart, checkout, recommendations

| ID | Practice | Evidence | Grade | AI role | Effort | Def. impact | Measure |
|---|---|---|---|---|---|---|---|
| CHK-1 | Guest checkout, total cost early, returns policy from cart, fewer fields | Baymard US survey: extra costs 40%, forced account 18%, long checkout 17% | B | AI audits flow | S | 5 | Checkout completion |
| CHK-2 | Express wallets | Shopify-commissioned study | C | — | S | 3 | Payment-step drop-off |
| CHK-3 | Local payment methods per market | Baymard survey (verify figure) | C | — | S | 2 | Drop-off by country |
| CHK-4 | Free-shipping threshold from AOV and margin | Vendor evidence. Mixed test data: shipping offers work best on product and checkout pages (Miller & Hosanagar †); free-delivery tests averaged −0.2% revenue per visitor (Qubit, 65 tests) | C | Model from orders | S | 3 | AOV |
| CRM-2 | Abandoned-cart email, consent-gated | Abandonment-recovery tests: +1.1% revenue per visitor (Qubit, 105 tests, 95% interval 0.4–1.7) | B | LLM copy | S | 2 | Recovery rate |
| REC-1 | Complements on cart and product page | Amazon item-to-item CF (method); recs mostly shift clicks (Sharma 2015); recommendation tests +0.4% revenue per visitor (Qubit, 119 tests) | B | Co-purchase + LLM complements | S–M | 3 | Attach rate; AOV |
| REC-2 | Similar/compatible items, rule-checked | Airbnb similar listings | A | Embeddings + rule check | M | 3 | OOS recovery |
| REC-3 | Substitutes when out of stock | Amazon ESCI (dataset, not outcome) | B | LLM labels | S | 3 | OOS exits |

### 6 Returns, retention, B2B

| ID | Practice | Evidence | Grade | AI role | Effort | Def. impact | Measure |
|---|---|---|---|---|---|---|---|
| RET-1 | Mine return reasons; fix content behind top 50 returned SKUs | Zalando size advice (observational, B); Fang −3.9% returns (A, marketplace) | A | LLM clusters | S | 4 | Return rate on fixed SKUs |
| RET-2 | Generous returns and warranty as trust signal | Thomann; meta-analysis of 21 papers: lenient policies raise purchases more than returns, longer windows lower return rates (Janakiraman, Syrdal & Freling 2016 †) | B | — | S | 3 | Conversion on covered lines |
| CRM-1 | Seasonal kit reminders; soft opt-in, opt-out in every message | Amazon S&S (C); Stanford name-in-subject +31% leads (A) | C | LLM kits from purchases | S–M | 3 | Repeat rate |
| B2B-1 | Customer-group prices, volume tiers on product page, VAT-ID checkout | Amazon B2B (C); Baymard B2B (B) | B | — | S | 4 | B2B revenue share |
| B2B-2 | Saved/shareable quote carts, quick reorder | Euro Car Parts; Baymard B2B | B | Optional | M | 3 | B2B repeat orders |

### 7 Service and assistants (build in this order)

| ID | Practice | Evidence | Grade | AI role | Effort | Def. impact | Measure |
|---|---|---|---|---|---|---|---|
| SVC-1 | Staff reply assistant | NBER w31161: +14% resolved/hour, +34% novices | A | LLM drafts, staff send | S | 4 | Response time |
| SVC-2 | Live translation for chat/email | Fang: +5.2% satisfaction | A | MT | S | 3 | Non-HR CSAT |
| SVC-3 | Pre-sale question bot, human handoff, out of hours | Fang: +16% vs no service; Klarna reversal 2025 | A | RAG; refuses when unsure | M | 3 | Answered; handoff rate |
| SVC-4 | Full shopping assistant ("will this fit?") | Rufus, Zalando, West Marine — self-selected | C | RAG + fitment | L | 3 | Holdout only |

Guardrails for all customer-facing AI text (SVC-3/4, PDP-4, PDP-6, PDP-8, CAT-1): answer only from retrieved shop text; never promise price, warranty or refund; log everything; disclose AI (LEG-7); never write "AI-powered" in product copy.

### 8 Discoverability

| ID | Practice | Evidence | Grade | AI role | Effort | Def. impact | Measure |
|---|---|---|---|---|---|---|---|
| DSC-1 | Complete Merchant Center feed (GTIN, brand, shipping, returns) | Google AI optimisation guide 2026; ChatGPT Shopping uses feeds | Policy | LLM fills gaps | S–M | 4 | Feed errors |
| DSC-2 | schema.org Product/Offer with shipping and returns | Same | Policy | Generated | S | 3 | Rich-result coverage |
| DSC-3 | AI-answer visibility is a by-product of clean data, not a channel | 973-shop study: ChatGPT ~0.2% of sessions (observational) | B | — | — | framing | AI referral share |
| SEO-1 | hreflang, canonicals, facet crawl control | Google Search Central | Policy | AI audits templates | S–M | 3 | Index coverage |

### 9 Omnichannel, merchandising, speed

| ID | Practice | Evidence | Grade | AI role | Effort | Def. impact | Measure |
|---|---|---|---|---|---|---|---|
| OMNI-1 | Store stock online; click-and-collect | Gallino & Moreno 2014 †: after launch at a housewares chain, online sales fell near stores while store sales and visits rose by more (quasi-experiment; direction verified 2026-10-08, sizes not) | B | — | M | 4 | Total sales, web + store; C&C orders |
| MER-1 | Seasonal merchandising pages | Hypothesis | C | LLM pages | S | 2 | Seasonal revenue |
| SPD-1 | Performance audit (cache, images, modules, CWV) | Bing +0.6% revenue per 100 ms; Booking latency −0.5% conversion | A | AI fix list | M | 3 | LCP, INP, TTFB |
| SPD-2 | AI widgets load async, never block render | Booking 150 models | A | — | S | guardrail | Page weight |

### 10 Operating system (how the shop decides)

| ID | Practice | Use |
|---|---|---|
| OS-1 | 1-page PR/FAQ per proposal (Amazon) | Required for effort ≥ 4 |
| OS-2 | Weekly input metrics (Amazon WBR) | Report: Tjedni pokazatelji |
| OS-3 | Experiment register (Booking) | Backlog doubles as register |
| OS-4 | Low-traffic measurement: proxies, before/after, LLM judging, interleaving | Every item |
| OS-5 | One change at a time, dated log (Etsy) | Items are single-hypothesis |
| OS-6 | Fake-door or remove-it test before big builds (Booking) | Before L items |
| OS-7 | Randomized SKU-level rollout | Default for catalogue items |
| OS-8 | Dated baseline snapshot | Baseline step (catalogue_health.py) |

### 11 Legal lane (unscored, reported above quick wins)

Verify every date and threshold against current law before the report goes out. Use the hr-zakonodavstvo skill or official sources.

| ID | Rule | Check |
|---|---|---|
| LEG-1 | European Accessibility Act (HR law, from 28 Jun 2025) | WCAG 2.1 AA; accessibility statement; microenterprise exemption |
| LEG-2 | GPSR Art. 19 | Manufacturer, EU responsible person, identifier, warnings on every offer |
| LEG-3 | Omnibus prior-price rule | Discounts show lowest price of previous 30 days |
| LEG-4 | CRD withdrawal function (Art. 11a) | Withdrawal button; confirm application date |
| LEG-5 | Cookies and consent | Analytics and marketing tags behind valid consent |
| LEG-6 | ePrivacy for CRM email | Soft opt-in basis; opt-out in every message |
| LEG-7 | EU AI Act Art. 50 | AI chat disclosed; synthetic content labelled; confirm status |
| LEG-8 | Omnibus review disclosure | Shop states how reviews are verified |
| LEG-9 | Consumer credit for pay-later and instalment offers (EU Directive 2023/2225 and its Croatian transposition) | Before BEH-4: who is the creditor, which exemptions apply, what must be disclosed; confirm scope and dates with counsel |

### 12 Purchase path and choice (behavior lane)

These cards go in the `behavior` list, never in `findings`. They are not scored in €: the lane ranks defects first, then hypotheses by grade and effort (scoring.md §7). Each active hypothesis states an observation with numbers, a hypothesis and a measure. The path numbers come from `path_metrics.py`, not from judgement.

The grade says how strong the study is, not how well it transfers to a marine shop. Name the study's setting in the item's `source` ("restaurants", "ticketing platform", "consumer mail order") so the report can say it.

Something seen broken, blocked or wrong on the path is a `defect`, not a hypothesis: it has no grade and ranks first. The first defect under a card takes the card's ID; each further one is NEWB-n. A signal the shop already shows that is not backed by live shop data, and any ticking timer, is a defect too. "Not backed" needs a check: ask the client or look at the shop's data. When nobody can confirm either way, the card goes to `not_checked`, not to the defects.

Cards marked **T** fall under the truth rule: the item needs `truth_source`.

| ID | Practice | Evidence | Grade | Effort | Measure | Limits |
|---|---|---|---|---|---|---|
| PATH-1 | Count interactions from landing to payment; remove steps and fields that add nothing | One-click buying: +28.5% spend over 15 months among 977 adopters (Unal & Park 2023 †, quasi-experiment, one Asian retailer). No randomized study of step count was found | B | S–M | Interactions to first checkout form; checkout fields typed; cart→checkout rate | Adopters chose one-click themselves. CHK-1 covers what the form asks; PATH-1 covers path length |
| PATH-2 | Saved details and express checkout for returning customers | Same study as PATH-1 | B | M | Repeat-order share; interactions for a logged-in reorder | EU card payments need strong customer authentication, so wallets (CHK-2) are the practical route |
| PATH-3 | The buy and checkout buttons exist, work, and nothing covers them | None as a conversion lever: see "Tested and flat" | — (defect) | S | No buy or checkout button in `covered_primary_flags`, except behind an open drawer | Defect-only card: file `kind: "defect"` when a buy or checkout button is missing, covered (cookie banner, chat bubble) or does not work. Position, size, colour and competing buttons are layout judgements, not defects. Without a defect the card is done |
| PATH-4 | Guided selection in complex categories (selector, "help me choose", fewer options first) | Choice overload is significant once four factors are counted: choice-set complexity, task difficulty, preference uncertainty and decision goal (Chernev, Böckenholt & Goodman 2015 †, 99 observations, N = 7,202). An earlier meta-analysis found a mean effect near zero (Scheibehenne et al. 2010, not re-read) | B | M | Category→product click rate; options per screen | Mostly lab studies; no revenue outcome. Use only where buyers are novices. Overlaps PDP-8 and SRC-8 |
| BEH-1 **T** | Popularity signals from real sales ("bestseller in anchors") | Social-proof tests +2.3% revenue per visitor (Qubit, 119 tests, 95% interval 1.7–2.9). RCT in restaurants: demand for the five dishes labelled as top sellers rose 13–18% (Cai, Chen & Fang 2009) | A | S | Click and add-to-cart rate on labelled SKUs | Generic badges tested flat (Qubit "product badging" −0.2%, 39 tests). Label from order data only |
| BEH-2 **T** | Low-stock signal from live stock ("2 left") | Scarcity tests +2.9% revenue per visitor (Qubit, 125 tests, 95% interval 2.3–3.6). Amazon RCTs: 10% more of a deal claimed led to 2.08% more cart adds in the next hour (Cui, Zhang & Bassamboo 2019 †) | A | S | Add-to-cart rate on low-stock SKUs | Needs accurate stock (PDP-2 first). Fake scarcity is banned (ground rule 5) |
| BEH-3 **T** | Real dispatch deadline as a clock time in plain text ("order by 14:00, ships today") | Urgency tests +1.5% revenue per visitor (Qubit, 119 tests, 95% interval 0.7–2.3) | B | S | Share of orders placed before cut-off | Vendor data only. A clock time, never a countdown, even for a real deadline. Hide the line when the cut-off cannot be met |
| BEH-4 | Pay after delivery (invoice) | RCT at a German furniture web shop, 2022: sales +20%, conversion +9 points (Berg, Burg, Keil & Puri 2025) | A | M | Payment-step completion; default rate | Control group of 948 customers vs 74,128; run by the company, not pre-registered; about 2% defaults. The lift came mainly from customers with low creditworthiness; +9 points is conversion among customers at checkout. Use a provider that carries the credit risk. Check consumer-credit rules first (LEG-9). Cash on delivery is a partial equivalent |
| BEH-5 **T** | Third-party trust seal the shop really holds | RCT, 9,098 sessions: the seal raised purchase completion (Özpolat et al. 2013 †) | B | S | Checkout completion | The seal provider ran the experiment, and the abstract gives no effect size: B until the full paper is read. One retailer. Show only a seal that is currently valid |
| BEH-6 | Prices ending in 9 | Three field experiments: demand rose in all three; more for new items, less next to "sale" signs (Anderson & Simester 2003 †) | A | S | Units sold on re-priced SKUs | Consumer retail; untested for trade buyers. Never touch an Omnibus prior price (LEG-3) |
| BEH-7 | Place price offers early in the path (category and listing pages); shipping offers late (product and checkout pages) | Meta-analysis of 2,732 A/B tests at 252 companies: price promotions worked best early in the funnel, shipping promotions late (Miller & Hosanagar †) | B | S | Margin per visitor, not revenue | No effect sizes were read. Offers cost margin. Qubit free-delivery tests were flat. Every offer is a real one: a crossed-out price follows the prior-price rule (LEG-3) |
| BEH-8 | Offer emails as advertising: measure with a holdout group, not by codes redeemed | Randomized experiments at a ticketing platform: recipients spent 37% more during the offer; about 90% of the lift came without a redeemed code (Sahni, Zou & Chintagunta 2017 †) | A | S | Spend per recipient vs holdout | One platform, not physical goods. Consent-gated (LEG-6). Pairs with CRM-1 and CRM-2 |
| BEH-9 | Faster delivery (operations) | Quasi-experiment, US apparel: online sales +1.45% per business day saved, from a 7-day baseline (Fisher, Gallino & Xu 2019 †) | B | L | Days from order to delivery; repeat rate | Logistics change, not a web change. PDP-1 covers showing the date |
| BEH-10 **T** | Three real options side by side (good, better, best) for kits and bundles | Mixed. Real sales at an online diamond retailer: when shoppers noticed a decoy pair (11–25% of the time), the dominant diamond sold 1.8–3.2 times faster, and gross profit rose 14.3% (Wu & Cosguner 2020 †, observational). Sixteen field experiments: high anchors did little with real money and low anchors pulled payments down (Jung, Perfecto & Nelson 2016 †). The decoy effect failed with realistic products (Frederick, Lee & Baskin 2014, not re-read) | C | M | Share of orders per option | Ground rule 8 applies: existing products with their own sales, none dominated. `truth_source` names the products and their unit sales over the last 12 months |

Findings outside these cards get IDs NEWB-1, NEWB-2… and grade C, unless `source_url` cites a study.

### Tested and flat

Large test sets found these changes near zero or negative. Never present one as a conversion win, and never file one as a defect: where a button sits, how big it is and what colour it has are layout judgements.

Source: Qubit 2017, mean change in revenue per visitor, with the number of tests.

| Change | Mean | Tests |
|---|---|---|
| Buttons (size, shape, position) | −0.2% | 197 |
| Calls to action (wording, prominence) | −0.3% | 172 |
| Colour | 0.0% | 81 |
| Resizing elements | 0.0% | 36 |
| Page redesign | +0.2% | 83 |
| Banners | +0.1% | 212 |
| Pop-ups | 0.0% | 91 |
| Navigation | −0.2% | 216 |
| Sticky navigation | −0.7% | 40 |
| Mobile navigation | −1.7% | 33 |
| Generic product badges | −0.2% | 39 |
| Upsell prompts | −0.1% | 99 |

Base rate: about 75% of effects in 2,101 commercial A/B tests were truly null (Berman et al. 2018 †).

Open question: the same data shows search tests at −0.2% (219 tests) and filter tests at 0.0% (126 tests). What those tests changed has not been read. Do not use these two figures for or against the SRC cards until it has.

---

## Never cite as fact

- "100 ms = 1% of Amazon sales" — one 2006 slide, no data. Use Bing figures.
- "35% of Amazon revenue from recommendations" — McKinsey 2013 estimate.
- "1-Click worth $2.4B/yr" — third-party arithmetic.
- Rufus, Walmart Sparky, West Marine assistant figures — self-selected users.
- Shop Pay "up to 50%" — commissioned study.
- Deloitte "Milliseconds Make Millions" +8.4% — observational, Google-commissioned.
- GEO "+40% visibility" — lab benchmark.
- ~70% cart abandonment as a recoverable lever — it is context, not a lever.
- "The $300 million button" — one consultant's anecdote about an unnamed retailer; no data published.
- The jam study (24 jams vs 6) as proof of choice overload — one small field study; the meta-analyses disagree (see PATH-4).
- Any Qubit figure as a promise for this shop — the tests ran on large retail and travel sites, and the lift applies to visitors who saw the change.

## Key sources

- Fang et al. 2025, GenAI field experiments: https://arxiv.org/abs/2510.12049
- Kohavi, Deng, Vermeer, "A/B Testing Intuition Busters", KDD 2022: https://airbnb.tech/wp-content/uploads/sites/19/2025/10/ABTestingIntuitionBusters.pdf
- Brynjolfsson, Hui & Liu, *Management Science* 2019: https://doi.org/10.1287/mnsc.2018.3207
- Brynjolfsson, Li & Raymond, NBER w31161: https://www.nber.org/papers/w31161
- Etsy embedding search: https://arxiv.org/abs/2306.04833v2
- Zalando LLM search QA: https://engineering.zalando.com/posts/2026/03/search-quality-assurance-with-llm-judge.html
- Allegro LLM judge: https://blog.allegro.tech/2026/08/automating-search-relevance-llm-as-a-judge.html
- Instacart query rewrites: https://tech.instacart.com/building-the-intent-engine-how-instacart-is-revamping-query-understanding-with-llms-3ac8051ae7ac
- Amazon semantic search: https://arxiv.org/abs/1907.00937
- Amazon COSMO: https://www.amazon.science/blog/building-commonsense-knowledge-graphs-to-aid-product-recommendation
- Booking 150 models: https://blog.acolyer.org/2019/10/07/150-successful-machine-learning-models/
- Kohavi rules of thumb: https://blog.acolyer.org/2017/09/26/seven-rules-of-thumb-for-web-site-experimenters/
- Baymard cart abandonment: https://baymard.com/lists/cart-abandonment-rate
- Baymard search query types: https://baymard.com/blog/ecommerce-search-query-types
- Baymard B2B 2026: https://baymard.com/research-articles/b2b-electronic-components-machinery-ux-benchmark-2026
- Walmart catalogue LLMs: https://tech.walmart.com/content/walmart-global-tech/en_us/blog/post/using-llms-to-manage-product-catalogs.html
- Google AI content guidance: https://developers.google.com/search/docs/fundamentals/using-gen-ai-content
- Sharma, Hofman & Watts 2015: https://arxiv.org/abs/1510.05569v1
- 973-shop AI referral study: https://searchengineland.com/llms-google-referral-conversion-study-463747

Behavior lane and evidence upgrades (added 2026-10-08):

- Browne & Swarbrick Jones 2017 (Qubit), "What works in e-commerce": https://www.gwern.net/doc/economics/advertising/2017-browne.pdf
- Miller & Hosanagar, e-commerce A/B testing meta-analysis: https://mackinstitute.wharton.upenn.edu/2020/empirical-meta-analysis-e-commerce-a-b-testing-practices/
- Berman, Pekelis, Scott & Van den Bulte, p-hacking in A/B testing: https://papers.ssrn.com/abstract=3204791
- Unal & Park, "Fewer Clicks, More Purchases", *Management Science* 2023: https://pubsonline.informs.org/doi/10.1287/mnsc.2023.4716 (summary: https://news.cornell.edu/node/325992)
- Chernev, Böckenholt & Goodman 2015, choice overload meta-analysis: https://www.kellogg.northwestern.edu/faculty/research/detail/2015/when-product-assortment-leads-to-choice-overload-a-conceptual
- Cai, Chen & Fang, *AER* 2009, observational learning: https://www.nber.org/papers/w13516
- Cui, Zhang & Bassamboo, *Management Science* 2019: https://pubsonline.informs.org/doi/10.1287/mnsc.2017.2950
- Berg, Burg, Keil & Puri, *JFE* 2025, buy now pay later: https://www.nber.org/papers/w33152
- Özpolat, Gao, Jank & Viswanathan, *ISR* 2013, assurance seals: https://doi.org/10.1287/isre.2013.0489
- Anderson & Simester 2003, $9 price endings: https://doi.org/10.1023/A:1023581927405
- Sahni, Zou & Chintagunta, *Management Science* 2017: https://doi.org/10.1287/mnsc.2016.2450 (summary: https://www.gsb.stanford.edu/insights/navdeep-sahni-email-promotions-prospective-customers-really-do-work)
- Fisher, Gallino & Xu, *JMR* 2019, rapid delivery: https://www.ama.org/research-insights/research-insight-is-faster-delivery-worth-it-for-your-firms-bottom-line/
- Wu & Cosguner, *Marketing Science* 2020, decoy effect: https://doi.org/10.1287/mksc.2020.1231
- Jung, Perfecto & Nelson, *JMR* 2016, anchoring in the field: https://doi.org/10.1509/jmr.14.0238
- Janakiraman, Syrdal & Freling, *Journal of Retailing* 2016 (summary): https://news.utdallas.edu/?p=11491
- Gallino & Moreno, *Management Science* 2014: https://doi.org/10.1287/mnsc.2014.1951 (summary: https://insight.kellogg.northwestern.edu/article/shop_online_pick_up_in_store/amp)
- Blake, Moshary, Sweeney & Tadelis, price salience: https://www.nber.org/papers/w25186
- Luguri & Strahilevitz, "Shining a Light on Dark Patterns": https://papers.ssrn.com/abstract=3431205
