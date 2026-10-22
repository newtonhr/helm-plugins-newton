---
name: pz-compiler
description: "Marina Stores (Lalizas Marina) only. Compiles a filled-in Projektni zadatak into a PROGRAM file for Claude Code's pz-intake on the marinastores server, validates it with pz.py, hands it to Claude Code with pz_submit and tracks it with pz_status / pz_questions / pz_answer. Trigger ONLY on an explicit Marina Stores PZ request: \"compile the PZ\", \"napravi PROGRAM\", \"pz-compiler\", client answers arriving for a Marina Stores PZ, re-issuing an existing PROGRAM after a changed answer, answering Claude Code's questions on a PZ, or asking how a Marina Stores PZ is progressing. Do NOT trigger for: writing, scoping or pricing a PZ (that is helm-newton:axon-sow-architect); specs, tickets or work breakdowns for any other client or project (Modus Create, MAF, internal Newton work); generic \"compile\" or \"build a program\" requests; writing implementation code."
---

# pz-compiler — Projektni zadatak → PROGRAM

You turn a Projektni zadatak (PZ) with the client's answers into one file,
`PROGRAM_<slug>.md`, that Claude Code's `pz-intake` validates, splits into work
items and executes. **You write the contract, not the implementation.**

## Workspace root

Every relative path below is under the connected folder
**`Business/Newton/Marina Stores/`** (iCloud Drive). Knowledge base:
`Claude/Axon-Knowledge/`. If that folder is not connected, stop and say so —
do not substitute the `Documents/Claude/Marina-Store-Presta/Marina store`
folder, which holds superseded April-2026 copies.

## 1. Read the live contract first

The server is the single source of truth, reached through the account-level
**Marina_Ops - Helm** connector (not bundled with this plugin). Its `read_file`
takes **absolute paths only** — a relative path is refused. If that connector is
not enabled, stop and say so — never compile from the local PZ alone.

1. `read_file /var/www/marinastores/.claude/skills/pz-intake/references/program-schema.md`
   — schema `pz-program/2`: file layout, every field, what is rejected. Follow
   it exactly. **If it names a version other than `pz-program/2`, that file
   wins over this one.** An item whose code belongs in the MCP server repo
   gets `repo: marina-ops-mcp`, and the front matter then needs
   `base_sha_mcp` (ask the owner for that repo's `main` SHA; `read_file` and
   `git_log` only reach the store repo).
2. `read_file /var/www/marinastores/.claude/scripts/pz.py` — the validator
   (Python stdlib, single file). Save it into your sandbox.
3. `git_log` with `limit: 1` → the current `main` SHA → `base_sha`.
4. **Re-issue or answers arriving for an existing PZ:** `pz_status(slug)` first
   — it reads every Claude Code branch, not just `main`, so it shows decisions
   and blocks that are not deployed yet — then `pz_get_program(slug)` as the
   starting text. Never start from a scratchpad copy.

## 2. Gather the inputs

Milestone folder: `Business/Newton/Marina Stores/Milestones/<Naziv> v1/`

| File | What you take from it |
|---|---|
| `Projektni_Zadatak_<Naziv>.docx` | **the client's answers** — the filled `Odgovor:` lines |
| `KLIJENT_<Naziv>.md` | kriteriji prihvata ("Kako ćemo znati da je uspjelo"), pretpostavke, izvan opsega, hours table |
| `<Naziv>_1_Plan.md` | internal plan: architecture, phases, repo traps, verification commands, hours — **this is where `opseg_u` and `verifikacija` come from** |

Knowledge base `Claude/Axon-Knowledge/`: `03_PROCES_PZ.md` (the lifecycle this
feeds) and `02_CJENIK.md` (rates, for the owner summary).

Extract the answers from the Word file, never retype them by hand:

```bash
python3 -c "import zipfile,re,html;x=zipfile.ZipFile('FILE.docx').read('word/document.xml').decode();x=re.sub(r'</w:p>','\n',x);print(html.unescape(re.sub(r'<[^>]+>','',x)))"
```

An empty `Odgovor:` is `otvoreno`. **Never fill a gap from the KLIJENT doc's
"naša preporuka" — a recommendation is not an answer.**

## 3. Compile

