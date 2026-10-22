# helm-newton

**Internal to Newton d.o.o.** This plugin holds Newton's pricing rules and delivery
process. Never install it for a client and never copy its files into
`newtonhr/helm-plugins` (the client plugins).

| Skill / agent | What it does | Came from |
|---|---|---|
| `helm-newton:e-commerce-audit` | Audits a web shop against proven e-tail practices → Croatian client report + .xlsx Newton backlog. Run by name only ("E-commerce audit") | `webshop-admin` 0.2.0, renamed |
| agent `audit-reviewer` | Mandatory review gate of an E-commerce audit | `webshop-admin` 0.2.0 |
| `helm-newton:axon-sow-architect` | Feature request → internal plan + Upitnik + priced Projektni zadatak | `marina-ops` 1.2.0 |
| `helm-newton:pz-compiler` | Answered PZ → `PROGRAM_<slug>.md`, handed to Claude Code with `pz_submit` | `marina-ops` 1.2.0 |

Install in Claude Code: `/plugin install helm-newton --marketplace newtonhr/helm-plugins-newton`.

**Source of truth:** this repo. Edit here, bump `version` in
`.claude-plugin/plugin.json`, zip `plugins/helm-newton/` and upload it to the Cowork org
plugins (or `/plugin marketplace add newtonhr/helm-plugins-newton` in Claude Code).

**After installing:** turn off the old `webshop-admin` and `marina-ops` plugins and any
standalone `axon-sow-architect` / `pz-compiler` skills. Otherwise two copies compete on
every message.

The Helm MCP connector is not bundled; add it at account level.

## E-commerce audit requirements

Python 3.9+ with `openpyxl`; LibreOffice for recalculation. Tests:
`python3 -m unittest discover -s plugins/helm-newton/skills/e-commerce-audit/scripts/tests`.
More in [`skills/e-commerce-audit/README.md`](skills/e-commerce-audit/README.md).

---

*The sections below come unchanged from the `marina-ops` 1.2.0 README.*

## Required folder

Both skills read the workspace at:

```
Business/Newton/Marina Stores/          (iCloud Drive)
├── Claude/Axon-Knowledge/
│   ├── 01_ODNOS.md        relationship state, contract terms, standing decisions
│   ├── 02_CJENIK.md       pricing rules — every price comes from here
│   ├── 03_PROCES_PZ.md    the PZ lifecycle in force
│   ├── 04_AUDIT.md        append an entry at the end of every session
│   ├── predlosci/         KLIJENT_predlozak.md
│   └── skripte/           generate_pz_docx.js
└── Milestones/<Naziv> v1/ the projektni zadaci
```

Connect that folder to the Cowork project before using either skill.

**Do not connect `Documents/Claude/Marina-Store-Presta/Marina store` as the
workspace.** It holds April-2026 copies of `Axon/` (retainer-era pricing, an
M0–M9 roadmap, a team that no longer exists). The skills would produce wrong
prices from it without complaining. Keep it for the PrestaShop material only.

## Pricing: one regime, not two

`02_CJENIK.md` (2026-08-30) is in force — 600/500/350 per day, **one** uplift of
10–15% (default 12%), blended sanity check ≈ €457–560/day.

The "milestone pricing model v2.0" (2026-08-28, 800/650/650/450 + 15% PM × risk
tier + 10% warranty + €600 base) is superseded. It is deliberately **not** shipped
as `references/pricing_model.md` in this plugin, because having both on disk is
how a PZ gets priced twice as high by accident.

## After installing

Turn off the standalone account-level `axon-sow-architect` and `pz-compiler`
skills in Customize → Skills. Otherwise both copies compete on every message.

## Not included

The **Marina_Ops - Helm** MCP connector stays a separate account-level connector.
It is not bundled here, so turning this plugin off does not cut server access.

## Before first use of the Word generator

`scripts/compile_sow.js` needs its dependency once:

```bash
cd skills/axon-sow-architect && npm install
```

That script is the **English / Greece** SOW generator, and its page header still
reads "AXON Program". The Croatian PZ for Ivan goes through
`Claude/Axon-Knowledge/skripte/generate_pz_docx.js` instead — v6 drops the word
"Axon" from anything the client sees.

## v1.2.0 (2026-10-01) — PZ channel through marina-ops

`pz-compiler` hands a PROGRAM to Claude Code with `pz_submit` instead of a file
the owner carries, and tracks it with `pz_status` (reads Claude Code's
branches, not just `main`), `pz_questions` and `pz_answer`. Schema
`pz-program/2` adds `repo:` per item for work in the MCP server repo. Needs the
connector's principal in `MARINA_OPS_PZ_PLANNER_PRINCIPALS` on the server.

## Open item — contract v4 → v6

The v4 commercial model is hardcoded in **12 commercial-term spots across 7 files**,
not one. (`grep -rno "v4" skills/` returns 13 — the 13th, `marine_industry_croatia.md:26`,
is a historical note, not a term to change.)

- `skills/axon-sow-architect/SKILL.md` — 1 (Commercial model heading)
- `references/marine_industry_croatia.md` — 3
- `references/review_checklist.md` — 3
- `references/interview_playbook.md` — 1
- `agents/reviewer.md` — 2
- `agents/drafter.md` — 1
- `agents/research_risk.md` — 1

The live draft is v6 (2026-09-09): no "Axon" toward the client, no Discovery
phase, never the word "paušal", no monthly activity report, 12-month warranty
under čl. 7.8 while Helm is paid. Sweep all 12 once v6 is signed.

## v1.1.0 (2026-09-18) — estimating methodology from the last two PZs

Derived from `POS narudžbe v1` and `Sidrene cijene i cjenici v1` (both 2026-09-15),
where the first estimate came in far too high — Sidrene 98 h → 38 h (2.6×), POS
19 days ≈ 152 h and €9,500–11,500 → 32 h and €1,800 (roughly 5×). Added to
`axon-sow-architect`:

- **Estimates in hours, never days.** Day rates stay internal; hour = day / 8
  (€75 / €62.50 / €43.75).
- **/2 for Claude Code.** The manual-work estimate is halved. Coordination with a
  third party, dry-run on live and training are halved last and only with a reason.
- **A Claude Code technical plan is not a client estimate** — cut to the smallest
  reliable version first.
- **Mandatory anti-gold-plating pass** before pricing, with the cut list and its
  hours recorded in the internal plan.
- **No discount off an inflated number.**
- **Two client tables** — "Procjena rada" (steps in business names + hours) and
  "Cijena i način rada" (fixed PZ vs hours × 40 €/h) — and the client chooses the
  working mode in the last question.
- **Sanity check** price / hours lands in €57–70/h (≈ €457–560/day ÷ 8), with up to
  €72/h tolerated when the hour mix explains it. Outside the band in either direction
  the cause is named — an arithmetic error, or an honest role mix (architecture-heavy
  above, Grgur's cap below) — and taken to Grgur, with the sacrificed margin in euros in
  the internal plan. Hours are never cut to hit a ratio. The rate is
  an arithmetic control only — it cannot detect an inflated scope.
- **No guarantee that depends on a third party**; unverified claims about the
  client's operation are written neutrally or cut.
- **Builder → reviewer → fix → READY loop** is a gate, not an option.

Also fixed: quality gate 5 said "sell a paid Phase 0 first", which contradicts
`02_CJENIK.md` ("no paid feasibility ramps; a PZ is all or nothing"). It now points
at the three permitted forms.

The same rules were appended to `Claude/Axon-Knowledge/02_CJENIK.md`, which remains
the binding source.
