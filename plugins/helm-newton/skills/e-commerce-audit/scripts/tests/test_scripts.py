"""Tests for e-commerce-audit scripts. Run: python3 -m unittest discover -s scripts/tests -v"""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import build_backlog as BB  # noqa: E402
import catalogue_health as CH  # noqa: E402
import diff_runs as DR  # noqa: E402
import kappa as KP  # noqa: E402
import page_checks as PC  # noqa: E402
import path_metrics as PM  # noqa: E402
import score as S  # noqa: E402

RECALC_CANDIDATES = ["/mnt/skills/public/xlsx/scripts/recalc.py"]


def fixture():
    with open(os.path.join(HERE, "fixture_findings.json"), encoding="utf-8") as fh:
        return json.load(fh)


def by_id(data):
    return {f["id"]: f for f in data["findings"]}


class ScoreTests(unittest.TestCase):
    def setUp(self):
        self.data, self.errors, self.warnings = S.score(fixture())
        self.assertEqual(self.errors, [])
        self.f = by_id(self.data)

    def test_simple_quick_win(self):
        f = self.f["CHK-1"]
        self.assertAlmostEqual(f["impact_eur"], 15000)
        self.assertEqual((f["impact_band"], f["effort_band"]), (3, 1))
        self.assertAlmostEqual(f["confidence"], 0.49)
        self.assertAlmostEqual(f["priority"], 1.47)
        self.assertEqual(f["quadrant"], "Quick win")

    def test_bundle(self):
        b = self.f["BND-QRY"]
        self.assertAlmostEqual(b["impact_eur"], 12000 + 0.5 * 4000)
        self.assertEqual((b["impact_band"], b["effort_band"]), (3, 2))
        self.assertEqual((b["rigor"], b["transfer"]), ("A", 0.7))
        self.assertAlmostEqual(b["priority"], 1.05)
        self.assertEqual(b["quadrant"], "Quick win")
        self.assertTrue(self.f["SRC-7"]["estimated"])
        self.assertIsNone(self.f["SRC-1"]["priority"])

    def test_transfer_cap_and_run_cost(self):
        f = self.f["CAT-1"]
        self.assertEqual(f["transfer"], 0.4)
        self.assertEqual(f["effort_band"], 5)
        self.assertAlmostEqual(f["priority"], 4 * 0.4 / 5)
        self.assertEqual(f["quadrant"], "Big bet")
        self.assertTrue(f["pr_faq"])
        self.assertTrue(any("capped" in w for w in self.warnings))

    def test_policy_and_test_first(self):
        f = self.f["DSC-1"]
        self.assertAlmostEqual(f["confidence"], 0.28)
        self.assertTrue(f["test_first"])
        self.assertNotIn("DSC-1", self.data["summary"]["report_quick_wins"])

    def test_inactive_and_skip(self):
        self.assertEqual(self.f["PDP-2"]["quadrant"], "Done")
        self.assertEqual(self.f["MER-1"]["quadrant"], "N/A")
        self.assertEqual(self.f["SVC-4"]["quadrant"], "Skip")

    def test_order(self):
        ids = [f["id"] for f in self.data["findings"]]
        self.assertEqual(ids, ["CHK-1", "BND-QRY", "SRC-1", "SRC-7", "SRC-4", "CAT-1", "DSC-1", "SVC-4",
                               "PDP-2", "MER-1"])

    def test_validation_errors(self):
        bad = fixture()
        bad["findings"].append({"id": "LEG-3", "status": "missing"})
        bad["findings"].append({"id": "BND-X", "kind": "bundle", "status": "missing", "newton_days": 1,
                                "client_days": 1})
        _, errors, _ = S.score(bad)
        self.assertTrue(any("LEG-3" in e for e in errors))
        self.assertTrue(any("BND-X" in e and "no children" in e for e in errors))

    def test_enabler_warning(self):
        d = fixture()
        d["findings"].append({"id": "SRC-2", "status": "missing", "rigor": "B", "transfer": 0.7,
                              "margin_base_eur": 1000, "effect_low": 0.01, "effect_high": 0.02,
                              "newton_days": 1, "client_days": 1, "evidence": "x"})
        _, errors, warnings = S.score(d)
        self.assertEqual(errors, [])
        self.assertTrue(any("enabler" in w for w in warnings))


class ValidationTests(unittest.TestCase):
    def errors_for(self, mutate):
        d = fixture()
        mutate(d)
        _, errors, _ = S.score(d)
        return errors

    def test_missing_margin_is_error(self):
        def m(d):
            next(f for f in d["findings"] if f["id"] == "CHK-1").pop("margin_base_eur")
        self.assertTrue(any("margin_base_eur is required" in e for e in self.errors_for(m)))

    def test_percent_effect_is_error(self):
        def m(d):
            next(f for f in d["findings"] if f["id"] == "CHK-1")["effect_high"] = 4
        self.assertTrue(any("effect_high" in e for e in self.errors_for(m)))

    def test_string_number_and_bad_transfer(self):
        def m(d):
            f = next(f for f in d["findings"] if f["id"] == "CHK-1")
            f["margin_base_eur"], f["transfer"] = "500000", 0.9
        errs = self.errors_for(m)
        self.assertTrue(any("must be a number" in e for e in errs))
        self.assertTrue(any("transfer must be" in e for e in errs))

    def test_item_with_bundle_field_and_missing_evidence(self):
        def m(d):
            f = next(f for f in d["findings"] if f["id"] == "CHK-1")
            f["bundle"], f["evidence"] = "BND-QRY", ""
        errs = self.errors_for(m)
        self.assertTrue(any("only kind 'child'" in e for e in errs))

    def test_bundle_status_derived_before_checks(self):
        d = fixture()
        next(f for f in d["findings"] if f["id"] == "BND-QRY")["status"] = "n/a"
        data, errors, _ = S.score(d)
        self.assertEqual(errors, [])
        self.assertEqual(by_id(data)["BND-QRY"]["status"], "partial")   # SRC-4 child is done

    def test_safety_critical_bundle_needs_per_sku(self):
        def m(d):
            next(f for f in d["findings"] if f["id"] == "SRC-1")["safety_critical"] = True
            next(f for f in d["findings"] if f["id"] == "BND-QRY")["acceptance_criteria"] = "batch approval"
        self.assertTrue(any("per-SKU" in e for e in self.errors_for(m)))

    def test_float_edge_matches_band(self):
        d = fixture()
        f = next(f for f in d["findings"] if f["id"] == "CHK-1")
        f.update(margin_base_eur=250000, effect_low=0.036, effect_high=0.044)   # 9999.999... unrounded
        data, errors, _ = S.score(d)
        self.assertEqual(errors, [])
        self.assertEqual(by_id(data)["CHK-1"]["impact_band"], 3)


