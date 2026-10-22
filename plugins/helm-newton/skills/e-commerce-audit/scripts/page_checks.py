#!/usr/bin/env python3
"""Check saved product/category pages for structured data and SEO basics.

Usage:
    python3 page_checks.py page1.html page2.html ... [-o pages.json]
    python3 page_checks.py --dir saved_pages/ [-o pages.json]

Works on HTML already fetched (Helm fetch_storefront_url, or browser "save page").
No network access. Checks: JSON-LD/microdata Product + Offer fields, shipping and
return policy markup, canonical, hreflang, robots, title, h1, image alt text, and
heuristic GPSR text hints. GPSR hints are label-style keyword matches ("Proizvođač: X") with snippets: confirm by eye.
"""
import argparse
import glob
import json
import os
import re
from html.parser import HTMLParser

# Label-style matches only ("Proizvođač: Lalizas"), to skip menus like "Proizvođači".
GPSR_HINTS = {
    "manufacturer": ["manufacturer", "proizvođač", "proizvodac", "hersteller", "produttore", "fabricant"],
    "eu_responsible": ["responsible person", "odgovorna osoba", "verantwortliche person", "persona responsabile",
                       "personne responsable"],
    "warnings": ["warning", "warnings", "upozorenje", "upozorenja", "warnhinweis", "warnhinweise", "avvertenze",
                 "avertissement", "sigurnosne upute", "safety information"],
}
# Contexts that are not GPSR (privacy/GDPR footers, payment security).
GPSR_EXCLUDE = ["za obradu", "obradu osobnih", "osobnih podataka", "data protection", "datenschutz",
                "personal data", "dati personali", "données personnelles"]
MICRODATA_PROPS = {"name", "image", "description", "brand", "sku", "gtin", "gtin8", "gtin12", "gtin13", "gtin14",
                   "mpn", "offers", "price", "lowPrice", "priceCurrency", "availability", "shippingDetails",
                   "hasMerchantReturnPolicy", "aggregateRating", "review"}


class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.jsonld, self._in_ld, self._buf = [], False, []
        self.canonical, self.hreflang, self.robots, self.html_lang = None, [], None, None
        self.title, self._in_title = "", False
        self.h1, self.imgs, self.img_no_alt = 0, 0, 0
        self.itemtypes, self.text, self.itemprops = [], [], set()
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self._in_ld, self._buf = True, []
        elif tag in ("script", "style", "noscript"):
            self._skip += 1
        elif tag == "link":
            rel = a.get("rel", "").lower()
            if rel == "canonical":
                self.canonical = a.get("href")
            elif rel == "alternate" and a.get("hreflang"):
                self.hreflang.append({"hreflang": a["hreflang"], "href": a.get("href")})
        elif tag == "meta" and a.get("name", "").lower() == "robots":
            self.robots = a.get("content")
        elif tag == "html":
            self.html_lang = a.get("lang")
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "img":
            self.imgs += 1
            if not a.get("alt", "").strip():
                self.img_no_alt += 1
        if "itemtype" in a:
            self.itemtypes.append(a["itemtype"].rsplit("/", 1)[-1])
        if a.get("itemprop"):
            self.itemprops.update(x for x in a["itemprop"].split() if x in MICRODATA_PROPS)

    def handle_endtag(self, tag):
        if tag == "script" and self._in_ld:
            self._in_ld = False
            raw = "".join(self._buf).strip()
            try:
                self.jsonld.append(json.loads(raw))
            except json.JSONDecodeError:
                self.jsonld.append({"_parse_error": raw[:200]})
        elif tag in ("script", "style", "noscript") and self._skip:
            self._skip -= 1
        elif tag == "title":
            self._in_title = False
        elif tag in ("dt", "th") and not self._skip:
            self.text.append(":")   # label/value layouts (<dt>Proizvođač</dt><dd>X</dd>) read as "label: value"

    def handle_data(self, data):
        if self._in_ld:
            self._buf.append(data)
        elif self._in_title:
            self.title += data
        elif not self._skip:
            self.text.append(data)


