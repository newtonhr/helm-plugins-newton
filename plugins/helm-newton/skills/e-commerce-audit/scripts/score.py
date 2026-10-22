#!/usr/bin/env python3
"""Score e-commerce-audit findings deterministically.

Usage:
    python3 score.py findings.json [-o scored.json]

Reads the findings file (schema in references/findings-schema.md), validates it,
applies the scoring rules, and writes scored.json. The same rules are written as
live formulas into the .xlsx by build_backlog.py; `build_backlog.py verify`
proves the two agree.

The behavior lane (`behavior` list: BEH-*, PATH-*, NEWB-* cards) is validated and
ranked here but never scored in EUR: it has no margin base, no bands and no quadrant.

Exit code 1 on validation errors. Warnings do not fail the run.
"""
import argparse
import json
import re
import sys

# ---- Scoring constants (mirror the Settings sheet in build_backlog.py) ----
RIGOR_WEIGHTS = {"A": 1.0, "B": 0.7, "C": 0.4, "Policy": 0.4, "C until verified": 0.4}
TRANSFER_VALUES = (0.4, 0.7, 1.0)
TRANSFER_CAPS = {"CAT-1": 0.4, "CAT-2": 0.4, "REC-2": 0.4}
ENABLERS = {"SRC-2", "SRC-9"}
EST_FACTOR = 0.7
TEST_FIRST_THRESHOLD = 0.3
RUN_COST_THRESHOLD = 300.0
IMPACT_BOUNDS = (2000, 10000, 25000, 50000)   # band = 1 + number of bounds <= value
EFFORT_BOUNDS = (3, 10, 20, 40)              # band = 1 + number of bounds < days
DEFAULT_EFFECT = (0.01, 0.03)
INACTIVE = {"done", "n/a"}
STATUSES = {"done", "partial", "missing", "n/a"}
KINDS = {"item", "bundle", "child"}
QUADRANT_ORDER = {"Quick win": 0, "Big bet": 1, "Fill-in": 2, "Skip": 3, "Done": 4, "N/A": 5}
# ---- Behavior lane (unscored; see references/scoring.md section 7) ----
BEHAVIOR_PREFIXES = ("BEH-", "PATH-", "NEWB-")
BEHAVIOR_GRADES = ("A", "B", "C")            # also the rank order
BEHAVIOR_EFFORTS = ("S", "M", "L")           # also the rank order
BEHAVIOR_KINDS = ("defect", "hypothesis")    # a defect is something seen broken on the path; it ranks first
BEHAVIOR_REQUIRED = {"hypothesis": ("title", "observation", "evidence", "hypothesis", "measure"),
                     "defect": ("title", "observation", "evidence", "measure")}
# Cards that show the shopper a claim about the shop: the claim must come from live shop data.
TRUTH_CARDS = {"BEH-1", "BEH-2", "BEH-3", "BEH-5", "BEH-10"}
# Grade of each library card (practice-library.md section 12). A test keeps this map equal to the library.
BEHAVIOR_CARD_GRADES = {"PATH-1": "B", "PATH-2": "B", "PATH-4": "B", "BEH-1": "A", "BEH-2": "A", "BEH-3": "B",
                        "BEH-4": "A", "BEH-5": "B", "BEH-6": "A", "BEH-7": "B", "BEH-8": "A", "BEH-9": "B",
                        "BEH-10": "C"}
DEFECT_ONLY_CARDS = {"PATH-3"}               # filed as a defect, or done; never a hypothesis
MONEY_HINT = re.compile(r"(€|\beur\b)\s*\d|\d\s*(€|\beur\b)", re.I)
BEHAVIOR_TOP_N = 7
# Words that point at banned patterns. A hit is a warning for the reviewer, not a verdict.
BANNED_HINTS = ("decoy", "mamac", "countdown", "odbrojavanje", "timer", "fake", "lažn", "pre-tick", "confirmsham")
# Rounding shared with the workbook formulas (ROUND(...,2) / ROUND(...,4)) so band edges agree.
EUR_DP, DAYS_DP, CONF_DP = 2, 4, 4


def impact_band(eur):
    if eur is None:
        return None
    return 1 + sum(1 for b in IMPACT_BOUNDS if eur >= b)


def effort_band(days, run_cost):
    base = 1 + sum(1 for b in EFFORT_BOUNDS if days > b)
    if (run_cost or 0) > RUN_COST_THRESHOLD:
        base += 1
    return min(5, base)


