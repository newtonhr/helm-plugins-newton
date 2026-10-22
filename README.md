# helm-plugins-newton

Newton d.o.o. internal Claude plugins for work on Helm clients. Client-facing plugins
live in `newtonhr/helm-plugins`; nothing from this repo goes to a client.

| Plugin | What it does |
|---|---|
| [`helm-newton`](plugins/helm-newton/) | E-commerce audit, Projektni zadatak scoping and pricing, PZ → PROGRAM compiler |

Install in Claude Code: `/plugin marketplace add newtonhr/helm-plugins-newton`, then
`/plugin install helm-newton@helm-plugins-newton`.

Tests: `python3 -m unittest discover -s plugins/helm-newton/skills/e-commerce-audit/scripts/tests`.
