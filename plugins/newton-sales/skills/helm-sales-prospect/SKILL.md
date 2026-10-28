---
name: helm-sales-prospect
description: Research one named company (or a short list) from public sources and produce Helm/Axon sales material tailored to it — fit and timing score, a one-page point of view for the director, outreach email, call plan and rendgen proposal. Loads helm-sales first.
---

# Helm tailored prospect material

You research one company and show its director what Helm would do **in his business**.
Tailoring means his products, his locations, his season, his systems and his likely questions.
It does not mean flattery or facts you cannot prove.

## Step 0 — Load the core

Load the core skill with the Skill tool: `newton-sales:helm-sales` when installed from the newton-sales plugin, or `helm-sales` when saved as a standalone skill first. It holds the ten director questions, capability status, proof, timely hooks, segments and style.
If it is not available, stop and tell the user to save it first.

## Step 1 — Inputs

Need: company name, and if possible OIB, web address and the contact person's name and role.
Ask which outputs are wanted (default: all of Step 6).
Ask which Marina Stores numbers and quotes are approved (core section 13). Without approval, the proof box uses only qualitative lines from core section 4, with no numbers.
For a list of more than five companies, run Step 3 (score) on all from light research, then deep research only on the top five.

## Step 2 — Research protocol

Research at company level. Use the person only in their business role.

