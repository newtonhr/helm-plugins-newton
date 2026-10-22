#!/usr/bin/env python3
"""Agreement between the LLM search-relevance judge and human (staff) labels.

Usage:
    python3 kappa.py labels.csv [--lang hr]

CSV columns: query, product, llm_label, human_label[, lang]
Labels: E (Exact), S (Substitute), C (Complement), I (Irrelevant), or 3/2/1/0.
Reports quadratic-weighted kappa, plain agreement, and a verdict:
kappa >= 0.7 -> "reliable"; below -> "directional only".
"""
import argparse
import csv
import json

MAP = {"E": 3, "S": 2, "C": 1, "I": 0, "3": 3, "2": 2, "1": 1, "0": 0}
K = 4


def to_int(x):
    s = str(x).strip().upper()
    v = MAP.get(s, MAP.get(s[:1]))
    if v is None:
        raise ValueError(f"unknown label {x!r}")
    return v


def quadratic_kappa(a, b):
    n = len(a)
    if n == 0:
        raise ValueError("no labels")
    obs = [[0] * K for _ in range(K)]
    for x, y in zip(a, b):
        obs[x][y] += 1
    ha = [sum(obs[i]) for i in range(K)]
    hb = [sum(obs[i][j] for i in range(K)) for j in range(K)]
    num = den = 0.0
    for i in range(K):
        for j in range(K):
            w = (i - j) ** 2 / (K - 1) ** 2
            num += w * obs[i][j]
            den += w * ha[i] * hb[j] / n
    return 1.0 if den == 0 else 1 - num / den


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--lang")
    a = ap.parse_args()
    llm, human = [], []
    with open(a.csv, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if a.lang and row.get("lang") and row["lang"] != a.lang:
                continue
            llm.append(to_int(row["llm_label"]))
            human.append(to_int(row["human_label"]))
    k = quadratic_kappa(llm, human)
    out = {"n": len(llm), "quadratic_kappa": round(k, 4),
           "agreement": round(sum(x == y for x, y in zip(llm, human)) / len(llm), 4),
           "verdict": "reliable" if k >= 0.7 else "directional only"}
    if len(llm) < 50:
        out["note"] = "fewer than 50 labels: treat kappa as rough"
    print(json.dumps(out))


if __name__ == "__main__":
    main()