class BacklogTests(unittest.TestCase):
    def test_build_recalc_verify(self):
        data, errors, _ = S.score(fixture())
        self.assertEqual(errors, [])
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "backlog.xlsx")
            BB.build(data, out)
            recalc = next((p for p in RECALC_CANDIDATES if os.path.exists(p)), None)
            if not recalc:
                self.skipTest("recalc.py not available")
            res = subprocess.run([sys.executable, recalc, out, "60"], capture_output=True, text=True)
            info = json.loads(res.stdout)
            self.assertEqual(info.get("status"), "success", res.stdout)
            self.assertEqual(BB.verify(data, out), [])

    def test_edges_and_all_inactive_after_recalc(self):
        recalc = next((p for p in RECALC_CANDIDATES if os.path.exists(p)), None)
        if not recalc:
            self.skipTest("recalc.py not available")
        d = fixture()
        f = next(f for f in d["findings"] if f["id"] == "CHK-1")
        f.update(margin_base_eur=250000, effect_low=0.036, effect_high=0.044, newton_days=2.1, client_days=0.9)
        g = next(f for f in d["findings"] if f["id"] == "DSC-1")
        g.update(margin_base_eur=100000, effect_low=0.12, effect_high=0.38, run_cost_month=300)   # 25,000 exactly
        done = {"meta": {}, "findings": [{"id": "PDP-2", "status": "done", "evidence": "x"},
                                        {"id": "MER-1", "status": "n/a", "evidence": "y"}]}
        with tempfile.TemporaryDirectory() as tmp:
            for name, src in (("edge.xlsx", d), ("done.xlsx", done)):
                data, errors, _ = S.score(src)
                self.assertEqual(errors, [])
                out = os.path.join(tmp, name)
                BB.build(data, out)
                subprocess.run([sys.executable, recalc, out, "60"], capture_output=True, text=True)
                self.assertEqual(BB.verify(data, out), [], name)

    def test_verify_detects_missing_recalc(self):
        data, _, _ = S.score(fixture())
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "b.xlsx")
            BB.build(data, out)
            problems = BB.verify(data, out)
            self.assertTrue(problems and "recalc" in problems[0])


class DiffTests(unittest.TestCase):
    def test_diff(self):
        old, _, _ = S.score(fixture())
        old["baseline"] = [{"metric": "Zero-result rate (hr)", "value": 0.2, "date": "2026-07-01", "method": "x"}]
        with tempfile.TemporaryDirectory() as tmp:
            prev = os.path.join(tmp, "prev.xlsx")
            BB.build(old, prev)
            new_in = fixture()
            for f in new_in["findings"]:
                if f["id"] == "CHK-1":
                    f["status"] = "done"
                if f["id"] == "PDP-2":
                    f["status"] = "partial"
                    f.update(rigor="B", transfer=0.7, margin_base_eur=10000, effect_low=0.01, effect_high=0.02,
                             newton_days=1, client_days=1)
            new_in["findings"] = [f for f in new_in["findings"] if f["id"] != "MER-1"]
            new, _, _ = S.score(new_in)
            new["baseline"] = [{"metric": "Zero-result rate (hr)", "value": 0.12, "date": "2026-10-07", "method": "x"}]
            ps, pb = DR.read_previous(prev)
            res = DR.apply(new, ps, pb)
            f = by_id(res)
            self.assertEqual(f["CHK-1"]["change"], "improved")
            self.assertEqual(f["PDP-2"]["change"], "regressed")
            self.assertEqual(res["diff"]["removed_ids"], ["MER-1"])
            self.assertAlmostEqual(res["baseline"][0]["change"], -0.08)


class CatalogueTests(unittest.TestCase):
    def test_health(self):
        products = [
            {"id": 1, "category": "Anchors", "revenue_rank": 1,
             "texts": {"hr": {"name": "Sidro", "description": "<p>" + "riječ " * 60 + "</p>"},
                       "en": {"name": "Anchor", "description": "Short."}},
             "features": {"weight": "10 kg", "material": "galv"},
             "images": [{"alt": {"hr": "sidro"}}, {"alt": {}}, {"alt": {"hr": "x"}}],
             "gpsr": {"manufacturer": "Lalizas", "eu_responsible": "X", "identifier": "123", "warnings": "w"},
             "safety_critical": False},
            {"id": 2, "category": "Anchors", "revenue_rank": 2,
             "texts": {"hr": {"name": "Sidro 2", "description": "Kratko."}},
             "features": {"weight": "5 kg"}, "images": [], "gpsr": {}, "safety_critical": True},
        ]
        d = CH.analyse(products, ["hr", "en"], top_n=2)
        self.assertEqual(d["languages"]["hr"]["thin_description_share"], 0.5)
        self.assertEqual(d["languages"]["en"]["description_coverage"], 0.5)
        self.assertEqual(d["languages"]["en"]["thin_description_share"], 1.0)   # 1 of 1 described SKU
        self.assertEqual(d["languages"]["en"]["description_missing_share"], 0.5)
        self.assertEqual(d["categories"]["Anchors"]["expected_keys"], ["material", "weight"])
        self.assertAlmostEqual(d["categories"]["Anchors"]["completeness"], 0.75)  # (2/2 + 1/2) / 2
        self.assertEqual(d["images"]["share_top_with_3plus"], 0.5)
        self.assertAlmostEqual(d["images"]["alt_coverage_hr"], 2 / 3)
        self.assertEqual(d["gpsr"]["complete_share"], 0.5)
        self.assertEqual(d["safety_critical"]["count"], 1)
        # frozen keys keep the metric monotonic across runs
        frozen = CH.analyse(products, ["hr"], top_n=2, frozen_keys={"Anchors": ["weight"]})
        self.assertEqual(frozen["categories"]["Anchors"]["completeness"], 1.0)
        # robustness: null language text, string images
        CH.analyse([{"id": 3, "texts": {"hr": None}, "images": ["a.jpg"]}], ["hr"])
        rows = CH.baseline_rows(d, "2026-10-07")
        self.assertTrue(any(r["metric"].startswith("Attribute completeness: Anchors") for r in rows))


class PageTests(unittest.TestCase):
    def test_page(self):
        html = """<html lang="hr"><head><title>Sidro 10 kg</title>
        <link rel="canonical" href="https://shop/x"><link rel="alternate" hreflang="en" href="https://shop/en/x">
        <script type="application/ld+json">{"@context":"https://schema.org","@type":"Product","name":"Sidro",
        "brand":{"@type":"Brand","name":"Lalizas"},"gtin13":"123","offers":{"@type":"Offer","price":"49.90",
        "priceCurrency":"EUR","availability":"InStock"}}</script></head>
        <body><h1>Sidro</h1><img src=a alt="sidro"><img src=b><p>Proizvođač: Lalizas</p></body></html>"""
        r = PC.check(html, "p.html")
        self.assertEqual(r["product_markup"], "jsonld")
        self.assertTrue(r["gtin"] and r["brand"] and r["price"])
        self.assertFalse(r["shippingDetails"])
        self.assertFalse(r["hasMerchantReturnPolicy"])
        self.assertEqual(r["hreflang_count"], 1)
        self.assertFalse(r["hreflang_has_x_default"])
        self.assertEqual(r["images_missing_alt"], 1)
        self.assertTrue(r["gpsr_hints"]["manufacturer"]["found"])
        self.assertFalse(r["gpsr_hints"]["eu_responsible"]["found"])

    def test_gpsr_false_positives_and_microdata(self):
        html = """<html><body><nav><a>Proizvođači</a></nav>
        <div itemscope itemtype="https://schema.org/Product"><span itemprop="name">X</span>
        <meta itemprop="gtin13" content="1"><div itemprop="offers" itemscope itemtype="https://schema.org/Offer">
        <span itemprop="price">9</span></div></div>
        <footer>Odgovorna osoba za obradu osobnih podataka: Ivo. Sigurnosno plaćanje karticom.</footer></body></html>"""
        r = PC.check(html, "m.html")
        self.assertEqual(r["product_markup"], "microdata")
        self.assertTrue(r["gtin"] and r["price"])
        self.assertFalse(any(v["found"] for v in r["gpsr_hints"].values()))

    def test_gpsr_label_layouts(self):
        r = PC.check("<p>Odgovorna osoba u EU: Marina d.o.o.</p><dl><dt>Proizvođač</dt><dd>Lalizas</dd></dl>", "g.html")
        self.assertTrue(r["gpsr_hints"]["eu_responsible"]["found"])
        self.assertTrue(r["gpsr_hints"]["manufacturer"]["found"])