def walk(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk(v)


def types_of(n):
    t = n.get("@type")
    return set(t if isinstance(t, list) else [t]) if t else set()


def microdata_checks(props):
    has = props.__contains__
    return {
        "product_markup": "microdata",
        "name": has("name"), "image": has("image"), "description": has("description"), "brand": has("brand"),
        "sku": has("sku"), "gtin": any(has(k) for k in ("gtin", "gtin8", "gtin12", "gtin13", "gtin14")),
        "mpn": has("mpn"), "offer": has("offers"), "price": has("price") or has("lowPrice"),
        "priceCurrency": has("priceCurrency"), "availability": has("availability"),
        "shippingDetails": has("shippingDetails"), "hasMerchantReturnPolicy": has("hasMerchantReturnPolicy"),
        "aggregateRating": has("aggregateRating"), "review": has("review"),
    }


def gpsr_hints(text):
    found = {}
    for field, words in GPSR_HINTS.items():
        snippets = []
        for w in words:
            for m in re.finditer(r"(?<!\w)" + re.escape(w) + r"(?:\s+\w+){0,3}\s*[:\-–]\s*\S", text):
                ctx = text[max(0, m.start() - 40): m.end() + 60]
                if not any(x in ctx for x in GPSR_EXCLUDE):
                    snippets.append(ctx.strip())
        found[field] = {"found": bool(snippets), "snippets": snippets[:3]}
    return found


def product_checks(jsonld):
    nodes = [n for doc in jsonld for n in walk(doc)]
    products = [n for n in nodes if "Product" in types_of(n) or "ProductGroup" in types_of(n)]
    if not products:
        return {"product_markup": None}
    p = products[0]
    offers = p.get("offers") or p.get("hasVariant") or {}
    offer_nodes = [o for o in walk(offers) if types_of(o) & {"Offer", "AggregateOffer"}] or (
        [offers] if isinstance(offers, dict) and offers else [])
    o = offer_nodes[0] if offer_nodes else {}
    gtin = any(k in p or k in o for k in ("gtin", "gtin8", "gtin12", "gtin13", "gtin14", "isbn"))
    return {
        "product_markup": "jsonld",
        "name": bool(p.get("name")), "image": bool(p.get("image")), "description": bool(p.get("description")),
        "brand": bool(p.get("brand")), "sku": bool(p.get("sku") or o.get("sku")), "gtin": gtin,
        "mpn": bool(p.get("mpn")),
        "offer": bool(o), "price": bool(o.get("price") or o.get("lowPrice")),
        "priceCurrency": bool(o.get("priceCurrency")), "availability": bool(o.get("availability")),
        "shippingDetails": bool(o.get("shippingDetails")),
        "hasMerchantReturnPolicy": bool(o.get("hasMerchantReturnPolicy") or p.get("hasMerchantReturnPolicy")),
        "aggregateRating": bool(p.get("aggregateRating")), "review": bool(p.get("review")),
    }


def check(html_text, name):
    c = Collector()
    c.feed(html_text)
    text = " ".join(" ".join(c.text).split()).lower()
    res = {
        "page": name,
        "title": c.title.strip()[:200], "html_lang": c.html_lang, "h1_count": c.h1,
        "canonical": c.canonical, "robots": c.robots,
        "hreflang": c.hreflang, "hreflang_count": len(c.hreflang),
        "hreflang_has_x_default": any(h["hreflang"].lower() == "x-default" for h in c.hreflang),
        "images": c.imgs, "images_missing_alt": c.img_no_alt,
        "jsonld_blocks": len(c.jsonld), "jsonld_parse_errors": sum(1 for d in c.jsonld if "_parse_error" in d),
        "microdata_types": sorted(set(c.itemtypes)),
        "visible_words": len(re.findall(r"\w+", text)),
        "gpsr_hints": gpsr_hints(text),
    }
    pc = product_checks([d for d in c.jsonld if "_parse_error" not in d])
    if pc["product_markup"] is None and "Product" in c.itemtypes:
        pc = microdata_checks(c.itemprops)
    res.update(pc)
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*")
    ap.add_argument("--dir")
    ap.add_argument("-o", "--out", default="pages.json")
    a = ap.parse_args()
    files = list(a.files)
    if a.dir:
        files += sorted(glob.glob(os.path.join(a.dir, "*.htm*")))
    results = []
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as fh:
            results.append(check(fh.read(), os.path.basename(path)))
    prod = [r for r in results if r.get("product_markup")]
    summary = {"pages": len(results), "with_product_markup": len(prod),
               "markup_types": sorted({r["product_markup"] for r in prod})}
    for k in ("gtin", "brand", "shippingDetails", "hasMerchantReturnPolicy", "aggregateRating", "availability"):
        summary[f"share_{k}"] = round(sum(1 for r in prod if r.get(k)) / len(prod), 4) if prod else 0
    summary["pages_without_canonical"] = sum(1 for r in results if not r["canonical"])
    summary["pages_without_hreflang"] = sum(1 for r in results if not r["hreflang_count"])
    summary["images_missing_alt"] = sum(r["images_missing_alt"] for r in results)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump({"summary": summary, "pages": results}, fh, ensure_ascii=False, indent=2)
    print(json.dumps({"out": a.out, **summary}))


if __name__ == "__main__":
    main()
