"""Static SVG figures for the write-up, drawn from the same scoring code as
results/summary_*.md. Light palette on a solid surface, so they read on
GitHub in either theme. No dependencies.

  uv run python -m sagat figures      # -> docs/fig_*.svg
"""
import json
from xml.sax.saxutils import escape

from . import score
from .config import REPO

INK, INK2, MUTED, GRID, AXIS, BG = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
ACCENT, RULE, NEG, POS = "#2a78d6", "#eb6834", "#2a78d6", "#e34948"
FONT = 'font-family="system-ui, -apple-system, Segoe UI, sans-serif"'
LEVELS = [("L1", "What's going on"), ("L2", "What it means"), ("L3", "What happens next")]
CHEAP = "openrouter:deepseek/deepseek-v4-flash"
STRONG = "openrouter:anthropic/claude-sonnet-5.5"
RULE_KEY = "heuristic (persistence)"


def _t(x, y, s, size=13, fill=INK2, anchor="start", weight=None):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}"{w} {FONT}>{escape(str(s))}</text>')


def level_figure(name, views, title, subtitle):
    """Small multiples, one panel per SA level: dot = mean, bar = ~95% CI,
    orange line = the persistence rule."""
    items, rows, costs, qmeta, missing = score.table(name)
    rule = score.per_level(rows[RULE_KEY], qmeta)
    left, panel, gap, top, rowh = 300, 230, 40, 118, 30
    W = left + 3 * panel + 2 * gap + 30
    H = top + len(views) * rowh + 46
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
           f'<rect width="{W}" height="{H}" fill="{BG}"/>',
           _t(20, 30, title, 18, INK, weight="600"), _t(20, 52, subtitle, 13, INK2)]
    for i, (key, label) in enumerate(views):
        y = top + i * rowh + rowh / 2
        out.append(_t(left - 14, y + 4, label, 13, INK, "end"))
    for p, (lv, lname) in enumerate(LEVELS):
        x0 = left + p * (panel + gap)
        sx = lambda v: x0 + v * panel  # noqa: E731
        out.append(_t(x0, top - 16, lname, 13, INK, weight="600"))
        for g in (0, 0.25, 0.5, 0.75, 1):
            out.append(f'<line x1="{sx(g):.1f}" x2="{sx(g):.1f}" y1="{top - 4}" y2="{H - 34}" stroke="{GRID}"/>')
            out.append(_t(sx(g), H - 16, f"{g:g}", 11, MUTED, "middle"))
        out.append(f'<line x1="{sx(rule[lv][0]):.1f}" x2="{sx(rule[lv][0]):.1f}" y1="{top - 4}" '
                   f'y2="{H - 34}" stroke="{RULE}" stroke-width="2"/>')
        for i, (key, label) in enumerate(views):
            m, h = score.per_level(rows[key], qmeta)[lv]
            y = top + i * rowh + rowh / 2
            out.append(f'<line x1="{sx(max(0, m - h)):.1f}" x2="{sx(min(1, m + h)):.1f}" y1="{y:.1f}" '
                       f'y2="{y:.1f}" stroke="{ACCENT}" stroke-width="2" stroke-linecap="round" opacity="0.45"/>')
            out.append(f'<circle cx="{sx(m):.1f}" cy="{y:.1f}" r="5" fill="{ACCENT}" stroke="{BG}" stroke-width="2"/>')
    lx = left
    out.append(f'<circle cx="{lx}" cy="72" r="5" fill="{ACCENT}"/>')
    out.append(_t(lx + 10, 76, "analyst average (bar = ~95% margin of error)", 12))
    out.append(f'<line x1="{lx + 300}" x2="{lx + 318}" y1="72" y2="72" stroke="{RULE}" stroke-width="2"/>')
    out.append(_t(lx + 324, 76, "“nothing changes” rule", 12))
    out.append("</svg>")
    return "\n".join(out)