class BehaviorLaneTests(unittest.TestCase):
    def lane_errors(self, mutate):
        d = fixture()
        mutate(d)
        _, errors, warnings = S.score(d)
        return errors, warnings

    def item(self, d, bid):
        return next(b for b in d["behavior"] if b["id"] == bid)

    def test_rank_grade_then_effort_then_id(self):
        data, errors, _ = S.score(fixture())
        self.assertEqual(errors, [])
        # the defect ranks first; hypotheses follow by grade, effort, id; done items last
        self.assertEqual([b["id"] for b in data["behavior"]], ["NEWB-2", "BEH-2", "BEH-4", "PATH-1", "NEWB-1", "PATH-3"])
        self.assertEqual([b["lane_rank"] for b in data["behavior"]], [1, 2, 3, 4, 5, None])
        self.assertEqual(data["summary"]["behavior_defects"], ["NEWB-2"])
        self.assertEqual(data["summary"]["behavior_top"], ["BEH-2", "BEH-4", "PATH-1", "NEWB-1"])
        self.assertEqual(data["summary"]["behavior_counts"]["done"], 1)

    def test_lane_is_unscored_and_leaves_findings_alone(self):
        with_lane, _, _ = S.score(fixture())
        d = fixture()
        d.pop("behavior")
        without, errors, _ = S.score(d)
        self.assertEqual(errors, [])
        self.assertEqual(without["behavior"], [])
        self.assertEqual([f["id"] for f in with_lane["findings"]], [f["id"] for f in without["findings"]])
        self.assertEqual(with_lane["summary"]["report_quick_wins"], without["summary"]["report_quick_wins"])
        for b in with_lane["behavior"]:
            self.assertFalse({"impact_eur", "impact_band", "quadrant", "priority"} & set(b))

    def test_lane_only_run(self):
        d = fixture()
        d["findings"] = []
        data, errors, _ = S.score(d)
        self.assertEqual(errors, [])
        self.assertEqual(data["summary"]["report_quick_wins"], [])
        self.assertEqual(len(data["summary"]["behavior_top"]), 4)
        self.assertEqual(data["summary"]["behavior_defects"], ["NEWB-2"])
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "lane.xlsx")
            BB.build(data, out)
            self.assertEqual(BB.verify_behavior(data, BB.load_workbook(out)), [])
        _, errors, _ = S.score({"findings": [], "behavior": []})
        self.assertTrue(any("non-empty" in e for e in errors))

    def test_truth_rule(self):
        errors, _ = self.lane_errors(lambda d: self.item(d, "BEH-2").pop("truth_source"))
        self.assertTrue(any("BEH-2" in e and "truth_source" in e for e in errors))

    def test_behavior_card_rejected_from_findings(self):
        def m(d):
            d["findings"].append({"id": "BEH-1", "status": "missing", "evidence": "x", "rigor": "A", "transfer": 0.7,
                                  "margin_base_eur": 1000, "newton_days": 1, "client_days": 1})
        errors, _ = self.lane_errors(m)
        self.assertTrue(any("BEH-1" in e and "belong in 'behavior'" in e for e in errors))

    def test_ids_grades_money_and_duplicates(self):
        def m(d):
            d["behavior"].append(dict(self.item(d, "PATH-1")))            # duplicate id
            d["behavior"].append({"id": "CHK-9", "status": "missing", "evidence": "x"})   # wrong prefix
            self.item(d, "BEH-4")["margin_base_eur"] = 5000               # money in an unscored lane
            self.item(d, "NEWB-1")["grade"] = "A"                         # outside the library, no source_url
        errors, _ = self.lane_errors(m)
        self.assertTrue(any("PATH-1" in e and "duplicate" in e for e in errors))
        self.assertTrue(any("CHK-9" in e and "start with" in e for e in errors))
        self.assertTrue(any("BEH-4" in e and "margin_base_eur" in e for e in errors))
        self.assertTrue(any("NEWB-1" in e and "source_url" in e for e in errors))

    def test_defect_rules(self):
        def m(d):
            self.item(d, "NEWB-2")["grade"] = "A"                         # a defect carries no evidence grade
            self.item(d, "BEH-2")["kind"] = "bug"                         # unknown kind
        errors, _ = self.lane_errors(m)
        self.assertTrue(any("NEWB-2" in e and "no evidence grade" in e for e in errors))
        self.assertTrue(any("BEH-2" in e and "kind must be" in e for e in errors))
        errors, _ = self.lane_errors(lambda d: self.item(d, "NEWB-2").pop("measure"))
        self.assertTrue(any("NEWB-2" in e and "measure" in e for e in errors))

    def test_active_item_needs_hypothesis_and_evidence(self):
        def m(d):
            b = self.item(d, "PATH-1")
            b["hypothesis"], b["evidence"] = "", ""
        errors, _ = self.lane_errors(m)
        self.assertTrue(any("PATH-1" in e and "hypothesis" in e for e in errors))
        self.assertTrue(any("PATH-1" in e and "evidence is required" in e for e in errors))

    def test_banned_pattern_hint_is_a_warning(self):
        def m(d):
            self.item(d, "NEWB-1")["hypothesis"] = "Add a decoy option next to the kit."
        errors, warnings = self.lane_errors(m)
        self.assertEqual(errors, [])
        self.assertTrue(any("NEWB-1" in w and "decoy" in w for w in warnings))

    def test_backlog_sheets_and_verify(self):
        data, errors, _ = S.score(fixture())
        self.assertEqual(errors, [])
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "b.xlsx")
            BB.build(data, out)
            wb = BB.load_workbook(out)
            ws = wb["Behavior lane"]
            head = [c.value for c in ws[1]]
            self.assertEqual([ws.cell(r, head.index("id") + 1).value for r in range(2, ws.max_row + 1)],
                             ["NEWB-2", "BEH-2", "BEH-4", "PATH-1", "NEWB-1", "PATH-3"])
            self.assertEqual([c.value for c in wb["Path"][1]], ["metric", "client desktop", "client mobile",
                                                                "awn desktop"])
            self.assertEqual(BB.verify_behavior(data, wb), [])
            ws.cell(3, head.index("grade") + 1).value = "C"              # tampering is caught
            self.assertTrue(any("grade" in p for p in BB.verify_behavior(data, wb)))

    def test_diff_covers_the_lane(self):
        old, _, _ = S.score(fixture())
        with tempfile.TemporaryDirectory() as tmp:
            prev = os.path.join(tmp, "prev.xlsx")
            BB.build(old, prev)
            new_in = fixture()
            self.item(new_in, "PATH-1")["status"] = "done"
            new_in["behavior"] = [b for b in new_in["behavior"] if b["id"] != "NEWB-1"]
            new, errors, _ = S.score(new_in)
            self.assertEqual(errors, [])
            res = DR.apply(new, *DR.read_previous(prev))
            lane = {b["id"]: b for b in res["behavior"]}
            self.assertEqual(lane["PATH-1"]["change"], "improved")
            self.assertEqual(lane["BEH-2"]["change"], "same")
            self.assertIn("NEWB-1", res["diff"]["removed_ids"])
            self.assertIn("PATH-1", res["diff"]["improved"])


