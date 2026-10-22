# Data sources and collection

## Generic shop

| Need | Source | Script |
|---|---|---|
| Catalogue export | Platform export, API, or connector | `catalogue_health.py` |
| Rendered pages, screenshots | Browser (Claude in Chrome or built-in browser), desktop and mobile | — |
| Saved page HTML | Browser save, or platform fetch tool | `page_checks.py` |
| Search queries | On-site search log, Search Console, support emails; synthetic to fill gaps | `kappa.py` for judge agreement |
| Orders, margins, returns | Platform or ERP export | — |
| Speed | Browser performance panel or PageSpeed; label "lab only" without field data | — |
| Funnel | GA4 export (when available) | — |
| Purchase path | Browser walk, logged step by step; `visible_counts.js` run on each screen | `path_metrics.py` |

The cloud workspace usually cannot reach shop websites from the shell. Fetch through the browser or the platform's tools, save the files, then run the scripts on the saved files.

## Access ladder (client and competitor sites)

A site that blocks one tool is not "not checked". Work down this ladder and move to the next rung on any block: 403, 429, bot challenge ("checking your browser"), geo-block, empty or challenge-only HTML, timeout.

1. Shell fetch with an honest user agent, where the site's robots.txt allows it; then a headless browser in the workspace. A 403 or a challenge to a script means: go to a real browser (rung 3). Never disguise a script to get past a block. Fetch only the pages the walk needs.
2. WebFetch.
3. The user's Chrome (Claude in Chrome): a real browser with a real session passes most bot checks.
4. **The built-in browser.** Always try it when Chrome is unavailable or also blocked.
5. Another storefront of the same company (another country domain or language path), when it shows the same feature. Say which storefront was used.
6. Ask the user to open the page and save it, or to complete a human check, then continue from the saved page or the open tab.

Rules for the ladder:

- Retry a rung once after a short wait before leaving it; a challenge often clears on the second load.
- A 404 or redirect is not a block: fix the URL (start from the site's root) before leaving the rung.
- In a browser, wait for the challenge page to finish (up to 30 seconds), then reload once.
- Never try to defeat a CAPTCHA or a login wall yourself: that is rung 6.
- When a tool declines a site for policy reasons (not a block by the site), do not route around that tool with another fetch method; go to rung 6.
- Record every rung in `evidence/access_log.md`, with its result or the reason it was skipped (for example "svb24: start at rung 3").
- Write "not checked" only when every rung failed, and name the rungs in `not_checked.reason`. The reviewer rejects "blocked" without the log.

## [Marina] Helm (read-only allowlist)

Call only these tools. Every other Helm tool is forbidden, including any tool whose effect is unclear.

| Need | Helm tools |
|---|---|
| Catalogue, texts, attributes | `find_catalog_items`, `get_product_details`, `search_products`, `get_product` |
| Raw page HTML | `fetch_storefront_url` |
| Orders, AOV | `list_orders`, `get_order` |
| Margins, movers, dead stock, stockouts | `pos_margin_report` (when the connector offers it), `pos_top_movers`, `pos_dead_stock`, `pos_stockout_risk` |
| Stock and prices | `get_stock`, `list_low_stock`, `pos_inventory_summary`, `pos_price_changes`, `pos_search_articles`, `pos_get_article_status`, `pos_history_timeseries` |
| Support themes | `get_customer_threads` (summarise into themes; no personal data in outputs) |
| Speed, errors | `diagnose_performance`, `list_recent_errors`, `telemetry_vitals` |
| Funnel, friction, traffic, on-site searches and zero-result terms | `telemetry_funnel`, `telemetry_overview` |
| Configuration, modules | `get_shop_config`, `list_modules`, `list_configuration`, `get_configuration`, `get_module` |

Check `list_modules` for PrestaShop's search statistics module: if enabled, it holds real on-site queries.

`telemetry_funnel` covers consenting sessions only: steps from listing to payment, rage and dead clicks, and the checkout fields with the most invalid inputs and abandons (field names only). It returns empty lists when no consenting session exists; on 2026-10-08 the pre-launch build returned none. An empty result is "no data", never "no friction": list it under not checked. `telemetry_query` (raw SQL) is not on the allowlist.

Not available from Helm: Search Console queries, rendered or mobile pages (use the browser), return reasons (ask where they are kept).

## Competitors

Product page, search, shipping information, cart and visible checkout steps, fitment, B2B features. Never enter data, create accounts or submit forms. The path walk on a competitor stops at the first personal-data form (`reached_first_form: true`). [Marina] Default competitor: svb24.com. It answers scripts with a bot challenge, so start at rung 3 of the access ladder and use the built-in browser if Chrome fails. On 2026-10-08 the shell and the headless browser got HTTP 403; Chrome and the built-in browser both loaded the shop. Its home is `https://www.svb24.com/` (there is no `/en/` home).
