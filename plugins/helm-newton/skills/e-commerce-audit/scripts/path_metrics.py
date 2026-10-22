#!/usr/bin/env python3
"""Count the purchase path: interactions from landing to checkout, and what a shopper sees on each screen.

Usage:
    python3 path_metrics.py --walks path_walk_*.json [--pages-dir pages/path] [--date 2026-10-08] [-o path.json]

Inputs, both written during the browser walk (SKILL.md step 3.3, "Path walk"):

1. Walk logs, one JSON per site and device. The audited shop's walks use "site": "client".
   {"site": "client", "device": "desktop", "scenario": "known item", "start": "home", "goal": "payment step",
    "complete": false, "reached_first_form": true, "stopped_reason": "...",
    "steps":   [{"stage": "find", "type": "click", "what": "open category", "page_load": true},
                {"stage": "checkout", "type": "fill", "fields": 3, "required": 3, "screen": "checkout 1"}],
    "screens": [{"name": "cart page", "stage": "cart", "kind": "cart", "counts": {...}}]}
   stage: find | product | cart | checkout.   type: click | fill | select | load.
   "load" is a direct page load (the landing); it counts as a page load, not as an interaction.
   A "fill" step counts one interaction per field typed (`fields`).
   A walk that stops at the first personal-data form without typing (every competitor walk) sets
   "reached_first_form": true; all its steps then count as the path to that form.
   "screens" holds what a shopper can SEE on a screen: "counts" is the output of visible_counts.js, run in
   the rendered page. These are the numbers for findings. The first screen listed for a stage is the one
   compared across sites, so list the full cart page before a cart drawer (a drawer's counts include the
   page behind it). "kind" says what the screen is ("guest form", "login or guest gate"): a competitor's
   screen is compared with the client's only when both have the same kind.
   Optional "pages": {"file.html": "cart"} names saved HTML that is not on the shortest path.

2. Saved HTML of cart and checkout screens (optional). The script counts the MARKUP: links by region,
   buttons, form fields (names only, never values), pre-ticked checkboxes and promo-code fields.
   Markup counts include everything a page hides with CSS (a checkout often carries the whole site menu),
   so they are hints for where to look, never numbers for a finding. They feed no baseline row.

The walk log is the source of truth. No network access.
Output: per-walk metrics, a client-vs-competitor comparison, baseline rows, flags.
"""
import argparse
import datetime
import glob
import json
import os
import re
import sys
from html.parser import HTMLParser

STAGES = ("find", "product", "cart", "checkout")
TYPES = ("click", "fill", "select", "load")
REGIONS = ("header", "nav", "footer")
INNER_TAGS = ("form", "article")       # not <main>: some themes wrap the whole page in it
SKIP_INPUT_TYPES = {"hidden", "submit", "button", "image", "reset"}
# Screen names that keep baseline rows comparable between runs. A cookie-banner variant adds ", <condition>".
SCREEN_NAMES = ("product page", "cart page", "cart drawer", "first form", "checkout 1", "checkout 2", "checkout 3",
                "checkout 4", "checkout 5")
# What a cart or checkout screen is. Screens are compared across sites only when the kinds are equal.
SCREEN_KINDS = ("product page", "cart", "cart drawer", "guest form", "login or guest gate", "login wall",
                "address form", "delivery", "payment", "review")
PROMO_WORDS = ("discount", "coupon", "promo", "voucher", "kupon", "popust", "gutschein", "rabatt", "sconto", "kod za")
CARD_CLASSES = ("product-miniature", "product-card", "product-item", "product-tile")
FACET_CLASSES = ("facet",)

# One word list for this script and visible_counts.js (which carries a copy; a test keeps them equal).
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "path_words.json"), encoding="utf-8") as _fh:
    WORDS = {k: re.compile(v, re.I) for k, v in json.load(_fh).items() if not k.startswith("_")}


def is_primary(text):
    """Same rule as visible_counts.js: a button that moves the shopper toward the order."""
    t = " ".join(str(text).split())
    return bool(WORDS["primary"].search(t)) and not WORDS["not_primary"].search(t) \
        and not (WORDS["login"].search(t) and not WORDS["guest"].search(t))


