# newton-sales

**Internal to Newton d.o.o.** Sales material for Helm and the Axon program, written for company directors. Never install it for a client.

| Skill | What it does |
|---|---|
| `newton-sales:helm-sales` | Shared core: what Helm is, the ten director questions, capability status (LIVE / BUILT / CONNECT / ROADMAP), Marina Stores proof in director language, timely Croatian hooks, style and checklist. The other two load it first. |
| `newton-sales:helm-sales-general` | General material for many readers: website and segment pages, A4 brochure or leave-behind, public case study, copy bank. |
| `newton-sales:helm-sales-prospect` | Researches one company from public sources, scores fit and timing, and writes a tailored one-page view for the director, outreach email, call plan and rendgen proposal. Includes GDPR/ZEK rules. |

Install in Claude Code: `/plugin install newton-sales@helm-plugins-newton`.

**Keep current:** the capability status table and Marina Stores facts in `skills/helm-sales/SKILL.md` go stale. Update them when a capability goes live or a client approves numbers, then bump `version` in `.claude-plugin/plugin.json`.

**Before first prospect e-mail:** fill `[NEWTON_PRIVATNOST_URL]` (Newton privacy notice) and have the legitimate-interest assessment checked once by counsel.

**After installing:** turn off any standalone `helm-sales`, `helm-sales-general` and `helm-sales-prospect` skills, or two copies compete on every message.
