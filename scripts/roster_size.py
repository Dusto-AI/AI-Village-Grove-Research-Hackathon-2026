"""Supplement: are bigger swarms harder to oversee?

Per-moment score (all 11 questions averaged, and per level) against the
number of agents on the roster, for each view (cheap model; both freeze
sets where the view was run). Rank correlation (Spearman) reported per
panel. No model calls.

  uv run python scripts/roster_size.py   # -> docs/supplement/fig_roster_size.svg
"""
import sys
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sagat import score as S                                   # noqa: E402
from sagat.config import REPO                                  # noqa: E402
from sagat.figures import ACCENT, BG, GRID, INK, INK2, MUTED, _t  # noqa: E402

CHEAP = "openrouter:deepseek/deepseek-v4-flash"
VIEWS = [("none", "Guessing"), ("dashboard", "Dashboard"), ("raw", "Raw records (SQL)"),
         ("self", "One agent's own memory"), ("dashboard2", "Improved dashboard")]


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(x, y):
    rx, ry = ranks(x), ranks(y)
    mx, my = mean(rx), mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else 0.0


def main():
    pts = {}
    for name in ("v1", "v2"):
        items, rows, _, qmeta, _ = S.table(name)
        size = {f: len(it["roster"]) for f, it in items.items()}
        for cond, _ in VIEWS:
            key = f"{CHEAP} · {cond}"
            if key not in rows:
                continue
            for f, qs in rows[key].items():
                lv = {l: mean(v for k, v in qs.items() if qmeta[k] == l) for l in ("L1", "L2", "L3")
                      if any(qmeta[k] == l for k in qs)}
                pts.setdefault(cond, []).append((size[f], mean(qs.values()), lv))
    print("view                     n   rho(all)  rho(L1)  rho(L2)  rho(L3)")
    rho = {}
    for cond, label in VIEWS:
        p = pts.get(cond, [])
        xs = [a for a, _, _ in p]
        r_all = spearman(xs, [b for _, b, _ in p])
        r_l = {l: spearman([a for a, _, lv in p if l in lv], [lv[l] for _, _, lv in p if l in lv]) for l in ("L1", "L2", "L3")}
        rho[cond] = r_all
        print(f"{label:24s} {len(p):2d}   {r_all:+.2f}     {r_l['L1']:+.2f}    {r_l['L2']:+.2f}    {r_l['L3']:+.2f}")
    pw, ph, gap, left, top = 190, 170, 34, 50, 80
    W = left + len(VIEWS) * (pw + gap)
    H = top + ph + 64
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
           f'<rect width="{W}" height="{H}" fill="{BG}"/>',
           _t(20, 28, "Bigger swarms: guessing degrades; the plain dashboard holds steady", 18, INK, weight="600"),
           _t(20, 50, "Each dot is one frozen moment: its average score over all 11 questions vs the number "
              "of agents (cheap analyst). ρ = rank correlation.", 13, INK2)]
    for p_i, (cond, label) in enumerate(VIEWS):
        x0 = left + p_i * (pw + gap)
        sx = lambda n: x0 + (n - 5) / 28 * pw        # noqa: E731
        sy = lambda v: top + (1 - v) * ph            # noqa: E731
        out.append(_t(x0, top - 12, label, 13, INK, weight="600"))
        for v in (0, 0.5, 1):
            out.append(f'<line x1="{x0}" x2="{x0 + pw}" y1="{sy(v):.1f}" y2="{sy(v):.1f}" stroke="{GRID}"/>')
            if p_i == 0:
                out.append(_t(x0 - 6, sy(v) + 4, f"{v:g}", 11, MUTED, "end"))
        for n in (10, 20, 30):
            out.append(_t(sx(n), top + ph + 16, str(n), 11, MUTED, "middle"))
        for a, b, _ in pts.get(cond, []):
            out.append(f'<circle cx="{sx(a):.1f}" cy="{sy(b):.1f}" r="3.5" fill="{ACCENT}" fill-opacity="0.75" stroke="{BG}" stroke-width="1.5"/>')
        out.append(_t(x0 + pw, top + ph + 34, f"ρ = {rho[cond]:+.2f} (n={len(pts.get(cond, []))})", 12, INK2, "end"))
    out.append(_t(left + (W - left) / 2, H - 6, "agents on the roster", 12, INK2, "middle"))
    out.append("</svg>")
    path = REPO / "docs" / "supplement" / "fig_roster_size.svg"
    path.write_text("\n".join(out))
    print("->", path)


if __name__ == "__main__":
    main()