class PageCounter(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.region_depth = {r: 0 for r in REGIONS}
        self.inner_depth = 0       # inside a form or article: a <footer> or <header> there is not the site's
        self.links = {"header": 0, "nav": 0, "footer": 0, "main": 0}
        self.exit_links = {"header": 0, "nav": 0, "footer": 0, "main": 0}
        self.buttons, self.fields, self.pre_ticked = [], [], []
        self.radio_groups, self.forms = set(), 0
        self.product_cards = self.facet_groups = 0
        self._capture, self._form, self._skip, self.words = None, None, 0, 0
        self._region_stack = []

    def _region(self):
        for r in ("footer", "nav", "header"):     # a nav inside a header counts as nav
            if self.region_depth[r]:
                return r
        return "main"

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v if v is not None else "") for k, v in attrs}
        if tag in INNER_TAGS:
            self.inner_depth += 1
        if tag == "nav" or (tag in REGIONS and not self.inner_depth):
            self.region_depth[tag] += 1
            self._region_stack.append(tag)
        elif tag in REGIONS:
            self._region_stack.append(None)          # an inner header/footer: remember it, count nothing
        if tag in ("script", "style", "noscript", "template"):
            self._skip += 1
            return
        classes = a.get("class", "").lower().split()
        if any(c in classes for c in CARD_CLASSES):
            self.product_cards += 1
        if any(c in classes for c in FACET_CLASSES):
            self.facet_groups += 1
        hidden = "hidden" in a or re.search(r"display\s*:\s*none", a.get("style", ""), re.I)
        if tag == "form":
            self.forms += 1
            self._form = a.get("id") or a.get("name") or a.get("action", "").rstrip("/").rsplit("/", 1)[-1][:40] \
                or f"form{self.forms}"
        elif tag == "a" and "href" in a:
            href = a["href"].strip().lower()
            region = self._region()
            self.links[region] += 1
            dead = href in ("", "#") or href.startswith(("#", "javascript:", "mailto:", "tel:"))
            if not dead and not WORDS["funnel"].search(href):
                self.exit_links[region] += 1
            if any("btn" in c or "button" in c or "cta" in c for c in classes):
                self._capture = {"tag": "a", "text": [], "region": region}
        elif tag == "button" or (tag == "input" and a.get("type", "").lower() in ("submit", "button")):
            if hidden:
                return
            entry = {"tag": tag, "text": [a.get("value", "")] if tag == "input" else [], "region": self._region()}
            if tag == "input":
                self._close_button(entry)
            else:
                self._capture = entry
        elif tag in ("input", "select", "textarea"):
            kind = a.get("type", "text").lower() if tag == "input" else tag
            if kind in SKIP_INPUT_TYPES or hidden:
                return
            name = a.get("name") or a.get("id") or "(unnamed)"
            if kind == "radio":
                self.radio_groups.add((self._form, name))
                return
            label = " ".join((name, a.get("placeholder", ""), a.get("id", ""))).lower()
            field = {"name": name, "type": kind, "required": "required" in a, "form": self._form,
                     "promo": any(w in label for w in PROMO_WORDS)}
            self.fields.append(field)
            if kind == "checkbox" and "checked" in a:
                self.pre_ticked.append({"name": name, "form": self._form})

    def _close_button(self, entry):
        text = " ".join(" ".join(entry["text"]).split())[:60]
        self.buttons.append({"text": text, "tag": entry["tag"], "region": entry["region"],
                             "primary_candidate": is_primary(text)})

    def handle_endtag(self, tag):
        if tag in INNER_TAGS and self.inner_depth:
            self.inner_depth -= 1
        if tag in REGIONS and self._region_stack:
            opened = self._region_stack.pop()
            if opened and self.region_depth[opened]:
                self.region_depth[opened] -= 1
        if tag in ("script", "style", "noscript", "template") and self._skip:
            self._skip -= 1
        elif tag == "form":
            self._form = None
        elif self._capture and tag == self._capture["tag"]:
            self._close_button(self._capture)
            self._capture = None

    def handle_data(self, data):
        if self._skip:
            return
        self.words += len(re.findall(r"\w+", data))
        if self._capture is not None:
            self._capture["text"].append(data)


