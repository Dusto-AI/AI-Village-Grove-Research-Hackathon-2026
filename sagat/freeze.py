"""Freeze points: sample a moment t, then build two strictly separated views.

- `Window`: everything the ground-truth extractors need, including the hidden
  future (t, t+HORIZON]. Never shown to an analyst.
- `build_frozen_db`: the analyst's world, a fresh SQLite file containing only
  rows with timestamp <= t (and >= t - LOOKBACK). Current-state columns that
  would leak the future (agents.money, status, room membership, a goal's
  end_time set after t) are dropped or nulled.

SAGAT's freeze is a pause of a live simulation; here it is a time cut on a
fully logged one, which is what makes projection (L3) scorable.
"""
import json
import random
import sqlite3
from dataclasses import dataclass, field
from datetime import timedelta

from .config import CACHE_DB, TRACES_DB, VILLAGE_DB, WORK, parse_ts, to_db, to_pt

LOOKBACK = timedelta(hours=96)   # analyst-visible history (spans a weekend)
HORIZON = timedelta(hours=3)     # hidden future used for L3 ground truth
ROSTER_WINDOW = timedelta(hours=24)


def ro(path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


@dataclass
class Window:
    t: object                       # freeze time, aware UTC datetime
    turns: list = field(default_factory=list)     # (dt, agent, session_id, action, has_error)
    chat: list = field(default_factory=list)      # (dt, speaker or None, speaker_type, content)
    sessions: list = field(default_factory=list)  # (dt, agent, session_id, short_goal)
    roster: list = field(default_factory=list)    # agents seen in the 24h before t

    def turns_in(self, a, b):
        """Turns with t+a < ts <= t+b (offsets as timedeltas, negative = past)."""
        lo, hi = self.t + a, self.t + b
        return [x for x in self.turns if lo < x[0] <= hi]

    def chat_in(self, a, b):
        lo, hi = self.t + a, self.t + b
        return [x for x in self.chat if lo < x[0] <= hi]

    def current_session(self, agent):
        past = [s for s in self.sessions if s[1] == agent and s[0] <= self.t]
        return past[-1] if past else None


def load_window(t, traces=None, cache=None):
    traces = traces or ro(TRACES_DB)
    cache = cache or ro(CACHE_DB)
    lo, hi = to_db(t - LOOKBACK), to_db(t + HORIZON)
    w = Window(t=t)
    w.turns = [(parse_ts(r["created_at"]), r["agent"], r["session_id"], r["action"],
                r["has_error"])
               for r in traces.execute(
                   "SELECT created_at, agent, session_id, action, has_error FROM traces "
                   "WHERE created_at > ? AND created_at <= ? ORDER BY created_at", (lo, hi))]
    w.chat = [(parse_ts(r["ts"]), r["speaker"], r["speaker_type"], r["content"] or "")
              for r in cache.execute(
                  "SELECT ts, speaker, speaker_type, content FROM chat "
                  "WHERE ts > ? AND ts <= ? ORDER BY ts", (lo, hi))]
    w.sessions = [(parse_ts(r["ts"]), r["agent"], r["session_id"], r["short_goal"] or "")
                  for r in cache.execute(
                      "SELECT ts, agent, session_id, short_goal FROM sessions "
                      "WHERE ts > ? AND ts <= ? ORDER BY ts", (lo, hi))]
    seen = {x[1] for x in w.turns_in(-ROSTER_WINDOW, timedelta(0))}
    seen |= {x[1] for x in w.chat_in(-ROSTER_WINDOW, timedelta(0)) if x[1]}
    w.roster = sorted(seen)
    return w


def sample_freezes(n, months, seed=0, min_active=4, exclude=()):
    """Stratified by month: pick a month round-robin, then a random turn in it
    as the candidate t. Activity-weighted within a month by construction
    (SAGAT freezes mid-operation, not at shift start). Accept t only if the
    village is genuinely running around it: >= min_active agents acting in the
    30 min before, and activity continuing 60-120 min after (so L3 queries
    are not trivially 'the day ended'). `exclude`: freeze times from another
    set; new freezes stay >= 24h away from them, so a held-out set never
    shares a day with the set a tool was designed on."""
    rng = random.Random(seed)
    traces, cache = ro(TRACES_DB), ro(CACHE_DB)
    bounds = {}
    for m in months:
        r = traces.execute("SELECT min(rowid), max(rowid) FROM traces WHERE month = ?",
                           (m,)).fetchone()
        if r[0] is not None:
            bounds[m] = (r[0], r[1])
    out, attempts, i = [], 0, 0
    order = list(bounds)
    while len(out) < n and attempts < n * 50:
        attempts += 1
        m = order[i % len(order)]
        row = traces.execute("SELECT created_at, month FROM traces WHERE rowid = ?",
                             (rng.randint(*bounds[m]),)).fetchone()
        if row is None or row["month"] != m:
            continue          # rowids are not month-contiguous; resample
        t = parse_ts(row["created_at"]).replace(microsecond=0)
        if any(abs((t - f.t).total_seconds()) < 6 * 3600 for f in out):
            continue          # keep freezes on distinct days/half-days
        if any(abs((t - x).total_seconds()) < 24 * 3600 for x in exclude):
            continue          # held-out set: no shared days with the excluded set
        w = load_window(t, traces, cache)
        active = {x[1] for x in w.turns_in(timedelta(minutes=-30), timedelta(0))}
        later = w.turns_in(timedelta(minutes=60), timedelta(minutes=120))
        if len(active) >= min_active and later:
            out.append(w)
            i += 1
    out.sort(key=lambda w: w.t)
    return out


def build_frozen_db(w, path):
    """The analyst's world at time t. Timestamps are converted to PT strings,
    the village's own working timezone."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    lo, t = to_db(w.t - LOOKBACK), to_db(w.t)
    out = sqlite3.connect(path)
    traces, cache, village = ro(TRACES_DB), ro(CACHE_DB), ro(VILLAGE_DB)
    out.executescript("""
        CREATE TABLE agents (name TEXT, model TEXT);
        CREATE TABLE chat (ts_pt TEXT, speaker TEXT, speaker_type TEXT, content TEXT);
        CREATE TABLE sessions (ts_pt TEXT, agent TEXT, session_id TEXT,
                               short_goal TEXT, goal TEXT);
        CREATE TABLE turns (ts_pt TEXT, agent TEXT, session_id TEXT, action TEXT,
                            has_error INTEGER, narration TEXT, reasoning TEXT);
        CREATE TABLE memories (ts_pt TEXT, agent TEXT, content TEXT);
        CREATE TABLE village_goals (start_pt TEXT, end_pt TEXT, goal TEXT);
    """)
    out.executemany("INSERT INTO agents VALUES (?,?)",
                    cache.execute("SELECT name, model FROM agents WHERE created_at <= ?",
                                  (t,)).fetchall())
    out.executemany("INSERT INTO chat VALUES (?,?,?,?)",
                    [(to_pt(r[0]), r[1] or "(human)", r[2], r[3]) for r in cache.execute(
                        "SELECT ts, speaker, speaker_type, content FROM chat "
                        "WHERE ts > ? AND ts <= ? ORDER BY ts", (lo, t))])
    out.executemany("INSERT INTO sessions VALUES (?,?,?,?,?)",
                    [(to_pt(r[0]),) + tuple(r[1:]) for r in cache.execute(
                        "SELECT ts, agent, session_id, short_goal, goal FROM sessions "
                        "WHERE ts > ? AND ts <= ? ORDER BY ts", (lo, t))])
    out.executemany("INSERT INTO turns VALUES (?,?,?,?,?,?,?)",
                    [(to_pt(r[0]),) + tuple(r[1:]) for r in traces.execute(
                        "SELECT created_at, agent, session_id, action, has_error, "
                        "substr(narration, 1, 600), substr(reasoning, 1, 1200) FROM traces "
                        "WHERE created_at > ? AND created_at <= ? ORDER BY created_at",
                        (lo, t))])
    # latest memory snapshot per agent at or before t
    for agent in w.roster:
        r = cache.execute("SELECT mem_rowid, ts FROM memory_index WHERE agent = ? AND ts <= ? "
                          "ORDER BY ts DESC LIMIT 1", (agent, t)).fetchone()
        if r:
            content = village.execute("SELECT content FROM agent_memories WHERE rowid = ?",
                                      (r["mem_rowid"],)).fetchone()[0]
            out.execute("INSERT INTO memories VALUES (?,?,?)", (to_pt(r["ts"]), agent, content))
    for g in cache.execute("SELECT goal, start_time, end_time FROM goals WHERE start_time <= ? "
                           "ORDER BY start_time", (t,)):
        end = g["end_time"] if g["end_time"] and g["end_time"] <= t else None
        out.execute("INSERT INTO village_goals VALUES (?,?,?)",
                    (to_pt(g["start_time"]), end and to_pt(end), g["goal"]))
    out.executescript("""
        CREATE INDEX ix_turns ON turns(agent, ts_pt);
        CREATE INDEX ix_chat ON chat(ts_pt);
    """)
    out.commit()
    out.close()
    return path


def freeze_id(w):
    return w.t.strftime("%Y%m%dT%H%M%SZ")


def frozen_db_path(w):
    return WORK / "frozen" / f"{freeze_id(w)}.db"