def quadrant(status, ib, eb):
    if status == "done":
        return "Done"
    if status == "n/a":
        return "N/A"
    if ib is None or eb is None:
        return None
    if ib >= 3 and eb <= 2:
        return "Quick win"
    if ib >= 3 and eb >= 3:
        return "Big bet"
    if eb <= 2:
        return "Fill-in"
    return "Skip"


def is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def item_impact_eur(f):
    base, lo, hi = f.get("margin_base_eur"), f.get("effect_low"), f.get("effect_high")
    if not (is_num(base) and is_num(lo) and is_num(hi)):
        return None
    return round(base * (lo + hi) / 2, EUR_DP)


def _check_number(f, key, errors, fid, lo=None, hi=None, required=False):
    v = f.get(key)
    if v is None:
        if required:
            errors.append(f"{fid}: {key} is required")
        return
    if not is_num(v):
        errors.append(f"{fid}: {key} must be a number, got {v!r}")
        return
    if lo is not None and v < lo:
        errors.append(f"{fid}: {key} must be >= {lo}, got {v}")
    if hi is not None and v > hi:
        errors.append(f"{fid}: {key} must be <= {hi}, got {v} (effects are fractions: 0.02 = 2%)")


def validate_and_normalise(data):
    errors, warnings = [], []
    findings = data.get("findings")
    lane_only = isinstance(findings, list) and not findings and bool(data.get("behavior"))
    if not isinstance(findings, list) or (not findings and not lane_only):
        return ["'findings' must be a non-empty list (it may be empty only in a behavior-lane-only run)"], warnings
    for i, f in enumerate(findings):
        if not isinstance(f, dict):
            errors.append(f"finding #{i + 1}: a finding is an object")
        elif not f.get("id"):
            errors.append(f"finding #{i + 1}: id is required")
    if errors:
        return errors, warnings
    ids = [f["id"] for f in findings]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        errors.append(f"duplicate ids: {sorted(dupes)}")

    for f in findings:
        f.setdefault("kind", "item")
        if f["kind"] not in KINDS:
            errors.append(f"{f['id']}: kind must be one of {sorted(KINDS)}")
        if f["kind"] != "child" and f.get("bundle"):
            errors.append(f"{f['id']}: only kind 'child' may have a 'bundle' field")
    if errors:
        return errors, warnings

    bundles = {f["id"]: f for f in findings if f["kind"] == "bundle"}
    children = {}
    for f in findings:
        if f["kind"] == "child":
            if f.get("bundle") not in bundles:
                errors.append(f"{f['id']}: child must name an existing bundle in 'bundle'")
            else:
                children.setdefault(f["bundle"], []).append(f)

    # Bundle status and safety flag derive from children, before any other check.
    for bid, b in bundles.items():
        kids = children.get(bid, [])
        if not kids:
            errors.append(f"{bid}: bundle has no children")
            continue
        statuses = {k.get("status") for k in kids}
        if statuses <= INACTIVE:
            b["status"] = "done" if "done" in statuses else "n/a"
        else:
            b["status"] = "missing" if statuses <= {"missing"} else "partial"
            active = [k for k in kids if k.get("status") not in INACTIVE]
            if len(active) == 1:
                warnings.append(f"{bid}: only one active child ({active[0]['id']}); score it as a normal item")
        if any(k.get("safety_critical") for k in kids):
            b["safety_critical"] = True

    for f in findings:
        fid, kind, status = f["id"], f["kind"], f.get("status")
        if status not in STATUSES:
            errors.append(f"{fid}: status must be one of {sorted(STATUSES)}")
            continue
        if fid.startswith("LEG-"):
            errors.append(f"{fid}: legal items belong in 'legal', not 'findings'")
        if fid.startswith("OS-"):
            errors.append(f"{fid}: OS cards are methods; they are not findings")
        if fid.startswith(BEHAVIOR_PREFIXES):
            errors.append(f"{fid}: behavior cards belong in 'behavior', not 'findings'")
        f.setdefault("cards", [fid] if kind != "bundle" else [])
        if kind != "bundle" and not str(f.get("evidence", "")).strip():
            errors.append(f"{fid}: evidence is required (URL, screenshot, or data query)")
        if kind == "item" and set(f["cards"]) & ENABLERS:
            warnings.append(f"{fid}: enabler {sorted(set(f['cards']) & ENABLERS)} scored standalone; put it in a bundle")

        if kind in ("item", "child") and status not in INACTIVE:
            if f.get("rigor") not in RIGOR_WEIGHTS:
                errors.append(f"{fid}: rigor must be one of {list(RIGOR_WEIGHTS)}")
            t = f.get("transfer")
            if not is_num(t) or t not in TRANSFER_VALUES:
                errors.append(f"{fid}: transfer must be one of {TRANSFER_VALUES}, got {t!r}")
            else:
                for card in f["cards"]:
                    cap = TRANSFER_CAPS.get(card)
                    if cap is not None and t > cap:
                        warnings.append(f"{fid}: transfer capped {t} -> {cap} ({card})")
                        f["transfer"] = t = cap
            if f.get("margin_base_eur") is None:
                errors.append(f"{fid}: margin_base_eur is required; estimate it (e.g. total web margin x share "
                              f"affected) and set estimated=true")
            _check_number(f, "margin_base_eur", errors, fid, lo=0)
            if f.get("effect_low") is None or f.get("effect_high") is None:
                f["effect_low"], f["effect_high"] = DEFAULT_EFFECT
                f["estimated"] = True
                warnings.append(f"{fid}: no measured effect; default 1-3% applied, marked estimated")
            _check_number(f, "effect_low", errors, fid, lo=0, hi=1)
            _check_number(f, "effect_high", errors, fid, lo=0, hi=1)
            if is_num(f.get("effect_low")) and is_num(f.get("effect_high")) and f["effect_low"] > f["effect_high"]:
                errors.append(f"{fid}: effect_low must not exceed effect_high")
            if kind == "child" and set(f["cards"]) <= ENABLERS:
                f["margin_base_eur"] = 0
                warnings.append(f"{fid}: enabler child gets no impact credit (margin base set to 0)")
            if f.get("rigor") == "Policy":
                warnings.append(f"{fid}: Policy rigor scored at C weight (0.4) for impact")
        if kind in ("item", "bundle") and status not in INACTIVE:
            _check_number(f, "newton_days", errors, fid, lo=0, required=True)
            _check_number(f, "client_days", errors, fid, lo=0, required=True)
        if kind in ("item", "bundle"):
            _check_number(f, "run_cost_month", errors, fid, lo=0)
            if f.get("safety_critical") and status not in INACTIVE \
                    and "per-sku" not in str(f.get("acceptance_criteria", "")).lower():
                errors.append(f"{fid}: safety-critical; acceptance criteria must require per-SKU sign-off")
        f["estimated"] = bool(f.get("estimated", False))
        if f.get("run_cost_month") is None:
            f["run_cost_month"] = 0
    return errors, warnings


