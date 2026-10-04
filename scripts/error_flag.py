"""Supplement: how contaminated is the dataset's per-action `error` flag?

One pass over computer_use_turns.jsonl.gz: every flagged turn is classed as
`benign` (stderr from a command that evidently succeeded: git push/clone
progress, curl progress meters, warnings) or `failure` (everything else,
including all non-command tool errors). Writes work/error_classes.tsv
(turn_id, kind, class, first 200 chars of the error) for reuse.

The rules are deliberately simple and listed below; a random sample is
hand-checked in docs/supplement/ERROR_FLAG.md.

  uv run python scripts/error_flag.py /path/to/computer_use_turns.jsonl.gz
"""
import gzip
import json
import re
import sys
from collections import Counter
from pathlib import Path

BENIGN = re.compile(
    r"(\S+\s+->\s+\S+"               # git push/fetch ref updates: "main -> main"
    r"|Everything up-to-date"
    r"|% Total\s+% Received"          # curl progress meter
    r"|Cloning into|Switched to (a new )?branch|Already on|Your branch is up to date"
    r"|remote: (Counting|Compressing|Enumerating|Total|Resolving)"
    r"|^warning: |DeprecationWarning|npm (WARN|notice)"
    r"|Successfully (installed|built|tagged)"
    r"|^\s*\[notice\])", re.I | re.M)
FAILURE = re.compile(
    r"(fatal:|error:|Error:|ERROR|denied|not found|No such file|Traceback|failed|Failed"
    r"|Exception|refused|timed out|Timeout|cannot |Could not|unable to|Unable to|exit status [1-9])")


def classify(turn):
    err = turn.get("error")
    action = turn.get("agent_action") or {}
    if not err:
        return None, None
    if not action.get("command"):
        return "tool", "failure"          # GUI/tool errors are genuine failures
    text = str(err)
    if BENIGN.search(text) and not FAILURE.search(text):
        return "bash", "benign"
    return "bash", "failure"


def main(path):
    out = Path(__file__).resolve().parent.parent / "work" / "error_classes.tsv"
    out.parent.mkdir(exist_ok=True)
    counts = Counter()
    with gzip.open(path, "rt") as f, open(out, "w") as w:
        w.write("turn_id\tkind\tclass\terror_head\n")
        for line in f:
            t = json.loads(line)
            kind, cls = classify(t)
            if not cls:
                continue
            counts[(kind, cls)] += 1
            head = " ".join(str(t["error"]).split())[:200].replace("\t", " ")
            w.write(f"{t['id']}\t{kind}\t{cls}\t{head}\n")
    total = sum(counts.values())
    print(f"flagged turns: {total}")
    for k, v in sorted(counts.items()):
        print(f"  {k[0]:5s} {k[1]:8s} {v:7d}  ({v / total:.1%})")
    print(f"-> {out}")


if __name__ == "__main__":
    main(sys.argv[1])