class LaneRuleTests(unittest.TestCase):
    """Rules a reviewer found untested: each one below fails if its check is removed from the scripts."""

    def hyp(self, bid, **kw):
        base = {"id": bid, "status": "missing", "title": "t", "observation": "o", "evidence": "e.png",
                "hypothesis": "If x, then y, because z.", "measure": "m", "effort": "S",
                "grade": S.BEHAVIOR_CARD_GRADES.get(bid, "C")}
        if bid in S.TRUTH_CARDS:
            base["truth_source"] = "order lines, daily"
        base.update(kw)
        return base

    def score(self, behavior, **extra):
        d = fixture()
        d["behavior"] = behavior
        d.update(extra)
        return S.score(d)

    def test_every_truth_card_needs_its_source_also_when_done(self):
        for card in sorted(S.TRUTH_CARDS):
            for status in ("missing", "partial", "done"):
                item = self.hyp(card, status=status)
                item.pop("truth_source")
                _, errors, _ = self.score([item])
                self.assertTrue(any(card in e and "truth_source" in e for e in errors), (card, status))
        item = self.hyp("BEH-1", status="n/a")
        item.pop("truth_source")
        self.assertEqual(self.score([item])[1], [])

    def test_every_money_field_is_refused(self):
        for key in ("margin_base_eur", "effect_low", "effect_high", "impact_eur"):
            _, errors, _ = self.score([self.hyp("BEH-4", **{key: 0.02})])
            self.assertTrue(any("BEH-4" in e and key in e for e in errors), key)

    def test_status_grade_effort_are_checked(self):
        for field, value, message in (("status", "open", "status must be"), ("grade", "D", "grade must be"),
                                      ("effort", "XL", "effort must be")):
            _, errors, _ = self.score([self.hyp("NEWB-7", **{field: value})])
            self.assertTrue(any("NEWB-7" in e and message in e for e in errors), field)

    def test_grade_must_equal_the_library_card(self):
        _, errors, _ = self.score([self.hyp("PATH-1", grade="A")])
        self.assertTrue(any("PATH-1" in e and "grade must be B" in e for e in errors))
        _, errors, _ = self.score([self.hyp("PATH-3", grade="C")])
        self.assertTrue(any("PATH-3" in e and "kind 'defect'" in e for e in errors))
        ok = {"id": "PATH-3", "kind": "defect", "status": "partial", "title": "t", "observation": "o",
              "evidence": "e.png", "measure": "m", "effort": "S"}
        self.assertEqual(self.score([ok])[1], [])

    def test_card_grades_match_the_library(self):
        lib = os.path.join(SCRIPTS, "..", "references", "practice-library.md")
        with open(lib, encoding="utf-8") as fh:
            rows = [l.split("|") for l in fh if l.startswith(("| PATH-", "| BEH-"))]
        grades = {r[1].replace("**T**", "").strip(): r[4].strip() for r in rows}
        self.assertEqual({k: v for k, v in grades.items() if v in ("A", "B", "C")}, S.BEHAVIOR_CARD_GRADES)
        self.assertEqual({k for k, v in grades.items() if v not in ("A", "B", "C")}, S.DEFECT_ONLY_CARDS)
        marked = {r[1].replace("**T**", "").strip() for r in rows if "**T**" in r[1]}
        self.assertEqual(marked, S.TRUTH_CARDS)

    def test_id_in_both_lists_and_evidence_on_inactive_items(self):
        _, errors, _ = self.score([self.hyp("CHK-1")])
        self.assertTrue(any("CHK-1" in e and "both 'findings' and 'behavior'" in e for e in errors))
        _, errors, _ = self.score([{"id": "NEWB-9", "status": "done", "title": "t", "observation": "o"}])
        self.assertTrue(any("NEWB-9" in e and "evidence is required" in e for e in errors))
        d = fixture()
        d["findings"].append("CHK-9")                                      # not an object: a message, not a traceback
        self.assertTrue(any("a finding is an object" in e for e in S.score(d)[1]))

    def test_top_list_holds_seven_hypotheses(self):
        lane = [self.hyp(f"NEWB-{i}") for i in range(1, 10)]
        data, errors, _ = self.score(lane)
        self.assertEqual(errors, [])
        self.assertEqual(len(data["summary"]["behavior_top"]), 7)
        self.assertEqual(data["behavior"][8]["lane_rank"], 9)

    def test_warnings_for_money_promises_and_banned_words(self):
        _, errors, warnings = self.score([self.hyp("BEH-6", hypothesis="If prices end in 9, we gain 4.000 € a year.")])
        self.assertEqual(errors, [])
        self.assertTrue(any("BEH-6" in w and "money amount" in w for w in warnings))
        _, errors, warnings = self.score([self.hyp("BEH-3", status="done", title="Countdown timer on product pages")])
        self.assertEqual(errors, [])
        self.assertTrue(any("BEH-3" in w and "countdown" in w for w in warnings))       # done items are scanned too

    def test_path_must_be_the_comparison_rows(self):
        _, errors, _ = self.score([self.hyp("NEWB-1")], path={"comparison": [], "walks": []})
        self.assertTrue(any("'path' must be a list" in e for e in errors))
        _, errors, _ = self.score([self.hyp("NEWB-1")], path=[{"metric": "x", "values": 3}])
        self.assertTrue(any("path row 1" in e for e in errors))
        data, errors, _ = self.score([self.hyp("NEWB-1")], path=None)
        self.assertEqual((errors, data["path"]), ([], []))

    def test_workbook_checks_rows_and_ranks_and_survives_odd_values(self):
        data, errors, _ = self.score([self.hyp("NEWB-1", evidence="a.png"), self.hyp("NEWB-2")])
        data["behavior"][0]["notes"] = ["a list", "of notes"]                 # a list must not crash the build
        data["path"] = None
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "b.xlsx")
            BB.build(data, out)
            wb = BB.load_workbook(out)
            self.assertEqual(BB.verify_behavior(data, wb), [])
            ws = wb["Behavior lane"]
            head = [c.value for c in ws[1]]
            self.assertEqual(ws.cell(2, head.index("notes") + 1).value, "a list; of notes")
            ws.cell(2, head.index("lane_rank") + 1).value = 5
            self.assertTrue(any("lane_rank" in p for p in BB.verify_behavior(data, wb)))
            ws.cell(2, head.index("lane_rank") + 1).value = 1
            ws.delete_rows(3)
            self.assertTrue(any("expected 2 rows" in p for p in BB.verify_behavior(data, wb)))

    def test_lane_only_rerun_keeps_the_scored_ids(self):
        old, _, _ = S.score(fixture())
        with tempfile.TemporaryDirectory() as tmp:
            prev = os.path.join(tmp, "prev.xlsx")
            BB.build(old, prev)
            lane_only = fixture()
            lane_only["findings"] = []
            lane_only["behavior"] = [b for b in lane_only["behavior"] if b["id"] != "NEWB-1"]
            new, errors, _ = S.score(lane_only)
            self.assertEqual(errors, [])
            res = DR.apply(new, *DR.read_previous(prev))
            self.assertEqual(res["diff"]["removed_ids"], ["NEWB-1"])        # not the ten scored IDs