def validate_behavior(data):
    """Validate and normalise the unscored behavior lane. Returns (errors, warnings)."""
    errors, warnings = [], []
    lane = data.get("behavior")
    if lane is None:
        data["behavior"] = []
        return errors, warnings
    if not isinstance(lane, list):
        return ["'behavior' must be a list"], warnings
    raw = data.get("findings")
    finding_ids = {f.get("id") for f in (raw if isinstance(raw, list) else []) if isinstance(f, dict)}
    seen = set()
    for i, b in enumerate(lane):
        bid = b.get("id") if isinstance(b, dict) else None
        if not bid:
            errors.append(f"behavior #{i + 1}: id is required")
            continue
        if not str(bid).startswith(BEHAVIOR_PREFIXES):
            errors.append(f"{bid}: behavior ids start with one of {list(BEHAVIOR_PREFIXES)}")
        if bid in seen:
            errors.append(f"{bid}: duplicate id in 'behavior'")
        if bid in finding_ids:
            errors.append(f"{bid}: id is in both 'findings' and 'behavior'")
        seen.add(bid)
        status = b.get("status")
        if status not in STATUSES:
            errors.append(f"{bid}: status must be one of {sorted(STATUSES)}")
            continue
        b.setdefault("kind", "hypothesis")
        if b["kind"] not in BEHAVIOR_KINDS:
            errors.append(f"{bid}: kind must be one of {list(BEHAVIOR_KINDS)}")
            continue
        for money_key in ("margin_base_eur", "effect_low", "effect_high", "impact_eur"):
            if b.get(money_key) is not None:
                errors.append(f"{bid}: {money_key} is not allowed in the behavior lane (it is unscored)")
        if not str(b.get("evidence", "")).strip():
            errors.append(f"{bid}: evidence is required (path.json, screenshot, URL or data query)")
        text = " ".join(str(b.get(k, "")) for k in ("title", "hypothesis", "acceptance_criteria")).lower()
        hits = [w for w in BANNED_HINTS if w in text]
        if hits:
            warnings.append(f"{bid}: text mentions {hits}; the reviewer must confirm this is not a banned pattern")
        # The truth rule also covers a signal the shop already shows: a "done" card must name its live data.
        if bid in TRUTH_CARDS and status != "n/a" and not str(b.get("truth_source", "")).strip():
            errors.append(f"{bid}: truth_source is required (the live shop data behind the signal), also when done")
        if status in INACTIVE:
            continue
        for key in BEHAVIOR_REQUIRED[b["kind"]]:
            if not str(b.get(key, "")).strip():
                errors.append(f"{bid}: {key} is required for an active behavior {b['kind']}")
        if b["kind"] == "defect":
            if b.get("grade") is not None:
                errors.append(f"{bid}: a defect has no evidence grade (it was seen broken); remove 'grade'")
        elif bid in DEFECT_ONLY_CARDS:
            errors.append(f"{bid}: this card is filed as kind 'defect' (something seen broken) or as done")
        elif b.get("grade") not in BEHAVIOR_GRADES:
            errors.append(f"{bid}: grade must be one of {list(BEHAVIOR_GRADES)}")
        elif bid in BEHAVIOR_CARD_GRADES and b["grade"] != BEHAVIOR_CARD_GRADES[bid]:
            errors.append(f"{bid}: grade must be {BEHAVIOR_CARD_GRADES[bid]}, the library card's grade")
        promise = " ".join(str(b.get(k, "")) for k in ("title", "hypothesis", "measure"))
        if MONEY_HINT.search(promise):
            warnings.append(f"{bid}: title, hypothesis or measure names a money amount; the lane carries no € impact")
        if b.get("effort") not in BEHAVIOR_EFFORTS:
            errors.append(f"{bid}: effort must be one of {list(BEHAVIOR_EFFORTS)}")
        if str(bid).startswith("NEWB-") and b.get("grade") in ("A", "B") and not str(b.get("source_url", "")).strip():
            errors.append(f"{bid}: a card outside the library is grade C unless source_url cites the study")
    return errors, warnings


