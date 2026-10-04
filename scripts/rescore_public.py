"""Recompute the headline numbers from results/public/answers.csv alone:
no dataset, no model calls, standard library only.

  python3 scripts/rescore_public.py

Prints per-level averages for every view (moments as the unit, no-answer
runs excluded) and the planted-misreport catch / false-alarm counts.
Compare with docs/WRITEUP.md and results/summary_*.md.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

PATH = Path(__file__).resolve().parent.parent / "results" / "public" / "answers.csv"


def parse(v):
    """Lists, booleans and null are stored as JSON; plain answers as text."""
    try:
        return json.loads(v)
    except (json.JSONDecodeError, TypeError):
        return v


def main():
    rows = list(csv.DictReader(open(PATH)))
    # (set, model, condition) -> moment -> level -> [scores]
    agg = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    rule = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    seen_rule = set()
    for r in rows:
        key = (r["set"], r["model"].split("/")[-1], r["condition"])
        if r["answered"] == "True":
            agg[key][r["moment_id"]][r["level"]].append(float(r["score"]))
        rk = (r["set"], r["moment_id"], r["question"])
        if rk not in seen_rule and not r["set"].startswith("v2plant"):
            seen_rule.add(rk)
            rule[(r["set"], "rule", "nothing-changes")][r["moment_id"]][r["level"]].append(float(r["rule_score"]))

    def level_means(moments):
        out = {}
        for lv in ("L1", "L2", "L3"):
            xs = [mean(m[lv]) for m in moments.values() if m.get(lv)]
            out[lv] = mean(xs) if xs else None
        return out

    print(f"{'set':6s} {'analyst':22s} {'view':26s} {'n':>3s}  L1    L2    L3")
    for key in sorted(list(rule) + list(agg)):
        if key[0].startswith("v2plant"):
            continue
        moments = (rule if key in rule else agg)[key]
        lv = level_means(moments)
        print(f"{key[0]:6s} {key[1]:22s} {key[2]:26s} {len(moments):3d}  " +
              "  ".join("  -  " if lv[l] is None else f"{lv[l]:.2f}" for l in ("L1", "L2", "L3")))

    print("\nplanted misreports (set v2plant3, clean design): caught / false alarms")
    t = defaultdict(lambda: [0, 0, 0, 0])   # caught, planted, false alarms, controls
    for r in rows:
        if r["set"] != "v2plant3" or r["answered"] != "True":
            continue
        truth, ans = parse(r["true_answer"]), parse(r["answer"])
        k = (r["model"].split("/")[-1], r["condition"])
        if truth == ["none"]:
            t[k][3] += 1
            t[k][2] += ans != "none"
        else:
            t[k][1] += 1
            t[k][0] += ans in truth
    for k, (c, p, fa, n) in sorted(t.items()):
        print(f"  {k[0]:22s} {k[1]:26s} caught {c}/{p}   false alarms {fa}/{n}")


if __name__ == "__main__":
    main()
