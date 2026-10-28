---
name: helm-sales-general
description: Produce Newton's general Helm/Axon sales material for many readers at once — website pages, brochures and leave-behinds, segment pages, the public case study and a reusable copy bank. Loads helm-sales first.
---

# Helm general sales material

General material speaks to many directors at once. It cannot know the reader's systems or numbers.
So it must make every reader think: "This is about my business."
It does that through the director questions, the segment switch and Marina Stores proof.

## Step 0 — Load the core

Load the core skill with the Skill tool: `newton-sales:helm-sales` when installed from the newton-sales plugin, or `helm-sales` when saved as a standalone skill before anything else.
It holds positioning, the ten questions, capability status, proof, hooks, style and the checklist.
If it is not available, stop and tell the user to save it first.

## Step 1 — Settle the brief (ask once, max 3 questions)

- Which asset: web page, brochure, segment page, case study, or copy bank?
- Language: Croatian, English, or both? Croatian is written first; English is adapted, not translated.
- Which Marina Stores numbers and quote are approved for publication?

## Step 2 — Write the copy deck before any design

Write all words first, in one document, section by section. Design comes after the words pass review.
Each section in the copy deck has: purpose (one line), headline, body, proof or status badge, image or screenshot placeholder.

## Step 3 — Use the right blueprint

### 3.1 Main web page (one primary CTA: "Zatražite rendgen poslovanja")

Use the core's web page structure (core section 8.2). Additions for general readers:
- The hero names no segment. It speaks to "vaša tvrtka".
- Show at least four director questions on cards. At least two are LIVE, and they come first.
- The segment switcher carries the tailoring: four tabs with three questions and one hook each.
- One "director's morning" mock-up, clearly marked as an example.
- A short "Kako počinjemo" strip: razgovor → rendgen u 48 h od pristupa → pilot → Axon.

### 3.2 Segment pages (one per segment in core section 7)

Same skeleton as the main page, but:
- hero = the segment hook;
- 3 director questions for that segment;
- one example insight written in that segment's own words (marked "primjer");
- the timely hook that fits the segment (core section 6a), e.g. seasonality for HoReCa, eRačun data for wholesale.

### 3.3 Brochure

Pick the format with the user. Default: **A4 bifold, 4 pages**. Alternative: one-page A4 leave-behind.

A4 bifold:
1. **Cover:** the core one-liner and one image placeholder. Nothing else.
2. **Inside left — "Pitanja koja sebi postavljate":** four director questions, each with one line of what Helm does and a status badge.
3. **Inside right — "Kako radi":** spojite → pitajte → Helm upozori → vi odobrite → sve je zapisano. One sentence each. Then one Marina Stores proof box.
4. **Back — "Kako počinjemo":** the rendgen offer in three steps, control and security in four lines, Newton contact and Split address.

One-page leave-behind: one-liner, three questions, one proof box, the offer, contact.

Brochure rules:
- No more than 250 words on a bifold, 150 on a one-pager.
- No webshop-specific content.
- Status wording stays visible in print ("Radi kod Marina Storesa", "Uz spajanje …", "U razvoju").
- Print outlives facts. Never print numbers that will change soon, except Marina Stores proof with its date.

### 3.4 Public case study

Use the core's case study structure (core section 8.1). Write it so a director from another segment can see himself in it:
- add one closing paragraph: "Što bi ovo značilo za veleprodaju / HoReCa / lanac poslovnica" — one sentence per segment, CONNECT items badged.

### 3.5 Copy bank (reusable lines for every other asset)

A table the team reuses everywhere: headline variants per director question (3 each), proof lines with source and date, objection answers (≤3 sentences), CTA variants, status-badge wording. Croatian first, English column second.

## Step 4 — Output format

- Web page: one self-contained HTML page published as an artifact. Load the artifact-design skill first.
- Brochure: if a Design artifact type is available, create from it. Otherwise produce a print-ready PDF via the pdf skill (A4, 3 mm bleed noted for the printer).
- Case study and copy bank: a document (Docs type if available).
- Always deliver the copy deck too, so the user can edit words without touching the layout.

## Step 5 — Review gate (mandatory)

Before showing anything to the user, start a review sub-agent with: the core checklist (core section 12), the asset, and this skill's brochure word limits.
The reviewer also checks: Croatian grammar and register, that no CONNECT/ROADMAP item reads as live, that no unapproved Marina Stores number or quote appears.
Fix what it finds and send it back until it answers READY.

## Do not

- Do not invent a client, a quote or a result to fill a section.
- Do not personalise general material to one named prospect. That is helm-sales-prospect's job.
- Do not lead with Helm Studio, catalogue work or webshop maintenance.