def count_page(html_text, name):
    """Markup counts for one saved page. Hints only: CSS-hidden elements count too."""
    c = PageCounter()
    c.feed(html_text)
    typed = [f for f in c.fields if f["type"] not in ("checkbox",)]
    by_form = {}
    for f in c.fields:
        by_form.setdefault(f["form"] or "(no form)", []).append(f["name"])
    primary = [b for b in c.buttons if b["primary_candidate"] and b["region"] not in ("footer", "nav")]
    return {
        "page": name,
        "links_total": sum(c.links.values()), "links_by_region": c.links,
        "exit_links_total": sum(c.exit_links.values()), "exit_links_by_region": c.exit_links,
        "buttons_total": len(c.buttons), "primary_candidates_main": len(primary),
        "buttons": c.buttons[:60],
        "forms": c.forms, "fields_total": len(c.fields), "fields_typed": len(typed),
        "fields_required": sum(1 for f in typed if f["required"]),
        "checkboxes": sum(1 for f in c.fields if f["type"] == "checkbox"),
        "radio_groups": len(c.radio_groups),
        "pre_ticked_checkboxes": c.pre_ticked,
        "promo_code_field": any(f["promo"] for f in c.fields),
        "field_names_by_form": by_form,
        "product_cards_hint": c.product_cards, "facet_groups_hint": c.facet_groups,
        "visible_words": c.words,
    }


def screen_summary(sc):
    """Flatten one visible_counts.js result. Missing keys stay None so a partial count is visible as partial."""
    c = sc.get("counts") or {}
    f = c.get("fields") or {}
    return {
        "name": sc.get("name"), "stage": sc.get("stage"), "kind": sc.get("kind"), "viewport": c.get("viewport"),
        "visible_links": c.get("links_total"), "visible_exit_links": c.get("exit_links_total"),
        "visible_exit_links_by_region": c.get("exit_links"),
        "primary_candidates": c.get("primary_candidates"), "primary_in_first_screen": c.get("primary_in_first_screen"),
        "primary_covered": c.get("primary_covered"),
        "typed_fields": f.get("typed"), "typed_required": f.get("typed_required"),
        "typed_optional": f.get("typed_optional"), "checkboxes": f.get("checkboxes"),
        "selects_without_default": f.get("selects_without_default"), "pre_ticked": c.get("pre_ticked") or [],
        "pre_selected_radios": c.get("pre_selected_radios") or [],
        "primary_buttons": c.get("primary_buttons") or [],
        "buttons": [b.get("text") for b in (c.get("buttons") or []) if isinstance(b, dict)][:12],
    }