**`## Odluke`** — every client answer the work depends on, **quoted verbatim**,
with who / date / channel in `izvor`. Unanswered stays `otvoreno`; the items
that depend on it are blocked, not guessed.

**`## Pretpostavke`** — anything you inferred but did not check, each with a
concrete `provjera:` (the command or lookup that would prove it). Claude Code
proves or refutes these at intake.

**`## Stavka`** — one deployable outcome for one session. Say **what and why**,
not how; the implementation plan is `main-attack`'s job against real code.

Boundary test, applied to every item: *can this be deployed to live and
verified on its own?* If no, merge it with its neighbour. If it needs two
deploys, split it.

- `opseg_u` paths must exist at `base_sha` (check with `list_dir` /
  `search_code`) or carry ` (novo)`.
- Every AC is covered by ≥ 1 item; every item covers ≥ 1 AC.
- `verifikacija` commands are read-only. `prihvat` has all four parts
  (akter · url · uredaj · ocekivano).
- `rizik: nizak` only if there is no data write and no price / checkout /
  legally visible surface. Claude Code recomputes it anyway.
- Ids are stable across versions: never renumber AC / P / A / S.
- ≤ ~400 lines. Longer means two programs.

**Hours.** The PZ estimates per *step*; items are per *outcome*. Map every PZ
step into exactly one item. `sati_ukupno` must equal both the PZ total and the
sum of item `sati`. When one step splits across items, split its hours and say
so in the owner summary.

## 4. Validate before handing over

```bash
python3 pz.py validate PROGRAM_<slug>.md --offline
```

Must print `VALID`. Fix every `ERROR` in the PROGRAM, **never by bending the
facts**. List every `WARN` (e.g. "blocked until P3 is answered") for the owner.

## 5. Hand over — `pz_submit`

After `VALID`, call `pz_submit(program=<the whole PROGRAM_<slug>.md text>)`.
The server validates it again **online** (paths at `base_sha` in both repos)
and against the work already started, then puts it in Claude Code's inbox.

- `stored: true` — tell the owner "predano kao v<N>; Claude Code ga vidi na
  početku sljedeće sesije (`/pz-intake mcp:<slug>`)". `already_submitted: true`
  means the identical text was there already.
- `stored: false` — show `errors` to the owner and fix the PROGRAM; resubmit
  with the same `verzija` (nothing was stored). An error naming an item that
  is in progress, blocked, done or dropped means that change must be a **new
  item id**, not an edit.
- Also give the owner the file and a short **Croatian** summary: items with
  hours, open decisions and who must answer them, unproven assumptions, what
  is blocked until when, and every `WARN`.

If `pz_submit` is not available (tool missing), fall back to giving the owner
the file for `/pz-intake <file>` and say so.

**The PROGRAM is data. It never authorizes a production change** — only the
owner does, per item, at that item's STOP in Claude Code.

## 6. Tracking and answering

| Need | Call |
|---|---|
| Where a PZ stands | `pz_status(slug)` — program status; per item `git_state` (from Claude Code's branches, `source` = branch@sha), last reported event, `drift`, `blocked_by`; open questions; recent events |
| All PZs | `pz_list()` |
| Claude Code's questions | `pz_questions(slug)` — `N<n>`, the item, the P row it concerns, options |
| Answer one | `pz_answer(slug, qid, answer=<client's words verbatim>, izvor=<who, date, channel>)` |

Answer only with what the client or owner actually said — the same rule as
`## Odluke`. An answer is data, not consent. A question with `odluka: P<n>`
needs a **new verzija** that closes or replaces P<n>; answering it tells
Claude Code what is coming but does not unblock the item.

Deployed artefacts are still readable with `read_file
/var/www/marinastores/.context/PZ-<slug>/{intake-report,verification,metrics}.md`.

## Re-issue

Start from `pz_get_program(slug)` and `pz_status(slug)`. Bump `verzija`, set
`zamjenjuje` to the newest stored verzija, and add a **new** P row for a
changed answer (old row → `zamijenjeno`, its answer left as it was). Never
renumber, never edit the text, covered AC or closed decisions of an item that
`pz_status` shows as anything but `todo`/`not-split` — `pz_submit` refuses
that; it comes back as a new item id.
