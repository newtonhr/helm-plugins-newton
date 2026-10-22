#!/usr/bin/env python3
"""Compute catalogue baseline metrics from a normalised catalogue export.

Usage:
    python3 catalogue_health.py catalogue.json --langs hr,en,de,it [--top 100] [-o health.json]
        [--expected-keys previous_health.json]   # re-runs: freeze each category's key set

Input: JSON list of products (schema in references/findings-schema.md, "catalogue.json").
Output: {"baseline": [...rows for the Baseline sheet...], "detail": {...}}.
Counts are exact; no sampling.
"""
import argparse
import datetime as dt
import html
import json
import re
from collections import defaultdict

TAG = re.compile(r"<[^>]+>")
GPSR_FIELDS = ("manufacturer", "eu_responsible", "identifier", "warnings")


def words(text):
    text = html.unescape(TAG.sub(" ", text or ""))
    return len(re.findall(r"\w+", text))


def filled(v):
    if v in (None, "", [], {}):
        return False
    return bool(html.unescape(TAG.sub(" ", str(v))).strip())


def text_of(p, lang):
    t = (p.get("texts") or {}).get(lang) or {}
    return t if isinstance(t, dict) else {}


def images_of(p):
    imgs = p.get("images") or []
    return [i if isinstance(i, dict) else {} for i in imgs] if isinstance(imgs, list) else []


def analyse(products, langs, top_n=100, thin=50, key_share=0.5, frozen_keys=None):
    n = len(products)
    detail = {"products": n, "languages": {}, "categories": {}, "gpsr": {}, "images": {}}

    for lang in langs:
        has_name = sum(1 for p in products if filled(text_of(p, lang).get("name")))
        counts = [words(text_of(p, lang).get("description")) for p in products]
        has_desc = sum(1 for c in counts if c > 0)
        thin_desc = sum(1 for c in counts if 0 < c < thin)
        detail["languages"][lang] = {
            "name_coverage": has_name / n if n else 0,
            "description_coverage": has_desc / n if n else 0,
            "description_missing_share": (n - has_desc) / n if n else 0,
            # thin share is over SKUs that HAVE a description; missing ones are a translation gap (CAT-2)
            "thin_description_share": thin_desc / has_desc if has_desc else 0,
            "thin_description_count": thin_desc,
        }

    by_cat = defaultdict(list)
    for p in products:
        by_cat[p.get("category") or "(none)"].append(p)
    for cat, items in by_cat.items():
        key_counts = defaultdict(int)
        for p in items:
            for k, v in (p.get("features") or {}).items():
                if filled(v):
                    key_counts[k] += 1
        if frozen_keys and cat in frozen_keys:
            expected = sorted(frozen_keys[cat])
        else:
            expected = sorted(k for k, c in key_counts.items() if c / len(items) >= key_share)
        if expected:
            comp = sum(sum(1 for k in expected if filled((p.get("features") or {}).get(k))) / len(expected)
                       for p in items) / len(items)
        else:
            comp = 0.0
        detail["categories"][cat] = {"products": len(items), "expected_keys": expected, "completeness": comp,
                                     "frozen": bool(frozen_keys and cat in frozen_keys)}

    ranked = sorted([p for p in products if isinstance(p.get("revenue_rank"), int)],
                    key=lambda p: p["revenue_rank"])[:top_n]
    sample = ranked if ranked else products[:top_n]
    detail["images"]["top_sample"] = len(sample)
    detail["images"]["top_sample_basis"] = "revenue_rank" if ranked else "first N (no revenue_rank given)"
    detail["images"]["share_top_with_3plus"] = (
        sum(1 for p in sample if len(images_of(p)) >= 3) / len(sample) if sample else 0)
    all_imgs = [img for p in products for img in images_of(p)]
    detail["images"]["total"] = len(all_imgs)
    for lang in langs:
        detail["images"][f"alt_coverage_{lang}"] = (
            sum(1 for img in all_imgs if filled((img.get("alt") if isinstance(img.get("alt"), dict) else {}).get(lang))) / len(all_imgs)
            if all_imgs else 0)

    gpsr_complete = sum(1 for p in products if all(filled((p.get("gpsr") or {}).get(f)) for f in GPSR_FIELDS))
    detail["gpsr"] = {"complete_share": gpsr_complete / n if n else 0,
                      "missing_by_field": {f: sum(1 for p in products if not filled((p.get("gpsr") or {}).get(f)))
                                           for f in GPSR_FIELDS}}
    sc = [p for p in products if p.get("safety_critical")]
    detail["safety_critical"] = {"count": len(sc), "ids": [p.get("id") for p in sc][:500]}
    return detail


def baseline_rows(detail, date):
    m = "catalogue_health.py over full export"
    rows = []
    for lang, d in detail["languages"].items():
        rows.append({"metric": f"Share of described SKUs with description < 50 words ({lang})",
                     "value": round(d["thin_description_share"], 4), "date": date, "method": m})
        rows.append({"metric": f"Share of SKUs with no description ({lang})",
                     "value": round(d["description_missing_share"], 4), "date": date, "method": m})
    cats = sorted(detail["categories"].items(), key=lambda kv: -kv[1]["products"])[:10]
    for cat, d in cats:
        rows.append({"metric": f"Attribute completeness: {cat}", "value": round(d["completeness"], 4),
                     "date": date, "method": m + f"; expected keys ({len(d['expected_keys'])}) frozen from first audit"
                     if d.get("frozen") else m + f"; expected keys = those filled on ≥50% of {d['products']} SKUs"})
    rows.append({"metric": f"Share of top-{detail['images']['top_sample']} SKUs with ≥ 3 images",
                 "value": round(detail["images"]["share_top_with_3plus"], 4), "date": date,
                 "method": m + "; basis " + detail["images"]["top_sample_basis"]})
    for k, v in detail["images"].items():
        if k.startswith("alt_coverage_"):
            rows.append({"metric": f"Image alt-text coverage ({k.rsplit('_', 1)[1]})", "value": round(v, 4),
                         "date": date, "method": m})
    rows.append({"metric": "GPSR fields complete (share of SKUs)", "value": round(detail["gpsr"]["complete_share"], 4),
                 "date": date, "method": m})
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("catalogue")
    ap.add_argument("--langs", required=True, help="comma-separated language codes, e.g. hr,en,de")
    ap.add_argument("--top", type=int, default=100)
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--expected-keys", help="previous health.json; reuse its expected keys per category")
    ap.add_argument("-o", "--out", default="health.json")
    a = ap.parse_args()
    with open(a.catalogue, encoding="utf-8") as fh:
        products = json.load(fh)
    frozen = None
    if a.expected_keys:
        with open(a.expected_keys, encoding="utf-8") as fh:
            prev = json.load(fh)
        frozen = {c: d["expected_keys"] for c, d in prev.get("detail", {}).get("categories", {}).items()}
    detail = analyse(products, [l.strip() for l in a.langs.split(",") if l.strip()], a.top, frozen_keys=frozen)
    out = {"baseline": baseline_rows(detail, a.date), "detail": detail}
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(json.dumps({"out": a.out, "products": detail["products"], "baseline_rows": len(out["baseline"])}))


if __name__ == "__main__":
    main()
