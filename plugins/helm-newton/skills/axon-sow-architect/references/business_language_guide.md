# Business Language Guide

The SOW, synthesis memo, and everything the client reads must be
understandable to a marine-retail business audience (CEO, commercial
director, catalog manager, marketing lead). Technical jargon is allowed
only when no plain-language equivalent exists and the concept is
load-bearing for understanding the work.

## The test

Before shipping any sentence in the SOW, ask:
*"Would Ivan Boban, reading this over coffee, know exactly what we're
buying and what he has to do?"*
If the sentence makes him stop and decode a term, rewrite it.

## Scope of this rule

| Artifact | Language discipline |
|---|---|
| SOW (all 12 sections) | Business-first. No unexplained technical terms. |
| Synthesis memo | Business-first. Technical notes allowed in a dedicated "Technical read" section only. |
| Interview notes | Mirror the user's language; do not translate upward. |
| Research briefs | Technical language OK — these are intermediate artifacts. |
| Implementation plan Section 0, 1, 2, 3 | Business-first. |
| Implementation plan Section 5 (Tasks) | Technical precision where it aids execution. |
| Risk register, acceptance criteria | Business-first — if a stakeholder can't verify it, it's not a criterion. |

## Words to avoid (and their translations)

These are common in engineering writing. In the SOW, translate or remove:

| Avoid | Prefer |
|---|---|
| API / endpoint | "connection between [system A] and [system B]" |
| Backend / frontend | "the customer-facing site" / "the system behind the scenes" |
| Database / schema / table | "where [X] is stored" / "how [X] is organized" |
| Middleware | don't use — describe what it actually does |
| Latency / throughput | "how quickly the page loads" / "how many searches we can handle per minute" |
| CRUD, CRUD operations | "creating, reading, updating, and deleting [X]" |
| Refactor | "rewriting how [X] is built" — but usually invisible to the client, so cut |
| Microservice / monolith | don't use — describe the boundary in terms of who owns it |
| Webhook | "a notification sent from [A] to [B] when [event]" |
| REST, GraphQL, RPC | don't use — say "connection" or "data feed" |
| Payload | "the information we send" |
| Deploy / deployment | "publishing the change to the live site" |
| Staging / production | "the preview copy of the site" / "the live site customers use" |
| Migration (data) | "moving [X] from the old system to the new one" |
| Index / indexing | "making [X] searchable" |
| Caching | "keeping a quick-access copy" — but often an implementation detail, just cut |
| Rate limit / throttle | "a cap on how often [system] can be called" |
| OAuth / SSO | "the login system" (unless specifically about it) |
| Token / bearer token | don't use — describe what it authorizes |
| Event / event-driven | "triggered when [X] happens" |
| Queue / message bus | "a list of tasks waiting to be processed" |
| Pipeline | "step-by-step workflow" |
| SLA | "the service level we commit to" (then state it in plain numbers) |
| Headless | don't use — describe the actual arrangement |
| Containerized / Kubernetes | client-invisible — cut |

## Words that stay (marine retail legitimate)

These are domain-correct and business-legitimate. Keep them:

- **SKU, catalog, fitment, compatibility** — retail language
- **Charter, leisure boater, marina, season** — customer segment language
- **Checkout, cart, AOV, conversion, retention** — e-commerce business metrics
- **PrestaShop** — it's a product name, not a jargon word, but explain *what the client sees change*, not the internals
- **GDPR, DPA, VAT, Ugovor, PZ** — legal/commercial language Ivan already speaks
- **Lalizas, Marina Stores, Axon, Helm, Projektni Zadatak (PZ), rad po satu** — program language

## Worked examples

**Bad (technical, closed to Ivan):**
> "We will integrate the PrestaShop REST API with a new FastAPI
> microservice hosted on the Axon Kubernetes cluster. The endpoint
> handles vector search with a 200ms P95 latency SLA."

**Good (business-first, same substance):**
> "We'll add a new search behind the existing store that understands
> natural-language questions (e.g. 'anchor for 45-ft yacht in 20 m
> water'). The search returns results in under one second for the
> top 95% of queries — measured over a full day of live traffic."

---

**Bad (assumption written as engineering note):**
> "Assumption: PrestaShop v8 REST API is stable and the product
> catalog has normalized attributes in the ps_feature table."

**Good (assumption a stakeholder can verify):**
> "Assumption: The current Marina Stores catalog has the boat-fitment
> attributes already filled in for at least 80% of SKUs. If fewer,
> additional cataloguing work is required before this milestone can
> ship, and that work is a separate SOW."

---

**Bad (acceptance criterion with no owner):**
> "Endpoint returns 200 OK with results array in < 300ms P95."

**Good (acceptance criterion a commercial lead can sign off):**
> "A catalog manager picks 20 realistic customer questions at random.
> For at least 18 of those 20, the search returns the correct SKU
> in the top 3 results."

---

**Bad (risk framed technically):**
> "Risk: Data migration from legacy system introduces referential
> integrity issues in the target schema."

**Good (risk framed as a business problem):**
> "Risk: When we move existing customer orders from the old system
> to the new one, some orders might lose their link to the customer
> record. If that happens, customer support would see blank fields
> until we repair the link. Mitigation: we run the move twice —
> once as a rehearsal on a copy, once on the live data — and compare
> record counts and a sample of orders before declaring done."

## Application in review

The reviewer subagent scans the SOW (not the research briefs) for
terms in the "avoid" list. Every match is a **must-fix** unless the
draft already translates the term in the same sentence.

## When in doubt

Default to plain language. If you genuinely need a technical term in
the SOW, the sentence should read: *"<plain-language description>
(technically: <term>)"* — not the reverse. The parenthesis acknowledges
engineers will read the SOW too; the primary text serves the business
reader.
