"""Score analyst runs (and the persistence heuristic) against ground truth.

Output is aggregate only (mean score per level and per query, with counts),
so results/summary_*.md can be committed without shipping dataset content.
"""
import json
from collections import defaultdict
from statistics import mean

from .config import RESULTS
from .queries import score

LEVELS = ("L1", "L2", "L3")


def load_set(name):
    with open(RESULTS / f"freezes_{name}.jsonl") as f:
        return [json.loads(line) for line in f]


def load_runs(name):
    runs = []
    for p in sorted((RESULTS / "runs" / name).glob("*/*/*.json")):   # model/condition/freeze
        runs.append(json.loads(p.read_text()))
    return runs


def _ci(xs):
    """Mean and a rough 95% half-width (normal approx; freezes are the unit)."""
    if len(xs) < 2:
        return mean(xs), 0.0
    m = mean(xs)
    sd = (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5
    return m, 1.96 * sd / len(xs) ** 0.5


def table(name):
    items = {it["id"]: it for it in load_set(name)}
    # rows: label -> freeze -> query id -> score
    rows = defaultdict(lambda: defaultdict(dict))
    costs = defaultdict(list)
    missing = defaultdict(int)     # runs that returned no answers at all
    for it in items.values():
        for q in it["queries"]:
            rows["heuristic (persistence)"][it["id"]][q["id"]] = score(q, q["heuristic"])
    for r in load_runs(name):
        label = f"{r['model']} · {r['condition']}"
        it = items.get(r["freeze"])
        if not it:
            continue
        costs[label].append(r["cost_usd"])
        if r["answers"] is None:
            # refused or broken: not a measurement of SA, so excluded from the
            # means (and from paired comparisons) but counted in `no-answer`
            missing[label] += 1
            continue
        for q in it["queries"]:
            rows[label][it["id"]][q["id"]] = score(q, r["answers"].get(q["id"]))
    qmeta = {}
    for it in items.values():
        for q in it["queries"]:
            qmeta.setdefault(q["id"], q["level"])
    return items, rows, costs, qmeta, missing


def per_level(freeze_scores, qmeta):
    """Per-freeze level means first, then across freezes (freeze = unit)."""
    out = {}
    for lv in LEVELS:
        per_freeze = [mean(v for k, v in qs.items() if qmeta[k] == lv)
                      for qs in freeze_scores.values()
                      if any(qmeta[k] == lv for k in qs)]
        out[lv] = _ci(per_freeze) if per_freeze else (None, None)
    allq = [mean(qs.values()) for qs in freeze_scores.values() if qs]
    out["all"] = _ci(allq) if allq else (None, None)
    return out


def report(name):
    items, rows, costs, qmeta, missing = table(name)
    lines = [f"# SAGAT results — freeze set `{name}` ({len(items)} freezes)", "",
             "Mean score (0-1) per SA level, freezes as the unit, ± ~95% CI. "
             "L1 perception, L2 comprehension, L3 projection.", "",
             "Runs that returned no answers (harness failure or a provider content filter) "
             "are excluded from the means and counted in `no-answer`; `n` is the number of "
             "freezes actually scored. Questions skipped inside a submitted run score 0.",
             "",
             "| analyst · condition | n | no-answer | L1 | L2 | L3 | all | mean $/freeze |",
             "|---|---|---|---|---|---|---|---|"]
    def fmt(mc):
        m, h = mc
        return "–" if m is None else f"{m:.2f} ± {h:.2f}"
    order = sorted(rows, key=lambda k: (k != "heuristic (persistence)", k))
    for label in order:
        lv = per_level(rows[label], qmeta)
        c = f"{mean(costs[label]):.3f}" if costs.get(label) else "–"
        nm = missing.get(label, 0) if label in costs else "–"
        lines.append(f"| {label} | {len(rows[label])} | {nm} | {fmt(lv['L1'])} | {fmt(lv['L2'])} | "
                     f"{fmt(lv['L3'])} | {fmt(lv['all'])} | {c} |")
    qids = sorted(qmeta, key=lambda k: (qmeta[k], k))
    lines += ["", "## Per query", "",
              "| analyst · condition | " + " | ".join(f"{q} ({qmeta[q]})" for q in qids) + " |",
              "|---|" + "---|" * len(qids)]
    for label in order:
        cells = []
        for q in qids:
            xs = [qs[q] for qs in rows[label].values() if q in qs]
            cells.append(f"{mean(xs):.2f} (n={len(xs)})" if xs else "–")
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
    lines += paired_section(rows, qmeta)
    text = "\n".join(lines) + "\n"
    (RESULTS / f"summary_{name}.md").write_text(text)
    return text


def paired(rows, qmeta, a, b, level):
    """Mean of (a - b) per freeze at one level, on freezes both cover. Pairing
    removes freeze difficulty (a 32-agent freeze is harder for everyone)."""
    la, lb = per_freeze_level(rows[a], qmeta, level), per_freeze_level(rows[b], qmeta, level)
    common = sorted(set(la) & set(lb))
    d = [la[f] - lb[f] for f in common]
    if not d:
        return None
    m, h = _ci(d)
    wins = sum(x > 0 for x in d), sum(x < 0 for x in d)
    return m, h, len(d), wins


def per_freeze_level(freeze_scores, qmeta, level):
    out = {}
    for f, qs in freeze_scores.items():
        xs = [v for k, v in qs.items() if level == "all" or qmeta[k] == level]
        if xs:
            out[f] = mean(xs)
    return out


def paired_section(rows, qmeta):
    """Every analyst view vs persistence and vs no-information, plus the
    view-vs-view pairs that answer the project's questions."""
    labels = [k for k in rows if k != "heuristic (persistence)"]
    models = sorted({k.split(" · ")[0] for k in labels})
    pairs = []
    for m in models:
        has = lambda c: f"{m} · {c}" in rows  # noqa: E731
        for c in ("dashboard", "dashboard2", "dashboard3", "raw", "both", "self"):
            if has(c):
                pairs.append((f"{m} · {c}", "heuristic (persistence)"))
                if has("none"):
                    pairs.append((f"{m} · {c}", f"{m} · none"))
        if has("raw") and has("dashboard"):
            pairs.append((f"{m} · raw", f"{m} · dashboard"))
        if has("dashboard2") and has("dashboard"):
            pairs.append((f"{m} · dashboard2", f"{m} · dashboard"))
        if has("dashboard3") and has("dashboard2"):
            pairs.append((f"{m} · dashboard3", f"{m} · dashboard2"))
    out = ["", "## Paired comparisons (same freezes)", "",
           "Difference A - B in mean score per freeze, ± ~95% CI; `wins` = freezes where A "
           "beat B / B beat A. A CI that excludes 0 is a difference we would report.", "",
           "| A | B | L1 | L2 | L3 | all |", "|---|---|---|---|---|---|"]
    for a, b in pairs:
        cells = []
        for lv in ("L1", "L2", "L3", "all"):
            r = paired(rows, qmeta, a, b, lv)
            cells.append("–" if r is None else
                         f"{r[0]:+.2f} ± {r[1]:.2f} ({r[3][0]}/{r[3][1]})")
        out.append(f"| {a} | {b} | " + " | ".join(cells) + " |")
    return out
