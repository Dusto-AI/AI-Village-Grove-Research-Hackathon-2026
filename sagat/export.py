"""Export every answer, true answer and score as CSV, with no dataset text.

  uv run python -m sagat export        # -> results/public/answers.csv, runs.csv

Same content policy as docs/explorer_public.html: agent names, answers,
truths and scores are included; what the analysts were shown (prompts),
multiple-choice option wording and SQL queries are not. Lets anyone without
dataset access or a model budget re-check the statistics
(scripts/rescore_public.py does exactly that).
"""
import csv
import json

from . import score
from .config import RESULTS

SETS = ["v1", "v2", "v2r2", "v2r3", "v2plant2", "v2plant3"]


def _cell(v):
    return json.dumps(v) if isinstance(v, (list, dict, bool)) or v is None else v


def build():
    out = RESULTS / "public"
    out.mkdir(parents=True, exist_ok=True)
    n_ans = n_runs = 0
    with open(out / "answers.csv", "w", newline="") as fa, open(out / "runs.csv", "w", newline="") as fr:
        wa, wr = csv.writer(fa), csv.writer(fr)
        wa.writerow(["set", "moment_id", "moment_pt", "n_agents", "focal_agent", "question", "level",
                     "kind", "true_answer", "rule_answer", "rule_score", "model", "condition",
                     "answered", "answer", "score"])
        wr.writerow(["set", "moment_id", "model", "condition", "answered", "stop_reason",
                     "n_requests", "n_sql_queries", "cost_usd"])
        for name in SETS:
            if not (RESULTS / f"freezes_{name}.jsonl").exists():
                continue
            items = {it["id"]: it for it in score.load_set(name)}
            for r in score.load_runs(name):
                it = items.get(r["freeze"])
                if not it:
                    continue
                wr.writerow([name, r["freeze"], r["model"], r["condition"], r["answers"] is not None,
                             r["stop_reason"], r["n_requests"], len(r["sql_queries"]), r["cost_usd"]])
                n_runs += 1
                for q in it["queries"]:
                    a = (r["answers"] or {}).get(q["id"])
                    wa.writerow([name, it["id"], it["t_pt"], len(it["roster"]), it["focal"], q["id"],
                                 q["level"], q["kind"], _cell(q["truth"]), _cell(q["heuristic"]),
                                 score.score(q, q["heuristic"]), r["model"], r["condition"],
                                 r["answers"] is not None, _cell(a),
                                 score.score(q, a) if r["answers"] is not None else ""])
                    n_ans += 1
    print(f"{n_ans} answer rows, {n_runs} runs -> {out}/answers.csv, runs.csv")