| Order | Source | What to take |
|---|---|---|
| 1 | Company website and webshop | Categories, brands, store and warehouse locations, B2B portal or not, delivery promises, opening dates, news page |
| 2 | Systems (only to judge connectability) | ERP/POS named in annual reports, job ads or tenders. Webshop platform only if they sell online, from page source if reachable; never mention the platform in external text |
| 3 | companywall.hr or poslovna.hr (fallback: sudreg.pravosudje.hr by hand) | OIB, NKD, board members, founding date, blockade status, 3-year revenue, profit and employees |
| 4 | If listed: eho.zse.hr annual report (search "site:eho.zse.hr <ticker> 2025"); otherwise ask the user for the FINA RGFI statement | Inventory (zalihe), locations, segments, systems, ownership |
| 5 | News (Slobodna Dalmacija, Dalmacija Danas, Lider, Poslovni dnevnik) | Openings, new warehouses, investments, owner changes, awards |
| 6 | Job ads (MojPosao, Posao.hr, the company's careers page) | Roles hired; systems named (Pantheon, SAP B1, Minimax, Luceed, Dynamics, Remaris, Thor) |
| 7 | e-Oglasna ploča, EOJN | Insolvency or enforcement (risk); public tenders they supply |
| 8 | Customer reviews and Google Maps | Number of locations; repeated complaints about stock, delivery, prices |
| 9 | Ownership: ZSE top shareholders, Hanfa takeover notices, news | Parent group, who decides, whether IT is run centrally by the group |

Rules:
- Every fact goes into an **evidence log**: claim | level | source URL | date of the fact (period the source covers) | date seen. Facts older than 24 months are Zaključeno at best and never appear in external text as current.
- Levels: **Opaženo** (public fact with source), **Zaključeno** (inference, reasoning written next to it), **Pretpostavljeno** (industry norm, flagged).
- A fact without a source is not a fact. Leave it out of every external document.
- Respect sites that block automated access. Do not bypass blocks or paywalls; note "nije dostupno".
- If the company site is blocked: use search-result snippets (site:domain), Google Maps listings and annual reports, mark website facts "nije provjereno na webu", and ask the user to paste the homepage, store list and category menu before Step 4. The Step 7 website check then runs on what the user pasted.
- Stop after about 20 sources or when the evidence log answers the Step 3 questions.

## Step 3 — Fit and timing score (internal)

**Fit (0–10):**
- +2 more than one sales point or channel (shop + web, several shops, B2B + retail)
- +2 large or complex stock (many items, several warehouses, seasonal goods)
- +2 B2B customers who reorder (contractors, hotels, restaurants, yachts, shops)
- +1 owner-led company (only from register data: small board and owner on the board; no speculation)
- +1 visible operational friction (repeated complaints about stock, delivery or prices; B2B customers can order only by phone or e-mail)
- +1 known system Helm can connect to (Minimax, SAP B1, Dynamics BC, Odoo have APIs; Pantheon usually via the database)
- +1 revenue roughly 2–100 M €

**Timing (0–5):** +1 for each fresh trigger (≤ 90 days): new shop or warehouse, new webshop or replatforming, ERP or POS change, hiring for e-commerce, data or stock roles, new director or succession, digitalisation grant, regulation (max +1 in total, and only with evidence it hits this company specifically — e.g. dodatna cijena only if they sell B2C with published prices; eRačun alone never counts, it applies to everyone since 1. 1. 2026), 6–10 weeks before their main season (state which season and the evidence for it).

**Negative signals:** blockade or insolvency notice, layoffs, a large recent ERP project with another vendor, a chain or parent group with its own IT department (check the parent). Each one lowers the decision by one step.

**Decision:** fit ≥ 6 and timing ≥ 2 → pursue now. Fit ≥ 6, timing < 2 → nurture (general material, check again in 90 days). Fit < 6 → skip, say why.

## Step 4 — Map to the director questions

Pick the 3 director questions (core section 2) the evidence supports best. At least two must be LIVE at Marina Stores; if the evidence supports only one, add a second LIVE question as "dodatno" and say so in the dosje.
For each write:
- **Hipoteza:** "Na temelju [opaženo], vjerojatno [zaključeno]." Never more certain than the evidence.
- **Što bi Helm pokazao u prvih 30 dana:** two or three example questions and alerts in **their own words** — their categories, brands, locations and season. Mark them "primjer".
- **Status badge** from the core status table, and which of their systems must be connected.
- **Proof:** the closest Marina Stores proof, translated per core section 4.

Numbers about their business are allowed only as a range with the formula and inputs shown. Example: "Ako 5–10 % zalihe stoji dulje od 90 dana, uz zalihu od ~X € to je Y–Z € zarobljenog novca." X must come from their public balance sheet (zalihe), with source.

## Step 5 — Tailoring rules

- Use their nouns: their categories, brands and towns. Never generic "proizvodi".
- Use their season: tourism for coastal businesses (core 6a), construction season for building materials, school and holidays where relevant.
- Use the timely hook that really applies to them, with its date.
- Name their systems only if observed. If inferred, write "ako koristite [sustav]".
- Say where an observation comes from ("U vašem godišnjem izvješću …", "Na vašem webu vidimo …"). Open sourcing is respectful; hidden profiling is creepy.
- Observations must be about the business: locations, categories, customers, season, growth, headcount. At most one web observation, and never as the e-mail opener unless they mainly sell online.
- Never mention private matters, staff problems, finances beyond what is published, or anything about family.
- Never pretend to know their numbers. Ask for them in the call plan.

## Step 6 — Outputs

1. **Interni dosje (never sent):** summary, fit and timing score with reasons, evidence log, risks, decision.
2. **Pogled na vašu tvrtku — one page for the director** (Croatian, ≤ 400 words):
   a. Što smo vidjeli (2–4 sourced observations).
   b. Gdje vjerojatno gubite novac (the 3 hypotheses).
   c. Zašto sada (the trigger, with date).
   d. Što bi Helm pokazao u prvih 30 dana (examples in their words, badged).
   e. Marina Stores, one proof box.
   f. Što bismo provjerili s vama (3–5 questions).
   g. Sljedeći korak: rendgen poslovanja u 48 sati od pristupa sustavima.
3. **E-mail director (50–90 words of body; signature, opt-out and privacy line excluded):** observation → what it means for him → one proof line → one easy question. No feature list. No flattery. Then two follow-ups (≤ 60 words each, a new angle each time, 4 and 10 days later).
4. **Plan prvog razgovora:** goal, the verification questions from 2f mapped to each hypothesis, the one live demo to show (core section 9), what to ask for the rendgen.
5. **Prijedlog rendgena:** which systems, read-only access, what he gets within 48 hours of working access (core 8.3), tailored to his three questions.

Output format: dosje and one-pager as documents (Docs type if available); emails in the reply, ready to paste. Croatian first; English only if asked.

## Step 7 — Verification gate (mandatory)

Before showing anything, start a review sub-agent with the outputs and the evidence log. It checks:
- every claim about the prospect appears in the evidence log with a source, and the external text is no more certain than the log level;
- nothing contradicts the prospect's current website;
- no CONNECT or ROADMAP capability reads as live;
- core checklist (core section 12), Croatian grammar and register;
- compliance rules below.
Fix and resubmit until it answers READY. A person at Newton sends every message; never send it yourself.

## Step 8 — Compliance (GDPR and ZEK)

- Collect only company data and the contact's name, business role and business contact details. No private social media, home address, private phone, family or special-category data.
- Keep the dosje internal. Never send a prospect "everything we know about you".
- First email must: show who Newton is (no hidden sender), offer a free way to opt out, and include one privacy line: where we found the contact, why we write, link to Newton's privacy notice (GDPR Art. 14). Placeholder: `[NEWTON_PRIVATNOST_URL]`.
- Prefer the company address for first contact. For named people rely on legitimate interest, low volume and clear relevance.
- Delete research on prospects who do not answer after 12 months. Respect any objection at once and add it to a do-not-contact list.
- This is not legal advice; Newton should have its legitimate-interest assessment checked once by counsel.

## Do not

- Do not invent store counts, systems, revenue, people or quotes.
- Do not use triggers older than 90 days as the email hook.
- Do not tailor by inventing a problem. If evidence is thin, say so in the dosje and recommend nurture.