def check_walk(walk, source):
    """Type and schema checks. Returns (errors, warnings); a walk with errors is not measured."""
    errors, warnings = [], []
    if not isinstance(walk, dict):
        return [f"{source}: a walk log is one JSON object"], warnings
    for key in ("site", "device", "steps"):
        if not walk.get(key):
            errors.append(f"{source}: '{key}' is required")
    steps = walk.get("steps") or []
    if not isinstance(steps, list):
        return errors + [f"{source}: 'steps' must be a list"], warnings
    for i, s in enumerate(steps, start=1):
        if not isinstance(s, dict):
            errors.append(f"{source} step {i}: a step is an object")
            continue
        if s.get("stage") not in STAGES:
            errors.append(f"{source} step {i}: stage must be one of {list(STAGES)}")
        if s.get("type") not in TYPES:
            errors.append(f"{source} step {i}: type must be one of {list(TYPES)}")
        if s.get("type") == "fill":
            if not (isinstance(s.get("fields"), int) and not isinstance(s.get("fields"), bool) and s["fields"] > 0):
                errors.append(f"{source} step {i}: a fill step needs 'fields' (whole number above 0)")
            if s.get("required") is not None and not isinstance(s.get("required"), int):
                errors.append(f"{source} step {i}: 'required' must be a whole number when given")
    order = [STAGES.index(s["stage"]) for s in steps if isinstance(s, dict) and s.get("stage") in STAGES]
    if order != sorted(order):
        errors.append(f"{source}: stages must run in order {list(STAGES)}")
    if walk.get("pages") is not None and not isinstance(walk["pages"], dict):
        errors.append(f"{source}: 'pages' must be an object {{file: stage}}")
    screens = walk.get("screens") or []
    if not isinstance(screens, list):
        return errors + [f"{source}: 'screens' must be a list"], warnings
    for i, sc in enumerate(screens, start=1):
        if not isinstance(sc, dict):
            errors.append(f"{source} screen {i}: a screen is an object")
            continue
        if sc.get("stage") not in STAGES:
            errors.append(f"{source} screen {i}: stage must be one of {list(STAGES)}")
        if not str(sc.get("name", "")).strip():
            errors.append(f"{source} screen {i}: name is required")
        elif not str(sc["name"]).split(",")[0].strip() in SCREEN_NAMES:
            warnings.append(f"{source} screen {i}: name '{sc['name']}' is not one of {list(SCREEN_NAMES)} "
                            f"(plus an optional ', <condition>'); baseline rows will not match between runs")
        if sc.get("stage") in ("cart", "checkout"):
            if not sc.get("kind"):
                warnings.append(f"{source} screen {i}: no 'kind'; without it the screen is compared with any other "
                                f"site's first {sc.get('stage')} screen")
            elif sc["kind"] not in SCREEN_KINDS:
                warnings.append(f"{source} screen {i}: kind '{sc['kind']}' is not one of {list(SCREEN_KINDS)}")
        counts = sc.get("counts")
        if isinstance(counts, str):                    # visible_counts.js returns a JSON string
            try:
                sc["counts"] = counts = json.loads(counts)
            except json.JSONDecodeError:
                counts = None
        if not isinstance(counts, dict):
            errors.append(f"{source} screen {i}: 'counts' must be the visible_counts.js result")
        elif isinstance(counts.get("scrolled_from"), (int, float)) and counts["scrolled_from"] > 0:
            warnings.append(f"{source} screen {i}: the page was scrolled when visible_counts.js ran; parts that react "
                            f"to scrolling are stale: run it again and store the second result")
    if walk.get("complete") and not any(isinstance(s, dict) and s.get("stage") == "checkout" and s.get("type") == "fill"
                                        for s in steps):
        errors.append(f"{source}: 'complete' is true but no checkout field was typed; a walk that stops at the first "
                      f"form is complete: false with reached_first_form: true")
    return errors, warnings


def walk_metrics(walk, source):
    errors, warnings = check_walk(walk, source)
    if errors:
        return None, errors, warnings
    steps = walk["steps"]

    def tally(rows):
        clicks = sum(1 for s in rows if s["type"] == "click")
        selects = sum(1 for s in rows if s["type"] == "select")
        fields = sum(s["fields"] for s in rows if s["type"] == "fill")
        loads = sum(1 for s in rows if s["type"] == "load" or s.get("page_load"))
        return {"clicks": clicks, "selects": selects, "fields_typed": fields,
                "interactions": clicks + selects + fields, "page_loads": loads}

    first_form = next((i for i, s in enumerate(steps) if s["stage"] == "checkout" and s["type"] == "fill"), len(steps))
    checkout = [s for s in steps if s["stage"] == "checkout"]
    fills = [s for s in checkout if s["type"] == "fill"]
    m = {
        "source": source, "site": walk["site"], "device": walk["device"],
        "label": f"{walk['site']} {walk['device']}", "is_client": str(walk["site"]).lower() == "client",
        "scenario": walk.get("scenario"), "start": walk.get("start"), "goal": walk.get("goal"),
        "browser": walk.get("browser"),
        "complete": bool(walk.get("complete")), "stopped_reason": walk.get("stopped_reason") or "",
        "total": tally(steps),
        "by_stage": {st: tally([s for s in steps if s["stage"] == st]) for st in STAGES},
        "to_first_checkout_form": tally(steps[:first_form]),
        "reached_checkout_form": first_form < len(steps) or bool(walk.get("reached_first_form")),
        "checkout_fields_typed": sum(s["fields"] for s in fills),
        "checkout_fields_required": sum(s["required"] if s.get("required") is not None else s["fields"] for s in fills),
        "checkout_screens": len({s.get("screen") for s in checkout if s.get("screen")}),
        "pages": sorted({s["page"] for s in steps if s.get("page")} | set(walk.get("pages") or {})),
        # `pages` on the walk names screens saved outside the shortest path (e.g. the full cart page).
        "page_stage": {**{s["page"]: s["stage"] for s in steps if s.get("page")}, **(walk.get("pages") or {})},
        "screens": [screen_summary(sc) for sc in (walk.get("screens") or [])],
    }
    return m, [], warnings


