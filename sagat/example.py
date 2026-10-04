"""Generate the write-up's worked example from the records (nothing retyped).

  uv run python -m sagat example --name v2 --freeze 20251225T181018Z

Prints markdown: an excerpt of the status board the analyst saw, then
every question with the true answer, the "nothing changes" rule, and the
cheap analyst on the original and improved dashboards. Note the board
excerpt is AI Village dataset text (agent names, task titles).
"""
import json
import sqlite3
from datetime import datetime, timedelta

from . import score
from .config import RESULTS, TS_FMT
from .explorer import QUESTION_SHORT


def _answer(q, a):
    if a is None:
        return "(skipped)"
    if q["kind"] == "set":
        t, s = set(q["truth"]), set(a)
        missed, extra = sorted(t - s), sorted(s - t)
        if not missed and not extra:
            return f"all {len(t)} right" if t else "none (right)"
        return "; ".join(x for x in (f"missed {', '.join(missed)}" if missed else "",
                                     f"extra {', '.join(extra)}" if extra else "") if x)
    return {True: "yes", False: "no"}.get(a, str(a))


def _mark(q, a):
    sc = score.score(q, a)
    return ("✓" if sc == 1 else "✗" if sc == 0 else f"◐ {sc:.2f}")


def build(name, fid, model="openrouter_deepseek__deepseek-v4-flash"):
    it = next(x for x in score.load_set(name) if x["id"] == fid)
    runs = {}
    for cond in ("dashboard", "dashboard2"):
        p = RESULTS / "runs" / name / model / cond / f"{fid}.json"
        runs[cond] = json.loads(p.read_text())["answers"]
    con = sqlite3.connect(it["frozen_db"])
    t = datetime.strptime(it["t_pt"][:19], TS_FMT)
    ago = lambda m: (t - timedelta(minutes=m)).strftime(TS_FMT)  # noqa: E731
    lines = [f"**The moment:** {t:%d %B %Y, %H:%M} Pacific time · {len(it['roster'])} agents "
             f"active · agent X (picked at random among busy agents) = **{it['focal']}**.", "",
             "**What the analyst saw** (excerpt of the original status board; the full board "
             "also lists the last 25 chat messages):", "",
             "| Agent | Current task (its own words) | Actions, last 30 min | Error rate, last hour | Chat messages, last hour |",
             "|---|---|---|---|---|"]
    agents = [r[0] for r in con.execute(
        "SELECT DISTINCT agent FROM turns WHERE ts_pt > ? ORDER BY 1", (ago(1440),))]
    for a in agents:
        s = con.execute("SELECT short_goal FROM sessions WHERE agent = ? ORDER BY ts_pt DESC "
                        "LIMIT 1", (a,)).fetchone()
        n30 = con.execute("SELECT count(*) FROM turns WHERE agent = ? AND ts_pt > ?",
                          (a, ago(30))).fetchone()[0]
        n60, e60 = con.execute("SELECT count(*), coalesce(sum(has_error), 0) FROM turns "
                               "WHERE agent = ? AND ts_pt > ?", (a, ago(60))).fetchone()
        c60 = con.execute("SELECT count(*) FROM chat WHERE speaker = ? AND ts_pt > ?",
                          (a, ago(60))).fetchone()[0]
        task = ((s[0] if s else "") or "-").replace("|", "/")
        lines.append(f"| {a} | {task} | {n30} | {f'{e60 / n60:.0%}' if n60 else '-'} | {c60} |")
    con.close()
    lines += ["", "**The 11 questions, and how each answered:**", "",
              "| Level | Question | True answer | “Nothing changes” rule | Original dashboard | Improved dashboard |",
              "|---|---|---|---|---|---|"]
    lvname = {"L1": "What's going on", "L2": "What it means", "L3": "What happens next"}
    for q in it["queries"]:
        truth = (", ".join(q["truth"]) or "none") if q["kind"] == "set" else (
            " or ".join(q["truth"]) if q["kind"] == "single" else
            {True: "yes", False: "no"}.get(q["truth"], q["truth"]))
        if q["kind"] == "set" and len(q["truth"]) > 4:
            truth = f"{len(q['truth'])} agents"
        if q["kind"] == "mc":
            truth = f"{q['truth']}: {q['options']['ABCD'.index(q['truth'])]}"
        cells = [f"{_mark(q, a)} {_answer(q, a)}" for a in
                 (q["heuristic"], runs["dashboard"].get(q["id"]), runs["dashboard2"].get(q["id"]))]
        lines.append(f"| {lvname[q["level"]]} | {QUESTION_SHORT[q["id"]].replace(" (see Entry 14)", "")} | {truth} | " + " | ".join(cells) + " |")
    # the improved dashboard's extra panel, as the analyst saw it, for agent X
    from .dashboard import render_v2
    v2 = render_v2(it["frozen_db"], it["t_pt"])
    panel = v2[v2.index("## Who is talking to whom"):v2.index("## Typical patterns")]
    xline = next((l for l in panel.splitlines() if l.startswith(f"- {it['focal']}:")), None)
    lines += ["", "**What the improved dashboard added** (its new panel's line for agent X, "
              "verbatim):", "", f"> {xline[2:] if xline else '(no line for agent X)'}"]
    return "\n".join(lines)