def validate_path(data):
    """`path` holds the comparison rows copied from path.json: a list of {metric, values: {walk: number}}."""
    rows = data.get("path")
    if rows is None:
        data["path"] = []
        return []
    if not isinstance(rows, list):
        return ["'path' must be a list: copy path.json -> comparison (not the whole file)"]
    errors = []
    for i, r in enumerate(rows, start=1):
        if not (isinstance(r, dict) and isinstance(r.get("metric"), str) and isinstance(r.get("values"), dict)):
            errors.append(f"path row {i}: expected {{'metric': text, 'values': {{walk: number}}}}")
    return errors


def rank_behavior(lane):
    """Active items first; defects before hypotheses; then evidence grade, effort, id. No EUR, no bands."""
    def key(b):
        active = b["status"] not in INACTIVE
        g = BEHAVIOR_GRADES.index(b["grade"]) if b.get("grade") in BEHAVIOR_GRADES else len(BEHAVIOR_GRADES)
        e = BEHAVIOR_EFFORTS.index(b["effort"]) if b.get("effort") in BEHAVIOR_EFFORTS else len(BEHAVIOR_EFFORTS)
        if b.get("kind") == "defect":
            return (not active, 0, 0, e, b["id"])
        return (not active, 1, g, e, b["id"])
    ranked = sorted(lane, key=key)
    n = 0
    for b in ranked:
        if b["status"] in INACTIVE:
            b["lane_rank"] = None
        else:
            n += 1
            b["lane_rank"] = n
    return ranked