class PathTests(unittest.TestCase):
    CART = """<html><body><header><a href="/">Logo</a><nav><a href="/hr/445-sidra">Sidra</a>
    <a href="/kosarica">Košarica</a></nav></header>
    <main><form id="voucher" action="/kosarica"><input type="hidden" name="token" value="secret">
    <input type="text" name="discount_name" placeholder="Promo kod"><button type="submit">Dodaj</button></form>
    <a class="btn btn-primary" href="/narudzba">Nastavi na blagajnu</a>
    <a class="btn" href="/hr/">Nastavi kupovinu</a><a class="btn" href="/hr/">Nastaviti s kupovinom</a>
    <a class="btn btn-primary" href="/narudzba">Završi kupovinu</a>
    <form id="customer-form"><input name="firstname" required><input name="email" type="email" required>
    <input type="checkbox" name="newsletter" checked><input type="checkbox" name="psgdpr" required>
    <input type="radio" name="id_gender" value="1"><input type="radio" name="id_gender" value="2">
    <select name="id_country"><option>HR</option></select><input name="ghost" style="display:none">
    <footer class="form-footer"><button type="submit">Nastavi</button></footer></form></main>
    <footer><a href="/content/1-dostava">Dostava</a><a href="#">Top</a><a href="mailto:a@b.hr">Mail</a></footer>
    </body></html>"""

    def walk(self, site, device, steps, **extra):
        return {"site": site, "device": device, "scenario": "known item", "steps": steps, **extra}

    def client_steps(self):
        return [
            {"stage": "find", "type": "load", "what": "home"},
            {"stage": "find", "type": "click", "what": "category", "page_load": True},
            {"stage": "product", "type": "click", "what": "product", "page_load": True},
            {"stage": "product", "type": "click", "what": "add to cart"},
            {"stage": "cart", "type": "click", "what": "to cart", "page_load": True},
            {"stage": "cart", "type": "click", "what": "to checkout", "page_load": True},
            {"stage": "checkout", "type": "click", "what": "guest tab", "screen": "personal"},
            {"stage": "checkout", "type": "fill", "fields": 4, "required": 3, "screen": "personal"},
            {"stage": "checkout", "type": "click", "what": "continue", "screen": "personal"},
            {"stage": "checkout", "type": "fill", "fields": 5, "screen": "address"},
            {"stage": "checkout", "type": "select", "what": "carrier", "screen": "delivery"},
        ]

    def comp_steps(self, extra_clicks=0):
        steps = self.client_steps()[:2] + [{"stage": "product", "type": "click", "what": "add to cart"}]
        steps += [{"stage": "cart", "type": "click", "what": f"extra {i}"} for i in range(extra_clicks)]
        return steps + [{"stage": "cart", "type": "click", "what": "checkout", "page_load": True}]

    def client_screens(self):
        cart = {"viewport": [1280, 900], "links_total": 9, "exit_links_total": 3, "exit_links": {"main": 1},
                "primary_candidates": 1, "primary_in_first_screen": 1, "primary_covered": 1,
                "primary_buttons": [{"text": "Na blagajnu", "first_screen": True, "covered": True}],
                "fields": {"typed": 0}, "pre_ticked": [], "buttons": [{"text": "Na blagajnu", "region": "main"}]}
        return [
            {"name": "cart page", "stage": "cart", "kind": "cart", "counts": json.dumps(cart)},   # the raw JS string
            {"name": "cart drawer", "stage": "cart", "kind": "cart drawer", "counts": {"exit_links_total": 50, "fields": {}}},
            {"name": "checkout 1", "stage": "checkout", "kind": "guest form", "counts": {
                "links_total": 3, "exit_links_total": 1, "primary_candidates": 1, "primary_in_first_screen": 0,
                "primary_covered": 0, "pre_ticked": ["newsletter"],
                "fields": {"typed": 7, "typed_required": 3, "typed_optional": 4, "checkboxes": 3,
                           "selects_without_default": 0}}}]

    def run_walks(self, walks, with_page=True):
        with tempfile.TemporaryDirectory() as tmp:
            pages = None
            if with_page:
                pages = os.path.join(tmp, "pages")
                os.mkdir(pages)
                with open(os.path.join(pages, "cart.html"), "w", encoding="utf-8") as fh:
                    fh.write(self.CART)
            files = []
            for name, w in walks:
                files.append(os.path.join(tmp, name))
                with open(files[-1], "w", encoding="utf-8") as fh:
                    fh.write(w if isinstance(w, str) else json.dumps(w))
            return PM.run(files, pages, "2026-10-08")

    def test_page_counts(self):
        r = PM.count_page(self.CART, "cart.html")
        self.assertEqual(r["links_by_region"], {"header": 1, "nav": 2, "footer": 3, "main": 4})
        self.assertEqual(r["exit_links_total"], 5)          # logo, category, 2 x continue shopping, delivery page
        self.assertEqual(r["exit_links_by_region"]["footer"], 1)
        self.assertEqual((r["fields_typed"], r["fields_required"], r["checkboxes"], r["radio_groups"]), (4, 2, 2, 1))
        self.assertEqual(r["pre_ticked_checkboxes"], [{"name": "newsletter", "form": "customer-form"}])
        self.assertTrue(r["promo_code_field"])
        primary = [b["text"] for b in r["buttons"] if b["primary_candidate"]]
        # "Nastavi kupovinu" / "Nastaviti s kupovinom" lead away; "Završi kupovinu" finishes the purchase
        self.assertEqual(primary, ["Nastavi na blagajnu", "Završi kupovinu", "Nastavi"])
        self.assertEqual(r["primary_candidates_main"], 3)                  # a <footer> inside the form is not the site footer
        self.assertNotIn("secret", json.dumps(r))                         # names only, never values
        self.assertNotIn("ghost", json.dumps(r))

    def test_walk_counts_and_gap(self):
        gate = [{"name": "first form", "stage": "checkout", "kind": "login or guest gate",
                 "counts": {"exit_links_total": 82, "primary_in_first_screen": 1,
                            "fields": {"typed": 5, "typed_required": 4}}}]
        res, errors, warnings = self.run_walks([
            ("c.json", self.walk("client", "desktop", self.client_steps(), complete=True,
                                 pages={"cart.html": "cart"}, screens=self.client_screens())),
            ("a.json", self.walk("awn", "desktop", self.comp_steps(), reached_first_form=True)),
            ("s.json", self.walk("svb24", "desktop", self.comp_steps(extra_clicks=2), reached_first_form=True,
                                 screens=gate))])
        self.assertEqual((errors, warnings), ([], []))
        client = next(w for w in res["walks"] if w["is_client"])
        self.assertEqual(client["to_first_checkout_form"], {"clicks": 6, "selects": 0, "fields_typed": 0,
                                                            "interactions": 6, "page_loads": 5})
        self.assertEqual(client["total"]["interactions"], 7 + 1 + 9)
        self.assertEqual((client["checkout_fields_typed"], client["checkout_fields_required"],
                          client["checkout_screens"]), (9, 8, 3))
        # the gap is against the BEST competitor (fewest interactions), not the first or the worst
        self.assertEqual(res["gaps_to_first_checkout_form"],
                         [{"device": "desktop", "client": 6, "best_competitor": "awn", "best_competitor_value": 3,
                           "gap": 3}])
        rows = {r["metric"]: r["values"] for r in res["comparison"]}
        self.assertEqual(rows["Interactions to first checkout form"],
                         {"client desktop": 6, "awn desktop": 3, "svb24 desktop": 5})
        self.assertEqual(rows["Checkout fields typed (complete walks only)"], {"client desktop": 9})
        base = {r["metric"]: r["value"] for r in res["baseline_rows"]}
        self.assertEqual(base["Path: interactions to first checkout form (desktop)"], 6)
        self.assertEqual(base["Path: visible exit links, cart page (desktop)"], 3)       # rendered, not markup
        self.assertEqual(base["Path: visible typed fields, checkout 1 (desktop)"], 7)
        self.assertFalse(any("cart.html" in m for m in base))                            # markup feeds no baseline
        # the FIRST screen listed for a stage is the one compared: the cart page (3), not the drawer (50)
        self.assertEqual(rows["Visible exit links, cart screen"], {"client desktop": 3})
        # a login gate is not compared with a guest form: svb24 is left out and named
        self.assertEqual(rows["Visible exit links, first checkout screen"], {"client desktop": 1})
        self.assertEqual(rows["Visible required typed fields, first checkout screen"], {"client desktop": 3})
        self.assertEqual(res["not_like_for_like"], [{"walk": "svb24 desktop", "stage": "checkout",
                                                     "screen": "first form", "kind": "login or guest gate",
                                                     "client_kind": "guest form"}])
        self.assertEqual(res["markup_pages"][0]["exit_links_total"], 5)
        self.assertEqual({f["source"] for f in res["pre_ticked_flags"]}, {"markup", "rendered page"})
        self.assertEqual(res["covered_primary_flags"], [{"walk": "client desktop", "screen": "cart page",
                                                         "primary_covered": 1, "buttons": ["Na blagajnu"]}])

    def test_same_kind_screens_are_compared(self):
        form = [{"name": "checkout 1", "stage": "checkout", "kind": "guest form",
                 "counts": {"exit_links_total": 40, "fields": {"typed": 4}}}]
        res, errors, _ = self.run_walks([
            ("c.json", self.walk("client", "desktop", self.client_steps(), complete=True, screens=self.client_screens())),
            ("a.json", self.walk("awn", "desktop", self.comp_steps(), reached_first_form=True, screens=form))], False)
        self.assertEqual(errors, [])
        rows = {r["metric"]: r["values"] for r in res["comparison"]}
        self.assertEqual(rows["Visible exit links, first checkout screen"], {"client desktop": 1, "awn desktop": 40})
        self.assertEqual(res["not_like_for_like"], [])

    def test_walk_that_never_reached_the_form_has_no_path_length(self):
        blocked = self.walk("client", "mobile", self.client_steps()[:3], stopped_reason="add to cart failed")
        res, errors, _ = self.run_walks([
            ("c.json", self.walk("client", "desktop", self.client_steps(), complete=True)),
            ("m.json", blocked),
            ("a.json", self.walk("awn", "mobile", self.comp_steps(), reached_first_form=True))], False)
        self.assertEqual(errors, [])
        rows = {r["metric"]: r["values"] for r in res["comparison"]}
        self.assertNotIn("client mobile", rows["Interactions to first checkout form"])
        self.assertFalse(any("(mobile)" in r["metric"] for r in res["baseline_rows"]))
        self.assertEqual(res["gaps_to_first_checkout_form"], [])       # no reached client walk on mobile, no gap

    def test_kind_is_matched_per_device(self):
        gate = [{"name": "first form", "stage": "checkout", "kind": "login or guest gate",
                 "counts": {"exit_links_total": 80, "fields": {"typed": 1}}}]
        form = [{"name": "checkout 1", "stage": "checkout", "kind": "guest form",
                 "counts": {"exit_links_total": 2, "fields": {"typed": 6}}}]
        res, errors, _ = self.run_walks([
            ("cd.json", self.walk("client", "desktop", self.comp_steps(), reached_first_form=True, screens=form)),
            ("cm.json", self.walk("client", "mobile", self.comp_steps(), reached_first_form=True, screens=gate)),
            ("ad.json", self.walk("awn", "desktop", self.comp_steps(), reached_first_form=True, screens=gate)),
            ("am.json", self.walk("awn", "mobile", self.comp_steps(), reached_first_form=True, screens=gate))], False)
        self.assertEqual(errors, [])
        rows = {r["metric"]: r["values"] for r in res["comparison"]}
        self.assertEqual(rows["Visible exit links, first checkout screen"],
                         {"client desktop": 2, "client mobile": 80, "awn mobile": 80})     # awn desktop: a gate vs a form
        self.assertEqual([n["walk"] for n in res["not_like_for_like"]], ["awn desktop"])

    def test_walk_validation(self):
        bad = self.walk("client", "desktop", [{"stage": "cart", "type": "click"},
                                              {"stage": "find", "type": "tap"},
                                              {"stage": "checkout", "type": "fill"}])
        m, errors, _ = PM.walk_metrics(bad, "bad.json")
        self.assertIsNone(m)
        self.assertTrue(any("type must be" in e for e in errors))
        self.assertTrue(any("fill step needs" in e for e in errors))
        self.assertTrue(any("stages must run in order" in e for e in errors))
        ok = self.client_steps()
        cases = {
            "a walk log is one JSON object": [ok],
            "a step is an object": self.walk("client", "desktop", ["click"]),
            "'screens' must be a list": self.walk("client", "desktop", ok, screens={"a": 1}),
            "a screen is an object": self.walk("client", "desktop", ok, screens=["cart"]),
            "'counts' must be": self.walk("client", "desktop", ok, screens=[{"name": "cart page", "stage": "cart",
                                                                              "counts": "not json"}]),
            "'pages' must be an object": self.walk("client", "desktop", ok, pages=["cart.html"]),
            "'complete' is true but no checkout field": self.walk("client", "desktop", ok[:6], complete=True),
            "'required' must be a whole number": self.walk("client", "desktop", [
                {"stage": "checkout", "type": "fill", "fields": 2, "required": "two"}]),
        }
        for message, walk in cases.items():
            m, errors, _ = PM.walk_metrics(walk, "w.json")
            self.assertIsNone(m, message)
            self.assertTrue(any(message in e for e in errors), (message, errors))
        m, errors, _ = PM.walk_metrics(self.walk("client", "desktop", [
            {"stage": "checkout", "type": "fill", "fields": 2, "required": None}]), "w.json")
        self.assertEqual((errors, m["checkout_fields_required"]), ([], 2))      # required: null means "all of them"

    def test_run_errors_are_messages_not_tracebacks(self):
        res, errors, _ = self.run_walks([("broken.json", "{not json")], False)
        self.assertIsNone(res)
        self.assertTrue(any("cannot read walk log" in e for e in errors))
        res, errors, _ = self.run_walks([("m.json", self.walk("marinastores.hr", "desktop", self.comp_steps(),
                                                              reached_first_form=True))], False)
        self.assertTrue(any('"site": "client"' in e for e in errors))
        res, errors, _ = self.run_walks([("a.json", self.walk("client", "desktop", self.comp_steps())),
                                         ("b.json", self.walk("client", "desktop", self.comp_steps()))], False)
        self.assertTrue(any("share the label" in e for e in errors))

    def test_screen_name_vocabulary_warning(self):
        w = self.walk("client", "desktop", self.comp_steps(), reached_first_form=True, screens=[
            {"name": "the basket", "stage": "cart", "kind": "cart", "counts": {}},
            {"name": "cart drawer, cookie banner unanswered", "stage": "cart", "kind": "cart drawer", "counts": {}},
            {"name": "checkout 1", "stage": "checkout", "counts": {}},
            {"name": "checkout 2", "stage": "checkout", "kind": "a form", "counts": {}}])
        m, errors, warnings = PM.walk_metrics(w, "w.json")
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 3)
        self.assertIn("the basket", warnings[0])                 # a name outside the vocabulary
        self.assertIn("no 'kind'", warnings[1])                  # compared with anything unless a kind is given
        self.assertIn("'a form' is not one of", warnings[2])


