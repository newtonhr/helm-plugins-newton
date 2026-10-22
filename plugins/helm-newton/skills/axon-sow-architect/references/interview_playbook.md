# Interview Playbook

The goal of the interview is to be able to write the synthesis memo without
making anything up. If you are ever inventing a number or a user segment in
the draft, the interview was too shallow — go back.

## Operating rules

1. One question per turn. Use `AskUserQuestion` with 2–4 concrete options
   when the choice is bounded; use prose when it's open.
2. Never ask what you can infer. Check the Axon-Knowledge base, workspace, Ugovor v4, prior
   milestones first. Validate your inferences — don't interrogate.
3. Progress by lens: Product → Business → Marine industry → Risk. Each
   lens has a required set below. Skip items only if already answered.
4. Name tensions. Before leaving the interview, surface at least three
   trade-offs and ask the user to weigh in on each.

## Lens 1 — Product

**Required questions:**

- **What is the feature, in one sentence?** (If they can't, that's the
  first flag — help them craft it, but don't write it for them.)
- **Who is the primary user?** (Leisure boater / charter fleet operator /
  Marina Stores internal staff / Axon admin) Be specific. "Boaters" is not
  a user.
- **What does the user do today instead?** This is the baseline against
  which any benefit will be measured.
- **What's the first moment the user encounters this feature?** Entry
  point matters — homepage, search results, email, PDP, checkout.
- **What's the job-to-be-done?** (See first_principles_framework.md) —
  frame it as "When [situation], I want to [motivation], so I can
  [outcome]."

**Optional follow-ups by answer pattern:**
- If the user says "everyone": push back. Every feature serves some
  users more than others. Get the primary user.
- If the user can't describe the status-quo behavior: the feature may be
  greenfield rather than replacement. That's fine but changes the
  adoption story.

## Lens 2 — Business

**Required questions:**

- **Revenue hypothesis.** What's the mechanism through which this
  increases revenue, decreases cost, or reduces risk? "Better experience"
  is not a mechanism — ask for the chain.
- **Measurable target.** What would "good" look like in 6 months? In 12?
  Pin a number or a range. If the user resists, propose a measurable
  that captures their intuition.
- **Budget envelope.** What's the price range they're carrying in their
  head? This sets the negotiation anchor and tells you what scope is
  possible.
- **Urgency.** Why now? What makes this a 2026 milestone rather than 2027?
  Seasonality, Lalizas pressure, competitive move, or artificial
  pacing?
- **Ownership.** Who at Marina Stores is accountable for the business
  outcome after delivery? (If no one, that's a big red flag.)

**The Lalizas lens** (always ask):
- Would this feature also work for Lalizas Greece as-is?
- If not, what would need to change per-branch?

## Lens 3 — Marine industry

**Required questions:**

- **Which segment?** Leisure boaters or charter fleets? If both, which
  dominates first?
- **Seasonality interaction.** Does this feature's value peak in-season
  (April–Sept), off-season, or is it flat? When does it go live?
- **Does it rely on Marina Stores' staff expertise?** Features that
  capture expertise are moat-building. Features that route around
  expertise commoditize the business.
- **Boat-centric or person-centric?** Marine users identify by boat.
  Any personalization must be grounded in boat profile, not just user
  account.
- **Catalog dependency.** Does it need clean product data, attributes,
  compatibility mappings? If yes, where does that data come from and is
  it ready?

## Lens 4 — Risk and failure modes

**Required questions:**

- **What would "disappointing" look like 6 months in?** Adoption under
  X%, revenue impact below Y, operational cost above Z.
- **What's the single most fragile assumption?** If we had to pick the
  one thing most likely to invalidate the plan, what is it?
- **Rollback story.** If this feature ships and underperforms, what's
  the unwind? (Remove, iterate, leave dark?)
- **Data privacy / GDPR surface.** Does this feature collect, process,
  or transfer personal data? Flag for DPA review.

## Tensions to surface before leaving

Pick at least three and name them back to the user. Examples:

- "This feature helps leisure boaters but charter fleets are our revenue
  backbone. Is that deliberate, or should we reshape it?"
- "You want to ship in June but the catalog prerequisite isn't ready
  until July. Which gives?"
- "Speed-to-ship vs. Lalizas-portability are pulling in opposite
  directions on this. Which matters more?"
- "The price you're carrying is €8k but the hours I'm seeing suggest
  €14–16k. Do we trim scope or renegotiate?"
- "This feature reduces calls to the support team, but support's
  expertise is a competitive moat. Are we sure we want to route around
  it?"

If you cannot name at least three tensions, you haven't thought hard
enough. Go back to the research briefs and look for conflicts.

## Exit criterion

You can answer each in one sentence:
1. What is this feature?
2. Who is it for?
3. What does it replace or augment?
4. Why now, specifically?
5. What would make us decide not to build it?

If any answer starts with "um" or "kind of", keep interviewing.
