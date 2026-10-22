# Marine Industry Croatia — Domain Brief for AXON

This is condensed expertise for any SOW reasoning. Read it at Phase 0. Cite
it when you argue a scoping decision.

## The AXON engagement context

- **Client:** Marina Stores d.o.o. — Croatian marine retailer, Lalizas Group
  subsidiary. Sells boating equipment (safety gear, electronics, deck hardware,
  engines, accessories) to leisure boaters and charter fleets.
- **Champion:** Ivan Boban, CEO. Reports up to Lalizas Group (Greece, ~$54M,
  14 branches).
- **Strategic bet:** If Axon proves out in Croatia, Lalizas Greece adopts
  globally. Newton owns the platform IP with per-branch licensing. Croatia is
  the proving ground; every milestone must be defensible as *something Greece
  would also want*.
- **Commercial frame (contract v4, from 2026-09):** NO monthly retainer.
  All development work is sold as fixed-price Projektni Zadaci (PZ);
  small jobs as rad po satu (€40/h + VAT, prior written approval). Only
  recurring fee: Helm €700/month (autonomous AI support — no human work
  included). PZ preparation (plan, upitnik, proposal) is FREE — recovered
  via the mandatory +10–15% margin inside every PZ price. PZs are where
  ALL of Newton's margin lives now.
- **Delivery rhythm (historical, April 2026):** M0 Discovery → M1 Dev Infra →
  M2 PrestaShop v9 Migration → M3 Axon Search → M4 My Boat → M5 Knowledge
  Capture → M6 Product Enrichment → M7–M9 TBD. Discovery was dropped after v4. Confirm the live milestone set in `01_ODNOS.md` before using
  this list for anything.

## What's distinctive about marine retail in Croatia

1. **Seasonality is brutal.** April–September is 70–80% of annual revenue.
   Any feature launched in October ships against a shrinking audience; any
   feature that ships in June competes with the busiest operations moment of
   the year. Timing matters more than in general e-commerce.

2. **Two very different buyer segments.**
   - *Leisure boaters*: low-frequency, high-deliberation, spec-sensitive,
     often foreign (Italian, German, Czech, Austrian flagged boats touring
     the Adriatic). Poor Croatian language knowledge. High tolerance for
     English content.
   - *Charter fleets*: high-frequency, price-sensitive, relationship-driven,
     often transacting outside the webshop (phone, email, on-site).
     Represent the revenue backbone but are underserved by digital
     channels.
   The SOW assumptions should be explicit about which segment the feature
   serves.

3. **"My Boat" as a category.** Boaters identify by their boat, not by
   themselves. Any personalization or recommendation feature has to anchor
   on boat profile (make, model, year, engine, electronics) rather than on
   the person. This is structurally different from fashion or electronics
   e-commerce.

4. **Catalog depth vs. query quality.** Marine catalogs have thousands of
   part-number-style SKUs where exact match matters (anode for Honda BF150,
   specific impeller, exact thread spec). Generic e-commerce search
   performs badly here. This is why Axon Search exists as a milestone.

5. **Physical installation and expertise.** Many products require install
   knowledge (anodes, transducers, chartplotter compatibility, fuel-line
   specs). Marina Stores' staff expertise is the moat. Digital features
   that fail to capture or surface this expertise reduce competitive
   advantage rather than increase it.

6. **Regulatory environment.** GDPR (operates in the EU), CE marking
   constraints for imports, VAT rules for EU cross-border sales, Croatian
   consumer-protection law for distance sales. The Ugovor handles most of
   this but any feature that touches data flow needs a note in Section 12.

## The competitive set

- **Svb** (Germany): dominant Northern-European marine webshop. Aggressive
  German-language SEO, broad catalog, fast shipping. The ceiling of what
  Axon could look like, in terms of online experience.
- **Plastimo** (France): OEM + retailer; vertical integration play.
- **Nautos** (Spain/Mediterranean): Southern-Europe focused; closer
  competitor geographically.
- **Decathlon Marine / Tribord**: entry-level, commodity. Not a direct
  threat on depth, but a threat on the first-time-boater top of funnel.