def score(data):
    errors, warnings = validate_and_normalise(data)
    b_errors, b_warnings = validate_behavior(data)
    errors, warnings = errors + b_errors + validate_path(data), warnings + b_warnings
    if errors:
        return None, errors, warnings
    findings = data["findings"]
    kids_of = {}
    for f in findings:
        if f["kind"] == "child":
            kids_of.setdefault(f["bundle"], []).append(f)

    for f in findings:
        f["impact_eur"] = item_impact_eur(f) if f["kind"] != "bundle" else None
        f["rigor_weight"] = RIGOR_WEIGHTS.get(f.get("rigor")) if f.get("rigor") else None

    for f in findings:
        if f["kind"] != "bundle":
            continue
        kids = kids_of[f["id"]]
        f["cards"] = sorted({card for c in kids for card in c["cards"]})
        active = [c for c in kids if c["status"] not in INACTIVE and c["impact_eur"] is not None]
        if active:
            values = [c["impact_eur"] for c in active]
            top = max(active, key=lambda c: c["impact_eur"])
            f["impact_eur"] = round(max(values) + 0.5 * (sum(values) - max(values)), EUR_DP)
            f["rigor"], f["rigor_weight"] = top["rigor"], top["rigor_weight"]
            f["transfer"], f["estimated"] = top["transfer"], top["estimated"]
        else:
            f["rigor"] = f["rigor_weight"] = f["transfer"] = None

    for f in findings:
        if f["kind"] == "child" or f["status"] in INACTIVE:
            f.update(impact_band=None, effort_band=None, est_factor=None, confidence=None,
                     priority=None, test_first=None, pr_faq=None)
            f["quadrant"] = quadrant(f["status"], None, None) if f["kind"] != "child" else None
            continue
        ib = impact_band(f["impact_eur"])
        eb = effort_band(round(f["newton_days"] + f["client_days"], DAYS_DP), f.get("run_cost_month"))
        est = EST_FACTOR if f["estimated"] else 1.0
        conf = round(f["rigor_weight"] * f["transfer"] * est, CONF_DP) if f.get("rigor_weight") is not None else None
        f.update(impact_band=ib, effort_band=eb, est_factor=est, confidence=conf,
                 priority=(ib * conf / eb) if (ib is not None and conf is not None) else None,
                 test_first=(conf < TEST_FIRST_THRESHOLD) if conf is not None else None,
                 pr_faq=eb >= 4, quadrant=quadrant(f["status"], ib, eb))

    data["findings"] = order(findings)
    data["behavior"] = rank_behavior(data["behavior"])
    data["summary"] = summarise(data["findings"], data["behavior"])
    return data, errors, warnings


def order(findings):
    """Parents by quadrant then priority; each bundle followed by its children (active first)."""
    parents = [f for f in findings if f["kind"] != "child"]
    parents.sort(key=lambda f: (QUADRANT_ORDER.get(f["quadrant"], 9), -(f["priority"] or 0), f["id"]))
    out = []
    for p in parents:
        out.append(p)
        if p["kind"] == "bundle":
            kids = [f for f in findings if f["kind"] == "child" and f.get("bundle") == p["id"]]
            kids.sort(key=lambda c: (c["status"] in INACTIVE, -(c["impact_eur"] or 0), c["id"]))
            out.extend(kids)
    return out


def summarise(findings, behavior=()):
    scored = [f for f in findings if f["kind"] != "child"]
    qw = [f for f in scored if f["quadrant"] == "Quick win" and not f["test_first"]]
    active = [b for b in behavior if b.get("lane_rank")]
    return {
        "counts": {q: sum(1 for f in scored if f["quadrant"] == q) for q in QUADRANT_ORDER},
        "report_quick_wins": [f["id"] for f in qw[:10]],
        "test_first": [f["id"] for f in scored if f.get("test_first")],
        "pr_faq_needed": [f["id"] for f in scored if f.get("pr_faq")],
        "behavior_defects": [b["id"] for b in active if b.get("kind") == "defect"],
        "behavior_top": [b["id"] for b in active if b.get("kind") != "defect"][:BEHAVIOR_TOP_N],
        "behavior_counts": {s: sum(1 for b in behavior if b["status"] == s) for s in sorted(STATUSES)},
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("findings")
    ap.add_argument("-o", "--out", default="scored.json")
    a = ap.parse_args()
    with open(a.findings, encoding="utf-8") as fh:
        data = json.load(fh)
    result, errors, warnings = score(data)
    for w in warnings:
        print("WARNING:", w, file=sys.stderr)
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    print(json.dumps({"out": a.out, "warnings": len(warnings), **result["summary"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
