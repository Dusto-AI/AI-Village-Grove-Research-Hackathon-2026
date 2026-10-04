"""Supplement: run-to-run variation. The same analyst (DeepSeek V4 Flash),
same views (original and improved dashboard), same 26 fresh moments, run
three times (v2, v2r2, v2r3). How much do scores move, and do the
conclusions survive?

  uv run python scripts/variance.py    # -> docs/supplement/fig_variance.svg + tables
"""
import sys
from pathlib import Path
from statistics import mean, pstdev

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sagat import score as S                                        # noqa: E402
from sagat.config import REPO                                       # noqa: E402
from sagat.figures import ACCENT, BG, GRID, INK, INK2, MUTED, RULE, _t  # noqa: E402

CHEAP = "openrouter:deepseek/deepseek-v4-flash"
REPS = ["v2", "v2r2", "v2r3"]
CONDS = [("dashboard", "Original dashboard"), ("dashboard2", "Improved dashboard")]
LV = ["L1", "L2", "L3"]


def main():
    data = {}
    for rep in REPS:
        _, rows, _, qmeta, missing = S.table(rep)
        for c, _ in CONDS:
            data[(rep, c)] = (rows[f"{CHEAP} · {c}"], missing.get(f"{CHEAP} · {c}", 0))
    print("level means per repeat (no-answer runs in brackets)")
    lvl = {}
    for c, label in CONDS:
        for rep in REPS:
            rows, miss = data[(rep, c)]
            lv = S.per_level(rows, qmeta)
            lvl[(c, rep)] = {k: v[0] for k, v in lv.items()}
            print(f"  {label:20s} {rep:5s} " + " ".join(f"{k}={lv[k][0]:.2f}" for k in LV + ['all']) + f"  [{miss}]")
    print("\nspread across the 3 repeats (max - min) of each level mean")
    for c, label in CONDS:
        print(f"  {label:20s} " + " ".join(f"{k}={max(lvl[(c, r)][k] for r in REPS) - min(lvl[(c, r)][k] for r in REPS):.2f}" for k in LV + ["all"]))
    print("\nsame answer-score on all 3 repeats, per (moment, question)")
    for c, label in CONDS:
        same = tot = 0
        sds = []
        common = set.intersection(*(set(data[(r, c)][0]) for r in REPS))
        for f in common:
            for q in data[("v2", c)][0][f]:
                xs = [data[(r, c)][0][f].get(q) for r in REPS]
                if None in xs:
                    continue
                tot += 1
                same += len(set(xs)) == 1
            sds.append(pstdev([mean(data[(r, c)][0][f].values()) for r in REPS]))
        print(f"  {label:20s} {same}/{tot} = {same / tot:.0%}; per-moment score SD across repeats: mean {mean(sds):.3f}")
    print("\nimproved minus original, paired by moment, on each repeat")
    for rep in REPS:
        rows = {f"{CHEAP} · {c}": data[(rep, c)][0] for c, _ in CONDS}
        out = []
        for lv in ("L2", "L3", "all"):
            r = S.paired(rows, qmeta, f"{CHEAP} · dashboard2", f"{CHEAP} · dashboard", lv)
            out.append(f"{lv} {r[0]:+.2f} ± {r[1]:.2f} ({r[3][0]}/{r[3][1]})")
        print(f"  {rep:5s} " + "   ".join(out))
    # figure: per level, three dots per condition (one per repeat)
    left, pw, gap, top = 200, 210, 64, 86
    W, H = left + 3 * pw + 2 * gap + 30, top + 2 * 44 + 50
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
           f'<rect width="{W}" height="{H}" fill="{BG}"/>',
           _t(20, 28, "Same analyst, same moments, three runs", 18, INK, weight="600"),
           _t(20, 50, "Each dot is one complete run over the 26 fresh moments (cheap analyst). "
              "The spread is the run-to-run wobble.", 13, INK2)]
    names = {"L1": "What's going on", "L2": "What it means", "L3": "What happens next"}
    lo = {"L1": 0.9, "L2": 0.6, "L3": 0.4}
    hi = {"L1": 1.0, "L2": 1.0, "L3": 0.8}
    for p, k in enumerate(LV):
        x0 = left + p * (pw + gap)
        sx = lambda v, k=k: x0 + (v - lo[k]) / (hi[k] - lo[k]) * pw   # noqa: E731
        svg.append(_t(x0, top - 16, names[k], 13, INK, weight="600"))
        for g in [lo[k], (lo[k] + hi[k]) / 2, hi[k]]:
            svg.append(f'<line x1="{sx(g):.1f}" x2="{sx(g):.1f}" y1="{top - 6}" y2="{H - 34}" stroke="{GRID}"/>')
            svg.append(_t(sx(g), H - 16, f"{g:.2f}".rstrip("0").rstrip("."), 11, MUTED, "middle"))
        for i, (c, label) in enumerate(CONDS):
            y = top + 22 + i * 44
            if p == 0:
                svg.append(_t(left - 14, y + 4, label, 13, INK, "end"))
            color = MUTED if c == "dashboard" else ACCENT
            for rep in REPS:
                v = lvl[(c, rep)][k]
                svg.append(f'<circle cx="{sx(v):.1f}" cy="{y}" r="5" fill="{color}" fill-opacity="0.8" stroke="{BG}" stroke-width="2"/>')
    svg.append("</svg>")
    (REPO / "docs" / "supplement" / "fig_variance.svg").write_text("\n".join(svg))
    print("-> docs/supplement/fig_variance.svg")


if __name__ == "__main__":
    main()
