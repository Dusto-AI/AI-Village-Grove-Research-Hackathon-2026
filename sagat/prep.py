"""One-time cache of the small, frequently-sliced tables, with time indexes.

The source dbs are opened read-only and never modified. village.db carries no
indexes, so slicing it per freeze point would rescan millions of rows; this
copies chat, sessions, goals and agents (plus a content-free index of memory
snapshots) into work/source_cache.db once.
"""
import sqlite3
import time

from .config import CACHE_DB, VILLAGE_DB, WORK


def ro(path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def build():
    WORK.mkdir(parents=True, exist_ok=True)
    if CACHE_DB.exists():
        CACHE_DB.unlink()
    t0 = time.time()
    con = sqlite3.connect(f"file:{CACHE_DB}", uri=True)  # uri=True so ATTACH accepts ?mode=ro
    con.execute("ATTACH ? AS v", (f"file:{VILLAGE_DB}?mode=ro",))
    con.executescript("""
        CREATE TABLE agents AS
          SELECT id, name, model_string AS model, created_at FROM v.agents;
        CREATE TABLE chat AS
          SELECT c.created_at AS ts, c.speaker_type, a.name AS speaker,
                 c.room_id AS room, c.content
          FROM v.chat_messages c LEFT JOIN agents a ON a.id = c.agent_speaker_id;
        CREATE INDEX ix_chat_ts ON chat(ts);
        CREATE TABLE sessions AS
          SELECT s.created_at AS ts, s.id AS session_id, a.name AS agent,
                 s.short_displayed_session_goal AS short_goal,
                 s.session_goal AS goal
          FROM v.computer_use_sessions s JOIN agents a ON a.id = s.agent_id;
        CREATE INDEX ix_sessions_ts ON sessions(ts);
        CREATE INDEX ix_sessions_agent ON sessions(agent, ts);
        CREATE TABLE goals AS
          SELECT goal, start_time, end_time FROM v.village_goals;
        CREATE TABLE memory_index AS
          SELECT m.rowid AS mem_rowid, a.name AS agent, m.created_at AS ts,
                 length(m.content) AS n_chars
          FROM v.agent_memories m JOIN agents a ON a.id = m.agent_id;
        CREATE INDEX ix_mem ON memory_index(agent, ts);
    """)
    con.commit()
    counts = {t: con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
              for t in ("agents", "chat", "sessions", "goals", "memory_index")}
    con.close()
    print(f"cache built in {time.time() - t0:.0f}s -> {CACHE_DB}: {counts}")
