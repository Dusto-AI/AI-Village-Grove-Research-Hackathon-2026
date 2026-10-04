"""A plain status board rendered from the frozen db only, the kind of overview
a person would build first. It is the 'dashboard' condition: the analyst
gets this text and no query access.

Swap in your own renderer to SAGAT-test your own dashboard. The harness only
needs a function frozen_db_path -> text (or image) shown to the analyst.
"""
import re
import sqlite3
from datetime import datetime, timedelta

from .config import TS_FMT


def _dt(s):
    return datetime.strptime(s[:19], TS_FMT)


def render(db_path, freeze_pt):
    con = sqlite3.connect(db_path)
    t = _dt(freeze_pt)
    def ago(m):
        return (t - timedelta(minutes=m)).strftime(TS_FMT)

    lines = [f"# Village status board — frozen at {freeze_pt} PT", ""]
    g = con.execute("SELECT goal, start_pt FROM village_goals ORDER BY start_pt DESC LIMIT 1"
                    ).fetchone()
    if g:
        lines += [f"Current village goal (since {g[1][:16]}): {g[0]}", ""]

    lines += ["## Agents (active in the last 24h)", "",
              "| agent | current task (session goal) | task age | actions 30m | "
              "actions 60m | error rate 60m | last action | chat msgs 60m | last chat |",
              "|---|---|---|---|---|---|---|---|---|"]
    agents = [r[0] for r in con.execute(
        "SELECT DISTINCT agent FROM turns WHERE ts_pt > ? UNION "
        "SELECT DISTINCT speaker FROM chat WHERE ts_pt > ? AND speaker_type = 'agent' "
        "ORDER BY 1", (ago(1440), ago(1440)))]
    for a in agents:
        s = con.execute("SELECT short_goal, ts_pt FROM sessions WHERE agent = ? "
                        "ORDER BY ts_pt DESC LIMIT 1", (a,)).fetchone()
        n30 = con.execute("SELECT count(*) FROM turns WHERE agent = ? AND ts_pt > ?",
                          (a, ago(30))).fetchone()[0]
        n60, e60 = con.execute("SELECT count(*), coalesce(sum(has_error), 0) FROM turns "
                               "WHERE agent = ? AND ts_pt > ?", (a, ago(60))).fetchone()
        last = con.execute("SELECT max(ts_pt) FROM turns WHERE agent = ?", (a,)).fetchone()[0]
        c60 = con.execute("SELECT count(*) FROM chat WHERE speaker = ? AND ts_pt > ?",
                          (a, ago(60))).fetchone()[0]
        lc = con.execute("SELECT max(ts_pt) FROM chat WHERE speaker = ?", (a,)).fetchone()[0]
        age = f"{int((t - _dt(s[1])).total_seconds() // 60)}m" if s else "-"
        task = (s[0] or "").replace("|", "/")[:70] if s else "-"
        rate = f"{e60 / n60:.0%}" if n60 else "-"
        lines.append(f"| {a} | {task} | {age} | {n30} | {n60} | {rate} | "
                     f"{(last or '-')[11:16]} | {c60} | {(lc or '-')[5:16]} |")

    h = con.execute("SELECT count(*), max(ts_pt) FROM chat WHERE speaker_type != 'agent' "
                    "AND ts_pt > ?", (ago(120),)).fetchone()
    lines += ["", f"Human chat messages in the last 2h: {h[0]}"
              + (f" (latest {h[1][11:16]})" if h[0] else ""), "",
              "## Recent chat (last 25 messages, newest last)", ""]
    for ts, spk, content in reversed(con.execute(
            "SELECT ts_pt, speaker, content FROM chat ORDER BY ts_pt DESC LIMIT 25").fetchall()):
        body = " ".join((content or "").split())[:240]
        lines.append(f"- {ts[5:16]} **{spk}**: {body}")
    con.close()
    return "\n".join(lines)


# ------------------------------------------------------------------ v2
# Built after SAGAT round 1 (freeze set v1) showed two gaps: no view of who
# interacts with whom (focal_partner 0.29 vs 0.71 with raw access), and no
# help with projection (no view beat persistence on L3). v2 adds an
# interaction panel and a "typical patterns" panel of base rates computed
# from the visible past only. Evaluate it on a fresh freeze set, not v1.

def _mention_counts(con, names, since):
    alts = "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
    rx = re.compile(rf"(?<![\w.])({alts})(?![\w]|\.\d)", re.IGNORECASE)
    canon = {n.lower(): n for n in names}
    pair = {}
    for spk, content in con.execute(
            "SELECT speaker, content FROM chat WHERE speaker_type = 'agent' AND ts_pt > ?",
            (since,)):
        for m in rx.findall(content or ""):
            other = canon[m.lower()]
            if other != spk:
                key = tuple(sorted((spk, other)))
                pair[key] = pair.get(key, 0) + 1
    return pair


