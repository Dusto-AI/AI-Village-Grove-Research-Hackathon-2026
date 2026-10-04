"""Build the two source databases the harness reads, straight from the raw AI
Village export (huggingface.co/datasets/aidigestorg/ai-village, gated).

  uv run python -m sagat build-data --raw /path/to/hf/files --out /path/to/dbs

Writes <out>/village.db (agents, chat_messages, computer_use_sessions,
village_goals, agent_memories: one TEXT column per JSON field, as the
original workspace tooling does) and <out>/traces.db (one row per computer-use
turn with reasoning/narration flattened out of the provider-shaped
agent_messages). Then point VILLAGE_DB / TRACES_DB at them.

Only the files below are needed (about 5 GB compressed); screenshots are not.
The extraction functions are copied from the original workspace tooling
(villagelib.py / build_traces.py), so a build from the same export revision
yields the same rows.
"""
import gzip
import json
import sqlite3
import time
from pathlib import Path

NEEDED = ["agents.jsonl.gz", "chat_messages.jsonl.gz", "computer_use_sessions.jsonl.gz",
          "village_goals.jsonl.gz", "agent_memories.jsonl.gz", "computer_use_turns.jsonl.gz"]


def iter_jsonl(path):
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def load_table(con, name, path, batch_size=5000):
    """jsonl(.gz) -> table; columns from the first record, all TEXT,
    nested values JSON-encoded."""
    it = iter_jsonl(path)
    first = next(it)
    cols = list(first.keys())
    con.execute(f"DROP TABLE IF EXISTS {name}")
    con.execute(f"CREATE TABLE {name} ({', '.join(c + ' TEXT' for c in cols)})")
    sql = f"INSERT INTO {name} VALUES ({', '.join('?' for _ in cols)})"

    def encode(rec):
        return [json.dumps(v) if isinstance(v, (dict, list)) else v
                for v in (rec.get(c) for c in cols)]

    batch, n = [encode(first)], 1
    for rec in it:
        batch.append(encode(rec))
        n += 1
        if len(batch) >= batch_size:
            con.executemany(sql, batch)
            batch = []
    if batch:
        con.executemany(sql, batch)
    con.commit()
    return n


# --- agent_messages is provider-shaped (copied from villagelib.py) ---------
#   anthropic  content[] {type: thinking, thinking}
#   openai     [] {type: reasoning, summary[]{text}}
#   google     candidates[].content.parts[] {thought}
#   other      reasoning_content / reasoning / reasoning_details / thinkingMessage

def extract_reasoning(am):
    texts = []
    if am is None:
        return texts
    if isinstance(am, list):
        for item in am:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "reasoning":
                for s in item.get("summary") or []:
                    if isinstance(s, dict) and s.get("text"):
                        texts.append(s["text"])
                for s in item.get("content") or []:
                    if isinstance(s, dict) and s.get("type", "").startswith("reasoning") \
                            and s.get("text"):
                        texts.append(s["text"])
        return texts
    if not isinstance(am, dict):
        return texts
    if isinstance(am.get("content"), list):
        for block in am["content"]:
            if isinstance(block, dict) and block.get("type") == "thinking" \
                    and block.get("thinking"):
                texts.append(block["thinking"])
        if texts or am.get("model", "").startswith("claude"):
            return texts
    if "candidates" in am:
        for cand in am.get("candidates") or []:
            for p in (((cand or {}).get("content") or {}).get("parts")) or []:
                if isinstance(p, dict) and p.get("thought") and p.get("text"):
                    texts.append(p["text"])
        return texts
    for k in ("reasoning_content", "reasoning"):
        v = am.get(k)
        if isinstance(v, str) and v.strip():
            texts.append(v)
    for rd in am.get("reasoning_details") or []:
        if isinstance(rd, dict) and rd.get("text"):
            texts.append(rd["text"])
    tm = am.get("thinkingMessage")
    if isinstance(tm, dict):
        for block in ((tm.get("message") or {}).get("content")) or []:
            if isinstance(block, dict) and block.get("thinking"):
                texts.append(block["thinking"])
    return texts


def extract_narration(am):
    out = []
    if isinstance(am, list):
        for item in am:
            if isinstance(item, dict) and item.get("type") == "message":
                for c in item.get("content") or []:
                    if isinstance(c, dict) and c.get("type") == "output_text" \
                            and c.get("text"):
                        out.append(c["text"])
        return out
    if not isinstance(am, dict):
        return out
    if isinstance(am.get("content"), list):
        for b in am["content"]:
            if isinstance(b, dict) and b.get("type") == "text" and b.get("text"):
                out.append(b["text"])
    elif isinstance(am.get("content"), str) and am["content"].strip():
        out.append(am["content"])
    for cand in am.get("candidates") or []:
        for p in (((cand or {}).get("content") or {}).get("parts")) or []:
            if isinstance(p, dict) and p.get("text") and not p.get("thought"):
                out.append(p["text"])
    return out


def action_verb(a):
    if not isinstance(a, dict):
        return None
    if a.get("action"):
        return str(a["action"])
    if a.get("command"):
        return "bash:" + str(a["command"]).strip().split()[0][:24]
    return None


def build(raw, out):
    raw, out = Path(raw), Path(out)
    missing = [f for f in NEEDED if not (raw / f).exists()]
    if missing:
        raise SystemExit(f"missing in {raw}: {missing}")
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    vpath = out / "village.db"
    if vpath.exists():
        vpath.unlink()
    con = sqlite3.connect(vpath)
    for stem in ("agents", "chat_messages", "computer_use_sessions", "village_goals",
                 "agent_memories"):
        n = load_table(con, stem, raw / f"{stem}.jsonl.gz")
        print(f"  {stem}: {n} rows ({time.time() - t0:.0f}s)")
    con.close()

    tpath = out / "traces.db"
    if tpath.exists():
        tpath.unlink()
    names = {a["id"]: a["name"] for a in iter_jsonl(raw / "agents.jsonl.gz")}
    sess_agent = {s["id"]: s["agent_id"]
                  for s in iter_jsonl(raw / "computer_use_sessions.jsonl.gz")}
    con = sqlite3.connect(tpath)
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    con.execute("""CREATE TABLE traces (
        turn_id TEXT PRIMARY KEY, session_id TEXT, agent TEXT, created_at TEXT,
        day TEXT, month TEXT, reasoning TEXT, narration TEXT, action TEXT,
        has_error INTEGER)""")
    sql = "INSERT OR REPLACE INTO traces VALUES (?,?,?,?,?,?,?,?,?,?)"
    batch, n = [], 0
    for t in iter_jsonl(raw / "computer_use_turns.jsonl.gz"):
        am = t.get("agent_messages")
        created = t.get("created_at") or ""
        batch.append((t["id"], t.get("session_id"),
                      names.get(sess_agent.get(t.get("session_id"))), created,
                      created[:10], created[:7],
                      "\n".join(extract_reasoning(am)) or None,
                      "\n".join(extract_narration(am)) or None,
                      action_verb(t.get("agent_action")), 1 if t.get("error") else 0))
        n += 1
        if len(batch) >= 2000:
            con.executemany(sql, batch)
            batch = []
    if batch:
        con.executemany(sql, batch)
    con.execute("CREATE INDEX ix_traces_created ON traces(created_at)")
    con.execute("CREATE INDEX ix_traces_month ON traces(month)")
    con.commit()
    con.close()
    print(f"  traces: {n} turns ({time.time() - t0:.0f}s)")
    print(f"done -> {vpath} and {tpath}\n"
          f"next: export VILLAGE_DB={vpath} TRACES_DB={tpath}")