def first_screen_of(walk, stage):
    return next((s for s in walk["screens"] if s["stage"] == stage), None)


def comparison(walks):
    reached = [w for w in walks if w["reached_checkout_form"]]      # a walk that never got there has no path length

    def row(metric, getter, pool):
        vals = {w["label"]: getter(w) for w in pool}
        return {"metric": metric, "values": vals} if vals else None

    done = [w for w in walks if w["complete"]]
    rows = [
        row("Interactions to first checkout form", lambda w: w["to_first_checkout_form"]["interactions"], reached),
        row("Clicks to first checkout form", lambda w: w["to_first_checkout_form"]["clicks"], reached),
        row("Page loads to first checkout form", lambda w: w["to_first_checkout_form"]["page_loads"], reached),
        row("Interactions, landing to goal (complete walks only)", lambda w: w["total"]["interactions"], done),
        row("Checkout fields typed (complete walks only)", lambda w: w["checkout_fields_typed"], done),
        row("Checkout screens (complete walks only)", lambda w: w["checkout_screens"], done),
    ]
    rows = [r for r in rows if r]
    # Screens: compare a competitor's first screen of a stage with the client's only when both are the same kind.
    not_like = []
    client_kind = {}                                     # (device, stage) -> kind of the client's first screen there
    for w in walks:
        if w["is_client"]:
            for stage in ("cart", "checkout"):
                sc = first_screen_of(w, stage)
                if sc and sc.get("kind"):
                    client_kind[(w["device"], stage)] = sc["kind"]
    for stage, label in (("cart", "cart screen"), ("checkout", "first checkout screen")):
        for key, title in (("visible_exit_links", "Visible exit links"), ("typed_fields", "Visible typed fields"),
                           ("typed_required", "Visible required typed fields"),
                           ("primary_in_first_screen", "Primary actions in first screen")):
            vals = {}
            for w in walks:
                sc = first_screen_of(w, stage)
                if not sc or sc[key] is None:
                    continue
                want = client_kind.get((w["device"], stage))
                if not w["is_client"] and want and sc.get("kind") and sc["kind"] != want:
                    note = {"walk": w["label"], "stage": stage, "screen": sc["name"], "kind": sc["kind"],
                            "client_kind": want}
                    if note not in not_like:
                        not_like.append(note)
                    continue
                vals[w["label"]] = sc[key]
            if vals:
                rows.append({"metric": f"{title}, {label}", "values": vals})
    gaps = []
    for device in sorted({w["device"] for w in reached}):
        same = [w for w in reached if w["device"] == device]
        client = next((w for w in same if w["is_client"]), None)
        others = [w for w in same if not w["is_client"]]
        if client and others:
            best = min(others, key=lambda w: w["to_first_checkout_form"]["interactions"])
            gaps.append({"device": device, "client": client["to_first_checkout_form"]["interactions"],
                         "best_competitor": best["site"],
                         "best_competitor_value": best["to_first_checkout_form"]["interactions"],
                         "gap": client["to_first_checkout_form"]["interactions"]
                         - best["to_first_checkout_form"]["interactions"]})
    return rows, gaps, not_like


