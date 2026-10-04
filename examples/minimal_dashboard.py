"""Template: SAGAT-test your own dashboard.

The harness freezes the swarm at a moment, builds a sealed snapshot of
everything up to that moment (an SQLite file), and calls your render()
on it. Whatever you return is exactly what the analyst sees; then the same
11 questions are asked and scored against what really happened.

    uv run python -m sagat show --name v2 20260824T163816Z --cond custom \
        --dashboard examples/minimal_dashboard.py      # preview what it shows
    uv run python -m sagat run  --name v2 --cond none,custom \
        --dashboard examples/minimal_dashboard.py \
        --model openrouter:deepseek/deepseek-v4-flash  # under $1 for 26 moments
    uv run python -m sagat score --name v2             # your board vs the rest

Snapshot tables (timestamps are Pacific-time strings, comparable as text):
  agents(name, model)
  chat(ts_pt, speaker, speaker_type, content)      speaker_type 'agent'/'user'
  sessions(ts_pt, agent, session_id, short_goal, goal)   latest row = current task
  turns(ts_pt, agent, session_id, action, has_error, narration, reasoning)
  memories(ts_pt, agent, content)                  each agent's latest memory
  village_goals(start_pt, end_pt, goal)

This example is the simplest dashboard people actually build: a chat
feed. Swap in your own; anything that returns text works (an image-based
dashboard would need the runner extended to send images).
"""
import sqlite3


def render(frozen_db_path, freeze_pt):
    con = sqlite3.connect(frozen_db_path)
    rows = con.execute("SELECT ts_pt, speaker, content FROM chat "
                       "ORDER BY ts_pt DESC LIMIT 40").fetchall()
    con.close()
    lines = [f"# Chat feed (latest 40 messages before {freeze_pt} PT)", ""]
    for ts, speaker, content in reversed(rows):
        lines.append(f"- {ts[11:16]} {speaker}: {' '.join((content or '').split())[:300]}")
    return "\n".join(lines)