def direction_figure(rows_spec, title, subtitle):
    """Diverging bars: wrong 'no' (left) vs wrong 'yes' (right) on the two
    yes/no forecasting questions."""
    data = []
    for name, key, label in rows_spec:
        items = {it["id"]: it for it in score.load_set(name)}
        fn = fp = 0
        for r in score.load_runs(name):
            if f"{r['model']} · {r['condition']}" != key or not r["answers"]:
                continue
            for q in items[r["freeze"]]["queries"]:
                if q["id"] in ("focal_chat_next", "human_next"):
                    a = r["answers"].get(q["id"])
                    fn += q["truth"] is True and a is not True
                    fp += q["truth"] is False and a is True
        data.append((label, fn, fp))
    left, half, top, rowh = 400, 220, 92, 30
    W, H = left + 2 * half + 70, top + len(data) * rowh + 20
    mid = left + half + 20
    mx = max(max(a, b) for _, a, b in data)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
           f'<rect width="{W}" height="{H}" fill="{BG}"/>',
           _t(20, 30, title, 18, INK, weight="600"), _t(20, 52, subtitle, 13, INK2),
           _t(mid - 8, top - 14, "← wrongly said “no, it won't happen”", 12, INK, "end"),
           _t(mid + 8, top - 14, "wrongly said “yes” →", 12, INK),
           f'<line x1="{mid}" x2="{mid}" y1="{top - 6}" y2="{H - 10}" stroke="{AXIS}"/>']
    for i, (label, fn, fp) in enumerate(data):
        y = top + i * rowh + 6
        wn, wy = fn / mx * half, fp / mx * half
        out.append(_t(left - 10, y + 13, label, 13, INK, "end"))
        out.append(f'<rect x="{mid - 1 - wn:.1f}" y="{y}" width="{wn:.1f}" height="18" rx="4" fill="{NEG}"/>')
        out.append(f'<rect x="{mid + 1:.1f}" y="{y}" width="{max(wy, 0.1):.1f}" height="18" rx="4" fill="{POS}"/>')
        out.append(_t(mid - 6 - wn, y + 13, fn, 12, INK, "end"))
        out.append(_t(mid + 6 + wy, y + 13, fp, 12, INK))
    out.append("</svg>")
    return "\n".join(out), data


def build():
    docs = REPO / "docs"
    fresh = level_figure("v2", [
        (f"{CHEAP} · none", "Guessing (cheap model)"),
        (f"{CHEAP} · dashboard", "Original dashboard (cheap)"),
        (f"{CHEAP} · dashboard2", "Improved dashboard (cheap)"),
        (f"{CHEAP} · dashboard3", "Improved + agents' plans (cheap)"),
        (f"{STRONG} · dashboard2", "Improved dashboard (strong)"),
        (f"{STRONG} · dashboard3", "Improved + agents' plans (strong)"),
        (f"{CHEAP} · custom-minimal_dashboard", "Chat feed only (cheap; the template)"),
    ], "Fresh 26 moments: the fixed dashboard helps understanding, not foresight",
        "Score by situation-awareness level (0 = always wrong, 1 = always right). "
        "Cheap = DeepSeek V4 Flash, strong = Claude Sonnet 5.5.")
    design = level_figure("v1", [
        (f"{CHEAP} · none", "Guessing (cheap model)"),
        (f"{STRONG} · none", "Guessing (strong model)"),
        (f"{CHEAP} · dashboard", "Dashboard (cheap)"),
        (f"{STRONG} · dashboard", "Dashboard (strong)"),
        (f"{CHEAP} · raw", "Raw records via SQL (cheap)"),
        (f"{CHEAP} · self", "One agent's own memory (cheap)"),
        (f"{STRONG} · self", "One agent's own memory (strong)"),
    ], "First 26 moments: what each view gives an analyst",
        "Same scale. The rule is perfect on the first two levels by construction, so it is "
        "a ceiling there and the bar to beat on the third.")
    direction, data = direction_figure([
        ("v1", f"{CHEAP} · dashboard", "Original dashboard, cheap · first 26"),
        ("v1", f"{STRONG} · dashboard", "Original dashboard, strong · first 26"),
        ("v2", f"{CHEAP} · dashboard", "Original dashboard, cheap · fresh 26"),
        ("v2", f"{CHEAP} · dashboard2", "Improved dashboard, cheap · fresh 26"),
        ("v2", f"{STRONG} · dashboard2", "Improved dashboard, strong · fresh 26"),
    ], "Analysts bet on activity stopping, and history panels fix that",
        "Wrong answers on the two yes/no forecasts (“will agent X post in 30 min?”, "
        "“will a human post in 2 h?”).")
    for fname, svg in (("fig_fresh_levels.svg", fresh), ("fig_design_levels.svg", design),
                       ("fig_forecast_errors.svg", direction)):
        (docs / fname).write_text(svg)
        print("wrote", docs / fname)
    print("error-direction counts:", json.dumps(data))