def baseline_rows(walks, date):
    rows = []
    for w in walks:
        if not w["is_client"]:
            continue
        src = f"path_metrics.py from {w['source']}"
        if w["reached_checkout_form"]:
            rows.append({"metric": f"Path: interactions to first checkout form ({w['device']})",
                         "value": w["to_first_checkout_form"]["interactions"], "date": date, "method": src})
        if w["complete"]:
            rows.append({"metric": f"Path: interactions, landing to goal ({w['device']})",
                         "value": w["total"]["interactions"], "date": date, "method": src})
            rows.append({"metric": f"Path: checkout fields typed ({w['device']})",
                         "value": w["checkout_fields_typed"], "date": date, "method": src})
        for sc in w["screens"]:
            method = f"visible_counts.js in the rendered page, via {w['source']}"
            if sc["stage"] in ("cart", "checkout") and sc["visible_exit_links"] is not None:
                rows.append({"metric": f"Path: visible exit links, {sc['name']} ({w['device']})",
                             "value": sc["visible_exit_links"], "date": date, "method": method})
            if sc["stage"] == "checkout" and sc["typed_fields"] is not None:
                rows.append({"metric": f"Path: visible typed fields, {sc['name']} ({w['device']})",
                             "value": sc["typed_fields"], "date": date, "method": method})
    return rows


def run(walk_files, pages_dir, date):
    walks, errors, warnings = [], [], []
    for path in walk_files:
        name = os.path.basename(path)
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"{name}: cannot read walk log ({e})")
            continue
        m, errs, warns = walk_metrics(data, name)
        errors += errs
        warnings += warns
        if m:
            walks.append(m)
    labels = [w["label"] for w in walks]
    for dup in sorted({x for x in labels if labels.count(x) > 1}):
        errors.append(f"two walks share the label '{dup}': one walk per site and device")
    if walks and not any(w["is_client"] for w in walks):
        errors.append("no walk has \"site\": \"client\": name the audited shop's walks 'client', competitors by name")
    if errors:
        return None, errors, warnings
    pages = {}
    if pages_dir:
        for path in sorted(glob.glob(os.path.join(pages_dir, "*.htm*"))):
            with open(path, encoding="utf-8", errors="replace") as fh:
                pages[os.path.basename(path)] = count_page(fh.read(), os.path.basename(path))
    rows, gaps, not_like = comparison(walks)
    missing = sorted({p for w in walks for p in w["pages"]} - set(pages)) if pages_dir else []
    flags = [{"page": name, "source": "markup", "pre_ticked_checkboxes": p["pre_ticked_checkboxes"]}
             for name, p in pages.items() if p["pre_ticked_checkboxes"]]
    flags += [{"page": f"{w['label']}: {sc['name']}", "source": "rendered page", "pre_ticked_checkboxes": sc["pre_ticked"]}
              for w in walks for sc in w["screens"] if sc["pre_ticked"]]
    # A button behind an open drawer is covered on purpose; a button under a cookie banner is a defect.
    # The texts let the reader tell the two apart.
    covered = [{"walk": w["label"], "screen": sc["name"], "primary_covered": sc["primary_covered"],
                "buttons": [b.get("text") for b in sc["primary_buttons"] if b.get("covered")]}
               for w in walks for sc in w["screens"] if sc["primary_covered"]]
    return {
        "date": date, "walks": walks, "comparison": rows, "gaps_to_first_checkout_form": gaps,
        "not_like_for_like": not_like,
        "markup_pages": list(pages.values()), "pages_missing": missing, "pre_ticked_flags": flags,
        "covered_primary_flags": covered,
        "baseline_rows": baseline_rows(walks, date),
        "note": "Walk logs (steps and screens) are the source of truth. markup_pages counts hidden markup too: hints only.",
    }, [], warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--walks", nargs="+", required=True, help="walk log JSON files (globs allowed)")
    ap.add_argument("--pages-dir")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("-o", "--out", default="path.json")
    a = ap.parse_args()
    files = sorted({f for pattern in a.walks for f in (glob.glob(pattern) or [pattern])})
    result, errors, warnings = run(files, a.pages_dir, a.date)
    for w in warnings:
        print("WARNING:", w, file=sys.stderr)
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    print(json.dumps({"out": a.out, "walks": len(result["walks"]), "markup_pages": len(result["markup_pages"]),
                      "screens": sum(len(w["screens"]) for w in result["walks"]),
                      "gaps": result["gaps_to_first_checkout_form"],
                      "not_like_for_like": result["not_like_for_like"],
                      "covered_primary_flags": result["covered_primary_flags"],
                      "pre_ticked_flags": len(result["pre_ticked_flags"]),
                      "pages_missing": result["pages_missing"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
