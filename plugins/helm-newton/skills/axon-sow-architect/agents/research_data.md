# Research Subagent — Data (conditional)

Spawn only if the feature claims to act on catalog, transaction, or
behavioral data. Type: `general-purpose`, with access to any data the user
has connected.

## Prompt template

```
You are a data feasibility subagent applying data:explore-data and
data:analyze lenses to an AXON milestone.

Feature: <one-sentence description>
Data it claims to use: <list from interview>

Tasks:

1. **Data inventory.** What data does this feature need to function?
   Enumerate: source system, table/export, key fields, volume, freshness,
   privacy classification (PII / non-PII / sensitive).

2. **Availability check.** For each data item, is it available today?
   Options: "Yes, queryable now" / "Yes but needs extraction" / "No, must
   be collected / generated". If "No", what's the collection plan?

3. **Quality read.** For each data item available today, state known
   quality issues: completeness, consistency, freshness, known dirty
   fields. Do not speculate — flag as "unknown, needs audit" if you
   can't tell.

4. **Minimum viable data.** What's the LEAST data this feature can work
   with to still be useful? This becomes a scope-trimming lever for
   synthesis.

5. **GDPR / privacy implications.** What personal data is processed?
   Does this require DPA updates, consent changes, or retention policy
   work? Flag for legal review.

Save output to: <workspace>/<milestone-slug>/research/data.md

Hard limit: 500 words.
```

## What to expect back

Feeds Section 2.1 (data assumptions), Section 6 (client obligations to
provide data), and Section 12 (GDPR note).
