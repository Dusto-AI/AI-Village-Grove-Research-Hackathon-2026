"""Supplement: how quickly does "nothing changes" stop working?

For every frozen moment (both sets, 52), predict that the agents active in
the 30 minutes before the freeze are the agents active in a 30-minute
window starting h minutes after it, and score the overlap (F1, as in the
main test). Split by time of day frozen, because the decline turns out to be the
working day ending. (Predicting "everyone on the roster" scores the same at
every horizon, since freezes are mid-workday when nearly everyone is
active.) No model calls; uses the source traces directly.

  uv run python scripts/horizon.py      # -> docs/supplement/fig_horizon.svg + table
"""
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sagat import score as S                      # noqa: E402
from sagat.config import TRACES_DB, to_db, REPO   # noqa: E402
from sagat.figures import ACCENT, BG, FONT, GRID, INK, INK2, MUTED, RULE, _t  # noqa: E402

HORIZONS = [0, 30, 60, 90, 120, 180, 240, 300]


def f1(a, b):
    a, b = set(a), set(b)
    if not a and not b:
        return 1.0
    tp = len(a & b)
    return 0.0 if not tp else 2 * tp / (len(a) + len(b))


def main():
    con = sqlite3.connect(f"file:{TRACES_DB}?mode=ro", uri=True)
    def active(t, a, b):
        return {r[0] for r in con.execute(
            "SELECT DISTINCT agent FROM traces WHERE created_at > ? AND created_at <= ?",
            (to_db(t + timedelta(minutes=a)), to_db(t + timedelta(minutes=b))))}
    groups = {"all": {}, "before noon": {}, "noon or later": {}}
    for name in ("v1", "v2"):
        for it in S.load_set(name):
            t = datetime.fromisoformat(it["t_utc"])
            g = "before noon" if int(it["t_pt"][11:13]) < 12 else "noon or later"
            now = active(t, -30, 0)
            for h in HORIZONS:
                v = f1(now, active(t, h, h + 30))
                for key in ("all", g):
                    groups[key].setdefault(h, []).append(v)
    print("horizon_min  all  before_noon  noon_or_later")
    for h in HORIZONS:
        print(f"{h:11d}  {mean(groups['all'][h]):.2f}  {mean(groups['before noon'][h]):11.2f}  "
              f"{mean(groups['noon or later'][h]):13.2f}")
    n = {k: len(v[0]) for k, v in groups.items()}
    W, H, left, top, pw, ph = 760, 410, 70, 92, 640, 240
    sx = lambda h: left + h / 300 * pw            # noqa: E731
    sy = lambda v: top + (1 - v) * ph             # noqa: E731
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
           f'<rect width="{W}" height="{H}" fill="{BG}"/>',
           _t(20, 28, "“Nothing changes” works until the working day ends", 18, INK, weight="600"),
           _t(20, 50, "Predicting which agents will be active in a 30-minute window h minutes after "
              "the freeze,", 13, INK2),
           _t(20, 68, "split by the time of day frozen (1 = perfect).", 13, INK2)]
    for v in (0, 0.25, 0.5, 0.75, 1):
        out.append(f'<line x1="{left}" x2="{left + pw}" y1="{sy(v):.1f}" y2="{sy(v):.1f}" stroke="{GRID}"/>')
        out.append(_t(left - 8, sy(v) + 4, f"{v:g}", 11, MUTED, "end"))
    for h in HORIZONS:
        out.append(_t(sx(h), top + ph + 18, f"{h}", 11, MUTED, "middle"))
    out.append(_t(left + pw / 2, top + ph + 38, "minutes after the freeze", 12, INK2, "middle"))
    for key, color in (("before noon", ACCENT), ("noon or later", RULE)):
        pts = [(h, mean(groups[key][h])) for h in HORIZONS]
        out.append('<polyline points="' + " ".join(f"{sx(h):.1f},{sy(v):.1f}" for h, v in pts)
                   + f'" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round"/>')
        for h, v in pts:
            out.append(f'<circle cx="{sx(h):.1f}" cy="{sy(v):.1f}" r="4" fill="{color}" stroke="{BG}" stroke-width="2"/>')
        lab_h = 120 if key == "before noon" else 90
        lab_v = mean(groups[key][lab_h])
        out.append(_t(sx(lab_h) + 10, sy(lab_v) + (-8 if key == "before noon" else 16),
                      f"frozen {key} (n={n[key]})", 12, INK))
    out.append("</svg>")
    path = REPO / "docs" / "supplement" / "fig_horizon.svg"
    path.write_text("\n".join(out))
    print("->", path)


if __name__ == "__main__":
    main()
