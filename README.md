# helm-plugins-newton

Newton d.o.o. internal Claude plugins for work on Helm clients. Client-facing plugins
live in `newtonhr/helm-plugins`; nothing from this repo goes to a client.

| Plugin | What it does |
|---|---|
| [`helm-newton`](plugins/helm-newton/) | Projektni zadatak scoping and pricing, PZ → PROGRAM compiler |
| [`newton-sales`](plugins/newton-sales/) | Helm/Axon sales material: website, brochures, case study, tailored prospect research |

Install in Claude Code: `/plugin marketplace add newtonhr/helm-plugins-newton`, then
`/plugin install helm-newton@helm-plugins-newton` (and `newton-sales@helm-plugins-newton`).

E-commerce audit is a client plugin: `newtonhr/helm-plugins`.