class WordListTests(unittest.TestCase):
    """One word list decides what a 'primary' button is, in Python and in the browser script."""

    def setUp(self):
        with open(os.path.join(SCRIPTS, "path_words.json"), encoding="utf-8") as fh:
            self.words = {k: v for k, v in json.load(fh).items() if not k.startswith("_")}
        with open(os.path.join(HERE, "button_texts.json"), encoding="utf-8") as fh:
            self.texts = json.load(fh)
        with open(os.path.join(SCRIPTS, "visible_counts.js"), encoding="utf-8") as fh:
            self.js = fh.read()

    def js_words(self):
        block = self.js.split("/*WORDS*/")[1].split("/*END WORDS*/")[0]
        return json.loads(block[block.index("{"): block.rindex("}") + 1])

    def test_js_copy_equals_json(self):
        self.assertEqual(self.js_words(), self.words)

    def test_python_classification(self):
        self.assertEqual([t for t in self.texts["primary"] if not PM.is_primary(t)], [])
        self.assertEqual([t for t in self.texts["not_primary"] if PM.is_primary(t)], [])
        self.assertGreater(len(self.texts["primary"]), 40)
        self.assertGreater(len(self.texts["not_primary"]), 25)

    def test_javascript_classification(self):
        import shutil
        node = shutil.which("node")
        if not node:
            self.skipTest("node not available")
        program = ("const W=%s;const RX=Object.fromEntries(Object.entries(W).map(([k,v])=>[k,new RegExp(v,'i')]));"
                   "const p=t=>RX.primary.test(t)&&!RX.not_primary.test(t)&&!(RX.login.test(t)&&!RX.guest.test(t));"
                   "const T=%s;console.log(JSON.stringify({miss:T.primary.filter(t=>!p(t)),"
                   "wrong:T.not_primary.filter(t=>p(t))}))") % (json.dumps(self.js_words()), json.dumps(self.texts))
        out = subprocess.run([node, "-e", program], capture_output=True, text=True)
        self.assertEqual(json.loads(out.stdout), {"miss": [], "wrong": []}, out.stderr)