def _active_slots(con, minutes):
    """Start times of past fixed-length slots (30 or 120 min) in which the
    village was running, i.e. had at least one action, within the snapshot."""
    slots = set()
    for (ts,) in con.execute("SELECT ts_pt FROM turns"):
        d = _dt(ts)
        if minutes < 60:
            floor = d.replace(minute=d.minute // minutes * minutes, second=0)
        else:
            h = minutes // 60
            floor = d.replace(hour=d.hour // h * h, minute=0, second=0)
        slots.add(floor)
    return sorted(slots)


def render_v2(db_path, freeze_pt):
    base = render(db_path, freeze_pt)
    con = sqlite3.connect(db_path)
    t = _dt(freeze_pt)
    def ago(m):
        return (t - timedelta(minutes=m)).strftime(TS_FMT)
    agents = [r[0] for r in con.execute(
        "SELECT DISTINCT agent FROM turns WHERE ts_pt > ? UNION "
        "SELECT DISTINCT speaker FROM chat WHERE ts_pt > ? AND speaker_type = 'agent' "
        "ORDER BY 1", (ago(1440), ago(1440)))]

    lines = ["", "## Who is talking to whom (last 2h of chat: times one names the other)", ""]
    pair = _mention_counts(con, agents, ago(120))
    for a in agents:
        mine = sorted(((n, b if a2 == a else a2) for (a2, b), n in pair.items() if a in (a2, b)),
                      reverse=True)[:3]
        if mine:
            lines.append(f"- {a}: " + ", ".join(f"{o} ({n})" for n, o in mine))
    if not pair:
        lines.append("- no agent named another agent in the last 2h")

    # base rates over the visible past (up to 96h, excluding the last 2h so
    # the "recent" columns above stay separate from "typical")
    slots30 = _active_slots(con, 30)
    slots30 = [s for s in slots30 if s < t - timedelta(hours=2)]
    chat = [(_dt(ts), spk, st) for ts, spk, st in
            con.execute("SELECT ts_pt, speaker, speaker_type FROM chat")]
    def share_posting(pred, slots, width):
        if not slots:
            return None
        hit = 0
        for s in slots:
            e = s + width
            hit += any(s <= d < e and pred(spk, st) for d, spk, st in chat)
        return hit / len(slots)
    slots2h = _active_slots(con, 120)
    slots2h = [s for s in slots2h if s < t - timedelta(hours=2)]
    human = share_posting(lambda spk, st: st != "agent", slots2h, timedelta(hours=2))
    lines += ["", "## Typical patterns (from the visible history before the last 2h)", ""]
    if human is not None:
        lines.append(f"- A human posted in {human:.0%} of past 2-hour stretches while the "
                     f"village was running ({len(slots2h)} stretches).")
    # same clock window 90-120 min later on previous days
    days = sorted({s.date() for s in slots30 if s.date() < t.date()})
    lines += ["", "| agent | posts in a typical 30 min | active 90-120 min after this "
              "time of day, on previous days |", "|---|---|---|"]
    turns_by_agent = {}
    for ts, a in con.execute("SELECT ts_pt, agent FROM turns"):
        turns_by_agent.setdefault(a, []).append(_dt(ts))
    for a in agents:
        p = share_posting(lambda spk, st, a=a: spk == a, slots30, timedelta(minutes=30))
        later_hits, later_days = 0, 0
        for d in days:
            lo = datetime.combine(d, t.time()) + timedelta(minutes=90)
            hi = lo + timedelta(minutes=30)
            village_on = any(lo <= x < hi for xs in turns_by_agent.values() for x in xs)
            if village_on:
                later_days += 1
                later_hits += any(lo <= x < hi for x in turns_by_agent.get(a, []))
        later = f"{later_hits}/{later_days} days" if later_days else "no comparable days"
        lines.append(f"| {a} | {'-' if p is None else f'{p:.0%}'} of stretches | {later} |")
    con.close()
    return base + "\n" + "\n".join(lines)


# ------------------------------------------------------------------ v3
# Built after v2's held-out test: forecasting still only tied persistence,
# with analysts consistently betting that activity would stop. v3 adds what
# the agents themselves say they intend to do next: the full text of each
# agent's current session goal, and the plan / next-steps part of its
# memory file. Both were written by the agent before the freeze.

_PLAN_HEAD = re.compile(r"(?im)^.{0,12}(next steps?|next actions?|plan\b|plans\b|to-?do|"
                        r"priorit|upcoming|pending|queue|immediate)[^\n]{0,60}$")


def _plan_excerpt(memory, limit=450):
    """First plan-like section of a memory file: the heading line and what
    follows it, flattened. Heuristic; empty if no such heading."""
    m = _PLAN_HEAD.search(memory or "")
    if not m:
        return ""
    return " ".join(memory[m.start():m.start() + limit].split())


def render_v3(db_path, freeze_pt):
    base = render_v2(db_path, freeze_pt)
    con = sqlite3.connect(db_path)
    t = _dt(freeze_pt)
    since = (t - timedelta(hours=24)).strftime(TS_FMT)
    agents = [r[0] for r in con.execute(
        "SELECT DISTINCT agent FROM turns WHERE ts_pt > ? UNION "
        "SELECT DISTINCT speaker FROM chat WHERE ts_pt > ? AND speaker_type = 'agent' "
        "ORDER BY 1", (since, since))]
    lines = ["", "## What each agent says it plans to do (its own words, written before "
             "the freeze)", ""]
    for a in agents:
        g = con.execute("SELECT goal FROM sessions WHERE agent = ? ORDER BY ts_pt DESC "
                        "LIMIT 1", (a,)).fetchone()
        mem = con.execute("SELECT content FROM memories WHERE agent = ?", (a,)).fetchone()
        goal = " ".join((g[0] or "").split())[:350] if g else ""
        plan = _plan_excerpt(mem[0]) if mem else ""
        if not goal and not plan:
            continue
        lines.append(f"### {a}")
        if goal:
            lines.append(f"- Current task, in full: {goal}")
        if plan:
            lines.append(f"- From its memory file: {plan}")
    con.close()
    return base + "\n" + "\n".join(lines)
