"""CLI.  uv run python -m sagat <command> ...

  build-data --raw DIR --out DIR     raw HF export -> village.db + traces.db (once)
  prep                               build work/source_cache.db (once per data snapshot)
  freezes --name v1 --n 24 [--months 2025-09:2026-09] [--seed 0] [--exclude v1]
                                     sample freeze points, build frozen dbs + query bank
  freezes --name v1 --times results/freeze_times_v1.txt
                                     rebuild exactly the published moments
  show --name v1 FREEZE_ID [--cond dashboard]
                                     print exactly what an analyst sees (no answers)
  run --name v1 --model claude-opus-5-5 --cond none,dashboard,raw [--limit N]
      (or --model openrouter:<provider/model>, e.g. openrouter:deepseek/deepseek-v4-flash)
      [--workers 4] [--effort medium]
      --cond custom --dashboard my_board.py   test YOUR dashboard (see examples/)
  score --name v1                    write results/summary_v1.md
  explorer [--public]                self-contained HTML explorer (full -> work/, public -> docs/)
  figures                            static SVG figures for the write-up (docs/fig_*.svg)
  export                             every answer/truth/score as CSV, no dataset text (results/public/)
  example --name v2 --freeze ID      the write-up's worked example, generated from the records
  plant --from v2 --name X [--real]  planted-misreport test set (see sagat/plant.py)
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import analyst, build_data, example, explorer, export, figures, freeze, plant, prep, queries, score
from .config import RESULTS, to_pt


def month_range(spec):
    a, b = spec.split(":")
    y, m = map(int, a.split("-"))
    out = []
    while f"{y:04d}-{m:02d}" <= b:
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def cmd_freezes(args):
    RESULTS.mkdir(exist_ok=True)
    exclude = []
    if args.exclude:
        from datetime import datetime
        exclude = [datetime.fromisoformat(it["t_utc"]) for it in score.load_set(args.exclude)]
    if args.times:
        # exact moments from a published times file: independent of how the
        # local traces.db was built (sampling uses row positions)
        from datetime import datetime
        lines = [l.strip() for l in open(args.times) if l.strip()]
        for l in lines:
            if l.startswith("# seed="):
                args.seed = int(l.split("=", 1)[1])   # questions need the set's seed
        times = [datetime.fromisoformat(l) for l in lines if not l.startswith("#")]
        ws = [freeze.load_window(t) for t in times]
    else:
        ws = freeze.sample_freezes(args.n, month_range(args.months), seed=args.seed,
                                   exclude=exclude)
    path = RESULTS / f"freezes_{args.name}.jsonl"
    with open(path, "w") as f:
        for w in ws:
            focal, qs = queries.build_queries(w, seed=args.seed)
            db = freeze.build_frozen_db(w, freeze.frozen_db_path(w))
            item = {"id": freeze.freeze_id(w), "t_utc": w.t.isoformat(), "t_pt": to_pt(w.t),
                    "roster": w.roster, "focal": focal, "frozen_db": str(db),
                    "queries": [q.to_dict() for q in qs]}
            f.write(json.dumps(item) + "\n")
            print(f"{item['id']}  {item['t_pt']} PT  roster={len(w.roster):2d}  "
                  f"focal={focal}  queries={len(qs)}")
    times_path = RESULTS / f"freeze_times_{args.name}.txt"
    times_path.write_text(f"# seed={args.seed}\n" + "".join(w.t.isoformat() + "\n" for w in ws))
    print(f"{len(ws)} freezes -> {path} (times: {times_path.name})")


def _custom(args, conds):
    """Swap 'custom' for the registered name of the --dashboard file."""
    if "custom" not in conds:
        return conds
    if not args.dashboard:
        sys.exit("--cond custom needs --dashboard path/to/your_dashboard.py")
    name = analyst.load_custom(args.dashboard)
    return [name if c == "custom" else c for c in conds]


def cmd_show(args):
    item = next(it for it in score.load_set(args.name) if it["id"] == args.freeze)
    cond = _custom(args, [args.cond])[0]
    print(analyst.user_message(item, cond))


def cmd_run(args):
    items = score.load_set(args.name)[: args.limit or None]
    conds = _custom(args, args.cond.split(","))
    bad = [c for c in conds if c not in analyst.CONDITIONS and not c.startswith("custom-")]
    if bad:
        sys.exit(f"unknown condition(s): {bad}")
    client = analyst.make_client(args.model)
    model_dir = args.model.replace("/", "__").replace(":", "_")
    jobs = []
    for cond in conds:
        for it in items:
            out = RESULTS / "runs" / args.name / model_dir / cond / f"{it['id']}.json"
            if out.exists() and not args.force:
                continue
            jobs.append((cond, it, out))
    print(f"{len(jobs)} runs to do ({args.model}, effort={args.effort})")
    total = 0.0
    with ThreadPoolExecutor(args.workers) as ex:
        futs = {ex.submit(analyst.run_one, client, args.model, c, it, args.effort): (c, it, o)
                for c, it, o in jobs}
        for fut in as_completed(futs):
            cond, it, out = futs[fut]
            try:
                r = fut.result()
            except Exception as e:  # keep the batch going; the failed run is retried next time
                print(f"  FAIL {cond} {it['id']}: {type(e).__name__}: {e}")
                continue
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(r, indent=1))
            total += r["cost_usd"]
            print(f"  {cond:9s} {it['id']}  stop={r['stop_reason']:8s} "
                  f"req={r['n_requests']:2d} sql={len(r['sql_queries']):2d} "
                  f"${r['cost_usd']:.3f}  (running ${total:.2f})"
                  + ("" if r["answers"] else "  NO ANSWERS"))
    print(f"done, ${total:.2f}")


def main():
    p = argparse.ArgumentParser(prog="sagat")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prep")
    f = sub.add_parser("freezes")
    f.add_argument("--name", required=True)
    f.add_argument("--n", type=int, default=24)
    f.add_argument("--months", default="2025-09:2026-09")
    f.add_argument("--seed", type=int, default=0)
    f.add_argument("--exclude", help="another freeze set; keep >= 24h away from its freezes")
    f.add_argument("--times", help="rebuild exact moments from a freeze_times_*.txt file")
    b = sub.add_parser("build-data")
    b.add_argument("--raw", required=True, help="folder with the HF export's .jsonl.gz files")
    b.add_argument("--out", required=True, help="folder to write village.db and traces.db")
    s = sub.add_parser("show")
    s.add_argument("--name", required=True)
    s.add_argument("freeze")
    s.add_argument("--cond", default="dashboard")
    s.add_argument("--dashboard", help="your render(frozen_db_path, freeze_pt) file, with --cond custom")
    r = sub.add_parser("run")
    r.add_argument("--name", required=True)
    r.add_argument("--model", default="claude-opus-5-5")
    r.add_argument("--cond", default="none,dashboard,raw")
    r.add_argument("--effort", default="medium")
    r.add_argument("--limit", type=int, default=0)
    r.add_argument("--workers", type=int, default=4)
    r.add_argument("--force", action="store_true")
    r.add_argument("--dashboard", help="your render(frozen_db_path, freeze_pt) file, with --cond custom")
    sc = sub.add_parser("score")
    sc.add_argument("--name", required=True)
    sub.add_parser("figures")
    sub.add_parser("export")
    pl = sub.add_parser("plant")
    pl.add_argument("--from", dest="src", required=True)
    pl.add_argument("--name", required=True)
    pl.add_argument("--seed", type=int, default=0)
    pl.add_argument("--real", action="store_true", help="v3 design: agents' own real messages, nothing inserted")
    eg = sub.add_parser("example")
    eg.add_argument("--name", required=True)
    eg.add_argument("--freeze", required=True)
    ex = sub.add_parser("explorer")
    ex.add_argument("--public", action="store_true",
                    help="strip all dataset text (safe to share publicly)")
    a = p.parse_args()
    if a.cmd == "prep":
        prep.build()
    elif a.cmd == "freezes":
        cmd_freezes(a)
    elif a.cmd == "show":
        cmd_show(a)
    elif a.cmd == "run":
        cmd_run(a)
    elif a.cmd == "score":
        print(score.report(a.name))
    elif a.cmd == "build-data":
        build_data.build(a.raw, a.out)
    elif a.cmd == "example":
        print(example.build(a.name, a.freeze))
    elif a.cmd == "plant":
        (plant.build_real if a.real else plant.build)(a.src, a.name, a.seed)
    elif a.cmd == "export":
        export.build()
    elif a.cmd == "figures":
        figures.build()
    elif a.cmd == "explorer":
        explorer.build(public=a.public)


if __name__ == "__main__":
    main()