class VisibleCountsTests(unittest.TestCase):
    """Runs visible_counts.js in a real page. Skipped where no browser is installed."""
    PAGE = """<html style="height:100%%;scroll-behavior:smooth"><body style="margin:0;height:100%%;overflow-x:hidden">
    <header><a href="/">Logo</a><form role="search"><input name="s" type="text"></form>
      <nav style="max-height:0;overflow:hidden"><a href="/a">A</a><a href="/b">B</a><a href="/c">C</a></nav>
      <a class="sr" href="#main" style="position:absolute;width:1px;height:1px;overflow:hidden">Skip</a></header>
    <main id="main" style="height:1400px">
      <form id="customer-form">
        <input name="firstname" required><input name="company"><input type="search" name="q">
        <input name="addr" placeholder="Search for your address">
        <label><input type="checkbox" name="newsletter" checked style="opacity:0;position:absolute">Newsletter</label>
        <label><input type="radio" name="gift" value="1" checked>Gift wrap</label>
        <select name="id_country"><option value="">Odaberite</option><option value="1">HR</option></select>
        <footer><a class="cta" href="/narudzba">Nastavi na blagajnu</a>
          <a class="btn" href="/hr/">Nastavi kupovinu</a>
          <div role="button" aria-label="Sign in and proceed to checkout" style="width:120px;height:20px"></div></footer>
      </form>
      <a class="btn" href="/narudzba" style="position:absolute;top:1200px">Završi kupovinu</a>
      <div role="button" style="position:absolute;top:1300px"><button>Zur Kasse</button></div>
      <div style="width:0;overflow:hidden"><a href="/side">Side menu</a></div>
      <div style="position:fixed;top:0;left:0;transform:translateY(-300%%)"><a class="btn" href="/narudzba">Checkout</a>
        <a href="/parked">Parked</a></div>
    </main>
    <footer><a href="/content/1">Dostava</a><input name="newsletter_email"></footer>
    <div id="banner" style="position:fixed;left:0;right:0;top:0;height:70%%;background:#fff">%s</div>
    </body></html>"""

    BODY = """<div style="height:20px;overflow:hidden"><div style="position:fixed;right:0;top:100px;width:200px">
        <a class="btn" href="/narudzba">Na blagajnu</a></div></div>
      <div style="height:20px;overflow:hidden"><a class="btn" href="/narudzba" style="position:fixed;right:0;top:300px">Kupi</a></div>
      <div style="position:fixed;left:-300px;top:0;width:250px"><a href="/offcanvas">Off canvas</a></div>
      <a href="/a">A</a><div style="height:1500px"></div>
      <a href="/b">B</a><input name="x"><input name="y"><a class="btn" href="/narudzba">Nastavi</a>"""
    SCROLLERS = {
        "body is the scroller": '<html style="height:100%%;overflow:hidden"><body style="margin:0;height:100%%;'
                                'overflow:auto">%s</body></html>',
        "app shell": '<html><body style="margin:0;height:100%%;overflow:hidden"><div style="height:100vh;'
                     'overflow-y:auto">%s</div></body></html>',
        "plain page": '<html><body style="margin:0">%s</body></html>',
    }

    def test_scrolling_containers_do_not_hide_what_is_below_the_fold(self):
        for name, shell in self.SCROLLERS.items():
            c = json.loads(self.counts(html=shell % self.BODY))
            # count: the drawer link (inside a fixed box inside a clipping parent), the fixed button whose own parent
            # clips, A, B and Nastavi. Do not count: the off-canvas link.
            self.assertEqual(c["links_total"], 5, name)
            self.assertEqual(c["fields"]["typed"], 2, name)
            self.assertEqual(sorted(b["text"] for b in c["primary_buttons"]), ["Kupi", "Na blagajnu", "Nastavi"], name)
            self.assertEqual(c["primary_in_first_screen"], 2, name)
            self.assertEqual(c["primary_covered"], 0, name)

    # name: (page, visible links, primary button texts)
    WINDOWS = {
        "tall modal that scrolls (the added-to-cart window on a phone)": (
            '<div style="position:fixed;top:0;left:0;right:0;bottom:0;overflow-y:auto"><div style="height:900px">Dodano</div>'
            '<a class="btn" href="/narudzba">Dovrši kupnju</a> <a class="btn" href="/">Nastavi kupovinu</a></div>',
            2, ["Dovrši kupnju"]),
        "cart drawer with a list that scrolls": (
            '<div style="position:fixed;top:0;right:0;width:300px;height:100vh"><div style="height:300px;overflow-y:auto">'
            '<div style="height:800px"></div><a href="/sidro">Sidro</a></div>'
            '<a class="btn" href="/narudzba">Na blagajnu</a></div>',
            2, ["Na blagajnu"]),
        "collapsed wrapper around a list that scrolls": (
            '<div style="max-height:0;overflow:hidden"><div style="height:100px;overflow-y:auto"><a href="/1">1</a>'
            '<div style="height:500px"></div><a href="/2">2</a></div></div>',
            0, []),
        "menu collapsed with overflow auto": (
            '<div style="height:50px"></div><div style="max-height:0;overflow:auto"><a href="/m1">M1</a><br>'
            '<a href="/m2">M2</a></div>',
            0, []),
        "swipe carousel inside a wrapper that clips sideways": (
            '<div style="width:300px;overflow-x:hidden"><div style="width:300px;overflow-x:auto;white-space:nowrap">'
            '<a style="display:inline-block;width:320px" href="/c1">C1</a>'
            '<a style="display:inline-block;width:320px" href="/c2">C2</a></div></div>',
            2, []),
        "overflow auto with room to spare shields nothing": (
            '<div style="height:100px;overflow:hidden"><div style="height:200px;overflow:auto">'
            '<div style="height:150px"></div><a href="/f">F</a></div></div>',
            0, []),
        "sideways overflow auto with room to spare shields nothing": (
            '<div style="width:100px;overflow-x:hidden"><div style="width:400px;overflow-x:auto">'
            '<a style="display:inline-block;margin-left:200px" href="/g">G</a></div></div>',
            0, []),
        "side menu collapsed to no width with overflow auto": (
            '<div style="width:0;overflow-x:auto;white-space:nowrap"><a href="/h">H link</a></div>',
            0, []),
        "fixed window parked below the screen": (
            '<div style="position:fixed;top:700px;left:0;width:300px;height:300px">'
            '<a class="btn" href="/narudzba">Kupi</a></div>',
            0, []),
        "fixed window that scrolls, parked above the screen": (
            '<div style="position:fixed;top:-400px;left:0;width:300px;height:300px;overflow-y:auto">'
            '<div style="height:800px"></div><a class="btn" href="/narudzba">Kupi</a></div>',
            0, []),
    }

    def test_windows_that_scroll_and_parents_that_collapse(self):
        for name, (body, links, primary) in self.WINDOWS.items():
            c = json.loads(self.counts(html='<html><body style="margin:0">%s</body></html>' % body))
            self.assertEqual(c["links_total"], links, name)
            self.assertEqual([b["text"] for b in c["primary_buttons"]], primary, name)

    def test_closed_details_boxless_parents_and_parked_links(self):
        page = ('<html><body style="margin:0"><a href="/skip" style="position:absolute;top:-100px">Skip to content</a>'
                '<details><summary>Imate kupon?</summary><a href="/x">X</a><input name="kupon"><button>Nastavi</button>'
                '</details><details open><summary>Dostava</summary><a href="/y">Y</a></details>'
                '<div style="content-visibility:hidden"><a href="/z">Z</a></div>'
                '<div style="display:contents;overflow:hidden"><a href="/k1">K1</a> <a href="/k2">K2</a></div>'
                '<input name="ime"><button>Kupi</button><div style="height:1500px"></div>'
                '<div style="content-visibility:auto"><a href="/low">Low</a></div></body></html>')
        c = json.loads(self.counts(html=page))
        self.assertEqual(c["links_total"], 4)                  # Y, K1, K2, Low; not Skip, X or Z
        self.assertEqual(c["fields"]["typed"], 1)              # not the coupon field in the closed <details>
        self.assertEqual([b["text"] for b in c["primary_buttons"]], ["Kupi"])

    def counts(self, banner="", html=None, scroll=None, twice=False):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.skipTest("playwright not installed")
        with open(os.path.join(SCRIPTS, "visible_counts.js"), encoding="utf-8") as fh:
            script = fh.read()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 800, "height": 600})
                page.set_content(html or self.PAGE % banner)
                if html is None:
                    if banner == "none":
                        page.evaluate("document.getElementById('banner').remove()")
                    # the page is scrolled down and scrolls smoothly: the script must jump back to the top itself
                    page.evaluate("scrollTo({top: 300, behavior: 'instant'})")
                    assert page.evaluate("scrollY") == 300
                if scroll:
                    page.evaluate("scrollTo({top: %d, behavior: 'instant'})" % scroll)
                    page.wait_for_timeout(300)                 # let the page react to that scroll
                raw = page.evaluate(script)
                if twice:
                    page.wait_for_timeout(300)                 # now the page reacts to the script's jump to the top
                    raw = (raw, page.evaluate(script))
                browser.close()
        except Exception as e:                                 # no browser binary on this machine
            self.skipTest(f"browser not available: {str(e)[:80]}")
        for one in (raw if twice else (raw,)):
            self.assertIsInstance(one, str)
        return raw

    def test_a_scrolled_page_is_flagged_and_the_second_run_is_right(self):
        page = ('<html><body style="margin:0"><header id="h"><a href="/a">A</a> <a href="/b">B</a></header>'
                '<div style="height:3000px"></div>'
                '<div id="bar" style="display:none;position:fixed;bottom:0;left:0"><button>Dodaj u košaricu</button></div>'
                '<script>addEventListener("scroll", () => {'
                'document.getElementById("h").style.display = scrollY > 100 ? "none" : "";'
                'document.getElementById("bar").style.display = scrollY > 400 ? "" : "none"; });</script></body></html>')
        first, second = (json.loads(r) for r in self.counts(html=page, scroll=1200, twice=True))
        self.assertGreater(first["scrolled_from"], 1000)        # about 1200: the hidden header shifts the page a little
        self.assertEqual(second["scrolled_from"], 0)
        self.assertEqual(second["links"]["header"], 2)          # the header is back
        self.assertEqual(second["primary_candidates"], 0)       # the buy bar is gone at the top of the page
        walk = {"site": "client", "device": "mobile", "steps": [{"stage": "product", "type": "click"}],
                "screens": [{"name": "product page", "stage": "product", "kind": "product page", "counts": first}]}
        _, errors, warnings = PM.walk_metrics(walk, "w.json")
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("scrolled", warnings[0])
        walk["screens"][0]["counts"] = second
        self.assertEqual(PM.walk_metrics(walk, "w.json")[1:], ([], []))

    def test_counts_only_what_is_visible(self):
        c = json.loads(self.counts("none"))
        self.assertEqual(c["links"]["nav"], 0)                 # menu collapsed by max-height:0 does not count
        self.assertEqual(c["links"]["header"], 1)              # logo; the 1 px skip link does not count
        self.assertEqual(c["exit_links_total"], 3)             # logo, continue shopping, footer delivery link
        self.assertEqual(c["links"]["footer"], 1)              # below the fold of a body with overflow-x:hidden: still counts
        # firstname, company and the address-lookup field (its placeholder says "Search"); both real search boxes
        # and the footer field are left out
        self.assertEqual(c["fields"]["typed"], 3)
        self.assertEqual((c["fields"]["typed_required"], c["fields"]["typed_optional"]), (1, 2))
        self.assertEqual(c["pre_ticked"], ["newsletter"])      # styled checkbox (opacity 0) judged by its label
        self.assertEqual(c["pre_selected_radios"], ["gift"])
        self.assertEqual(c["fields"]["selects_without_default"], 1)
        # a.cta counts; the sized role=button with an aria-label is read and vetoed as a login; a wrapper around a
        # button counts once; the fixed panel parked above the screen and the zero-width side menu do not count
        self.assertEqual(sorted(b["text"] for b in c["primary_buttons"]),
                         ["Nastavi na blagajnu", "Završi kupovinu", "Zur Kasse"])
        self.assertIn("Sign in and proceed to checkout", [b["text"] for b in c["buttons"]])
        prim = {b["text"]: b for b in c["primary_buttons"]}
        self.assertTrue(prim["Nastavi na blagajnu"]["first_screen"])
        self.assertFalse(prim["Nastavi na blagajnu"]["covered"])
        self.assertFalse(prim["Završi kupovinu"]["first_screen"])
        self.assertIsNone(prim["Završi kupovinu"]["covered"])  # below the first screen: not "covered"
        self.assertEqual(c["primary_in_first_screen"], 1)

    def test_banner_covers_the_button_and_result_feeds_path_metrics(self):
        raw = self.counts("<button>Odbaci sve</button>")
        c = json.loads(raw)
        self.assertEqual(c["primary_covered"], 1)
        walk = {"site": "client", "device": "desktop", "reached_first_form": True,
                "steps": [{"stage": "cart", "type": "click"}],
                "screens": [{"name": "checkout 1, cookie banner unanswered", "stage": "checkout", "kind": "guest form",
                             "counts": raw}]}
        m, errors, warnings = PM.walk_metrics(walk, "w.json")
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)                     # the test page was scrolled to 300 before the run
        self.assertIn("scrolled", warnings[0])
        self.assertEqual(m["screens"][0]["primary_covered"], 1)
        self.assertEqual(m["screens"][0]["typed_fields"], 3)


class KappaTests(unittest.TestCase):
    def test_kappa(self):
        self.assertEqual(KP.quadratic_kappa([0, 1, 2, 3], [0, 1, 2, 3]), 1.0)
        self.assertAlmostEqual(KP.quadratic_kappa([0, 0, 3, 3], [3, 3, 0, 0]), -1.0)
        self.assertEqual([KP.to_int(x) for x in ["Exact", "s", "2", "I"]], [3, 2, 2, 0])


if __name__ == "__main__":
    unittest.main()