- **SeaHelp, Boatflix, Marine-Aid** and similar service platforms: adjacent,
  not direct. Relevant when scoping content or community features.
- **Local Croatian chandlers** (Tiskara Jurcan, Nautic Centar, hardware
  stores in marinas): offline-strong, digitally weak. Marina Stores can
  out-compete them online with relatively modest investment.

## The Lalizas lens (always apply)

When scoping any feature, ask: "Would Lalizas Greece want this too?"

- ✅ *Yes, same feature, same way*: strong candidate. Tag in synthesis memo.
- 🟡 *Yes, but differently per branch*: scope as platform + branch-local
  config. Licensing math works well here.
- ❌ *Only Croatia needs this*: still legitimate, but the business case must
  stand on Croatian ROI alone. Don't justify on Lalizas upside.

## Pricing sanity anchors

Fixed-milestone pricing rules of thumb (Newton internal, 2026):

| Work type | Indicative rate | Typical frame |
|---|---|---|
| Technical architecture | €600/day = €75/h | 16–40 h |
| Full-stack dev (senior) | €500/day = €62.50/h | 40–160 h |
| Product & discovery | €500/day = €62.50/h | 16–64 h |
| QA & testing | €350/day = €43.75/h | 16–48 h |

Estimates are written in hours, never days (02_CJENIK, 2026-09-15). The frames above
are pre-Claude-Code, manual-work figures: halve them, except for human-paced items.

Indicative only. The binding rates and the **single** 10–15% uplift (default 12%)
live in `Claude/Axon-Knowledge/02_CJENIK.md`, which wins on every disagreement.
There is no separate project-management day rate and no second uplift — stacking
them pushes the blended rate past the €57–70/h (€457–560/day) sanity band.

There is no retainer any more — every euro of margin travels through PZs.
Sanity check any price by dividing it by total hours: the blended rate must land in
€57–70/h (≈ €457–560/day) per 02_CJENIK.md, with up to €72/h acceptable when the hour
mix explains it. Outside that in either direction, name the cause — an arithmetic error,
or an honest role mix (architecture-heavy above, Grgur's cap below) — and take it to
Grgur rather than bending the hours. The rate says nothing about whether the scope is
inflated — that is the anti-gold-plating pass.

## The contract v4 constraints you must honor

(Ugovor o poslovnoj suradnji v4 — always cross-check `Claude/Axon-Knowledge/01_ODNOS.md`,
which is updated more often than this file.)

- Acceptance: client has **5 radnih dana** from delivery to object in
  writing or accept; silence = deemed acceptance (čl. 7.5).
- **Nedostatak vs. Promjena** (čl. 7.6): defects (result ≠ agreed spec)
  fixed free within ≤10 radnih dana; changes (new/altered functionality)
  = new PZ or rad po satu. There is NO included revision round and NO
  free tail-support after acceptance.
- Every PZ must define (čl. 7.2): cilj, opseg (in/out), mjerila uspjeha,
  rok, cijena, **plan plaćanja**, ovisnosti o klijentu. No work before
  written confirmation (e-mail with signed PDF suffices, čl. 7.3).
- Invoicing: after completion, 15-day terms. For PZs > €6,000 propose
  phase invoicing inside the PZ's own payment plan.
- Early termination by client without Newton default: 50% of remaining
  fixed price (čl. 7.7).
- Client-caused delay beyond agreed obligations extends timeline
  day-for-day; scope changes mid-PZ go through čl. 7.4 (new PZ or hourly).
- Exclusivity: Newton must not serve EU nautical-equipment retailers
  during the contract + 24 months; penalty €50,000; lapses if client
  >30 days late on payment + 7 days after warning (čl. 10–11).
- No SLA guarantee by Newton (čl. 14.4); liability cap = 6 months of
  client payments; AI-output responsibility sits with the client, with a
  human-review duty (čl. 15).
- All AI costs on client accounts (Claude Max ≥ $100/mo + client-owned
  Anthropic API). Newton never fronts AI costs.
- Croatian law, Trgovački sud u Splitu.

Echo the relevant items in every PZ. Do not restate or contradict the
contract in other sections.
