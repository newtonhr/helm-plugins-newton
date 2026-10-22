# First-Principles Framework

Apply this in Phase 1 (end of interview) and again in Phase 3 (synthesis).
It's short. The value is in the discipline of actually answering each
question in writing — not in the complexity of the framework.

## The four questions

For every feature, write one paragraph per question into the synthesis memo.

### 1. What is the underlying job-to-be-done?

Strip away the feature name and solution. What does the user hire this
work to do?

- Bad: "Users want an Axon Search feature."
- Better: "When a user has a specific boat part in mind, they want to
  find the correct SKU in seconds without reading compatibility specs."

If you cannot state the job in the "When [situation], I want to
[motivation], so I can [outcome]" format, the feature is not yet
understood.

### 2. What is the minimum intervention that satisfies the job?

The cheapest thing that moves the needle. Not necessarily what we build —
but the floor that everything else has to beat.

- For a search feature: is it a tuned synonym dictionary, or is it an LLM?
- For personalization: is it a "your boat" cookie, or a full profile
  system?
- For knowledge capture: is it a FAQ page, or a full knowledge graph?

The minimum becomes the baseline against which we justify complexity.

### 3. What happens if we simply don't build it?

The null hypothesis. Be specific.

- Does revenue decline? By how much, over what horizon?
- Does a competitor leapfrog? Which one, with what move?
- Does the moat erode? What's the specific mechanism?
- Or — do we tell ourselves a story and the business keeps running?

If the honest answer is "not much happens", that's a legitimate reason to
deprioritize — and it should be stated plainly in the synthesis.

### 4. Which of our assumptions would need to be false to flip the recommendation?

List 3–5 assumptions. For each, ask: "If this turned out to be wrong,
would I still recommend the same scope and price?"

The assumptions that would flip the recommendation are the **load-bearing**
ones — they belong in Section 2.1 of the SOW. The ones that don't flip
it are commentary; leave them out.

Example load-bearing assumptions:
- "PrestaShop v9 ships stable by June 2026"
- "Catalog has < 50k SKUs"
- "Marina Stores provides tagged training data within 2 weeks"

Example non-load-bearing (cut from SOW):
- "The internet continues to function"
- "Users speak Croatian or English"

## Common first-principles failures

**The "obvious" trap.** When something feels obvious, stop. Obvious things
are usually conventional wisdom, not first-principles truths. Write out
why it's obvious, then stress-test.

**The "everyone wants it" trap.** Features described this way have no
primary user. Force naming one.

**The "competitive parity" trap.** "Svb has it, so we need it" is not a
first-principles argument. The argument is: "Svb has it, and the absence
of it is specifically why we lose segment X of customers." Prove the
second half.

**The "tech gravity" trap.** "We already have the infrastructure" makes
features feel free. They aren't free — every feature has a maintenance,
support, and cognitive cost that doesn't show up in the SOW.

## How to surface first-principles in the SOW

- The **acceptance criteria** should reflect the job-to-be-done, not the
  feature description. "Users can find the correct anode for their engine
  in ≤ 3 interactions" beats "Search returns results."
- The **assumptions** should be the load-bearing ones from Q4.
- The **out-of-scope** should list the "maximum" variants that the
  minimum (Q2) rules out. This shows the user what they're explicitly
  not buying, which prevents scope creep.

## Red flag phrases

If you catch yourself writing these in the SOW or synthesis, stop and
re-apply the framework:

- "Industry best practice"
- "Modern users expect..."
- "AI-powered" (what does it do, specifically?)
- "Seamless integration"
- "Turnkey solution"
- "Future-proof"

These are placeholders for thought, not thought itself.
