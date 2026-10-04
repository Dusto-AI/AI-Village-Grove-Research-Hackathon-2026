"""Build a self-contained, offline HTML explorer of every run.

  uv run python -m sagat explorer                # full: includes what analysts saw
  uv run python -m sagat explorer --public       # no dataset text (see below)

All numbers are computed here by the same scoring code as results/summary_*.md
(score.py), then embedded as JSON; the page only renders them, so the page
and the summary tables cannot disagree.

Full mode embeds the exact prompt each analyst saw (dashboard text, memory
excerpts, chat lines): AI Village dataset content under its research-only
licence. It writes to work/ (gitignored). --public strips every piece of
dataset text (prompts, multiple-choice option texts, SQL queries, which can
quote data) and keeps answers, truths, scores and agent names; it writes to
docs/explorer_public.html.
"""
import json
from collections import defaultdict
from datetime import datetime, timezone

from . import analyst, score
from .config import REPO, RESULTS, WORK

MODEL_NAMES = {
    "openrouter:deepseek/deepseek-v4-flash": "DeepSeek V4 Flash (cheap)",
    "openrouter:anthropic/claude-sonnet-5.5": "Claude Sonnet 5.5 (strong)",
}
COND_NAMES = {
    "none": "Guessing (roster only)",
    "dashboard": "Dashboard",
    "raw": "Raw records (SQL)",
    "both": "Dashboard + SQL",
    "self": "Agent's own view",
    "dashboard2": "Dashboard + who-talks-to-whom + patterns",
    "dashboard3": "… + agents' stated plans",
    "custom-minimal_dashboard": "Chat feed only (template example)",
}
SET_NAMES = {"v1": "First 26 moments (design set)",
             "v2": "Fresh 26 moments (held-out test)"}
QUESTION_SHORT = {
    "active_now": "Who acted in last 30 min", "focal_task": "What is X working on",
    "chattiest": "Chattiest in last hour", "human_recent": "Human posted in last 2h",
    "most_struggling": "Most error output (see Entry 14)", "focal_partner": "Who X talks to most",
    "gone_quiet": "Who has gone quiet", "active_later": "Who works 90-120 min later",
    "next_speaker": "Who speaks next", "focal_chat_next": "Will X post in 30 min",
    "human_next": "Will a human post in 2h",
}
RULE = "heuristic (persistence)"


def _label_parts(label):
    if label == RULE:
        return None, "rule"
    m, c = label.split(" · ")
    return m, c


def _set_payload(name, public):
    items, rows, costs, qmeta, missing = score.table(name)
    runs_raw = score.load_runs(name)
    freezes = []
    for it in items.values():
        qs = []
        for q in it["queries"]:
            q = dict(q)
            if public and q["kind"] == "mc":
                q["options"] = [f"(option {l}: text hidden in public build)"
                                for l in "ABCD"[:len(q["options"])]]
            qs.append(q)
        freezes.append({"id": it["id"], "t_pt": it["t_pt"], "roster": it["roster"],
                        "focal": it["focal"], "queries": qs})
    cond_order = list(COND_NAMES)
    model_order = list(MODEL_NAMES)
    def order(k):
        if k == RULE:
            return (0, 0, 0)
        m, c = _label_parts(k)
        return (1, cond_order.index(c) if c in cond_order else 99,
                model_order.index(m) if m in model_order else 99)
    labels = sorted(rows, key=order)
    views = []
    for lab in labels:
        m, c = _label_parts(lab)
        lv = score.per_level(rows[lab], qmeta)
        views.append({
            "key": lab, "model": m, "cond": c,
            "name": "“Nothing changes” rule" if c == "rule"
                    else f"{COND_NAMES.get(c, c)} · {MODEL_NAMES.get(m, m)}",
            "n": len(rows[lab]), "no_answer": missing.get(lab, 0),
            "cost": (sum(costs[lab]) / len(costs[lab])) if costs.get(lab) else None,
            "levels": {k: v[0] for k, v in lv.items()},
            "ci": {k: v[1] for k, v in lv.items()},
            "per_q": {q: [s for s in (fs.get(q) for fs in rows[lab].values()) if s is not None]
                      for q in qmeta},
            "scores": {f: qs for f, qs in rows[lab].items()},
        })
    # paired comparisons: per-freeze differences, so the page can show every dot
    pairs = []
    for a, b in _pairs(labels, rows):
        entry = {"a": a, "b": b, "levels": {}}
        for lv in ("L1", "L2", "L3", "all"):
            la = score.per_freeze_level(rows[a], qmeta, lv)
            lb = score.per_freeze_level(rows[b], qmeta, lv)
            common = sorted(set(la) & set(lb))
            d = {f: la[f] - lb[f] for f in common}
            r = score.paired(rows, qmeta, a, b, lv)
            entry["levels"][lv] = {"diffs": d, "mean": r[0] if r else None,
                                   "ci": r[1] if r else None}
        pairs.append(entry)
    # forecast error direction on the two yes/no projection questions
    direction = []
    truth = {(it["id"], q["id"]): q["truth"] for it in items.values() for q in it["queries"]}
    for lab in labels:
        m, c = _label_parts(lab)
        if c == "rule":
            continue
        fn = fp = n = 0
        for r in runs_raw:
            if f"{r['model']} · {r['condition']}" != lab or not r["answers"]:
                continue
            for qid in ("focal_chat_next", "human_next"):
                t = truth.get((r["freeze"], qid))
                if t is None:
                    continue
                a = r["answers"].get(qid)
                n += 1
                fn += t is True and a is not True
                fp += t is False and a is True
        direction.append({"key": lab, "wrong_no": fn, "wrong_yes": fp, "n": n})
    runs = []
    for r in runs_raw:
        runs.append({
            "key": f"{r['model']} · {r['condition']}", "freeze": r["freeze"],
            "answers": r["answers"], "cost": r["cost_usd"], "requests": r["n_requests"],
            "stop": r["stop_reason"], "served_by": r.get("served_by"),
            "sql": [] if public else r["sql_queries"], "n_sql": len(r["sql_queries"]),
        })
    prompts = {}
    if not public:
        conds = sorted({r["condition"] for r in runs_raw})
        full_items = {x["id"]: x for x in score.load_set(name)}
        for it in items.values():
            full = full_items[it["id"]]
            for c in conds:
                if c.startswith("custom-") and c not in analyst.CUSTOM:
                    continue          # plug-in dashboard not loaded in this build
                prompts[f"{c}|{it['id']}"] = analyst.user_message(full, c)
        prompts["__system__"] = analyst.SYSTEM
        prompts["__sql_tool__"] = analyst.SQL_TOOL["description"]
    return {"name": name, "title": SET_NAMES.get(name, name), "freezes": freezes,
            "views": views, "pairs": pairs, "direction": direction, "runs": runs,
            "prompts": prompts, "qmeta": qmeta}


def _pairs(labels, rows):
    out = []
    models = sorted({_label_parts(l)[0] for l in labels if l != RULE})
    for m in models:
        has = lambda c: f"{m} · {c}" in rows  # noqa: E731
        for c in ("dashboard", "dashboard2", "dashboard3", "raw", "self"):
            if has(c):
                out.append((f"{m} · {c}", RULE))
                if has("none"):
                    out.append((f"{m} · {c}", f"{m} · none"))
        for a, b in (("raw", "dashboard"), ("dashboard2", "dashboard"),
                     ("dashboard3", "dashboard2")):
            if has(a) and has(b):
                out.append((f"{m} · {a}", f"{m} · {b}"))
    # cross-model on the same view
    for c in ("dashboard", "self", "none"):
        ks = [f"{m} · {c}" for m in models if f"{m} · {c}" in rows]
        if len(ks) == 2:
            out.append((ks[1], ks[0]))
    return out


def build(public=False, sets=("v1", "v2")):
    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "public": public,
        "questions": QUESTION_SHORT,
        "sets": [_set_payload(s, public) for s in sets
                 if (RESULTS / f"freezes_{s}.jsonl").exists()],
    }
    data = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    html = TEMPLATE.replace("/*__DATA__*/", data)
    out = (REPO / "docs" / "explorer_public.html") if public else (WORK / "explorer.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB)")
    return out


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Swarm SAGAT Explorer</title>
<style>
:root {
  color-scheme: light;
  --page: #f9f9f7; --surface: #fcfcfb; --surface-2: #f3f2ee;
  --ink: #0b0b0b; --ink-2: #52514e; --muted: #898781;
  --grid: #e1e0d9; --axis: #c3c2b7; --ring: rgba(11,11,11,0.10);
  --accent: #2a78d6; --accent-soft: #cde2fb;
  --neg: #2a78d6; --pos: #e34948;
  --good: #0ca30c; --good-text: #006300; --bad: #d03b3b;
  --rule: #eb6834;
  --seq-0: #f0efec; --seq-1: #cde2fb; --seq-2: #9ec5f4; --seq-3: #6da7ec;
  --seq-4: #3987e5; --seq-5: #256abf; --seq-6: #184f95; --seq-7: #0d366b;
  --si-0: #0b0b0b; --si-1: #0b0b0b; --si-2: #0b0b0b; --si-3: #0b0b0b;
  --si-4: #ffffff; --si-5: #ffffff; --si-6: #ffffff; --si-7: #ffffff;
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) {
    color-scheme: dark;
    --page: #0d0d0d; --surface: #1a1a19; --surface-2: #242422;
    --ink: #ffffff; --ink-2: #c3c2b7; --muted: #898781;
    --grid: #2c2c2a; --axis: #383835; --ring: rgba(255,255,255,0.10);
    --accent: #3987e5; --accent-soft: #184f95;
    --neg: #3987e5; --pos: #e66767;
    --good: #0ca30c; --good-text: #0ca30c; --bad: #e66767;
    --rule: #d95926;
    --seq-0: #383835; --seq-1: #104281; --seq-2: #184f95; --seq-3: #1c5cab;
    --seq-4: #256abf; --seq-5: #3987e5; --seq-6: #6da7ec; --seq-7: #9ec5f4;
    --si-0: #ffffff; --si-1: #ffffff; --si-2: #ffffff; --si-3: #ffffff;
    --si-4: #ffffff; --si-5: #0b0b0b; --si-6: #0b0b0b; --si-7: #0b0b0b;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --page: #0d0d0d; --surface: #1a1a19; --surface-2: #242422;
  --ink: #ffffff; --ink-2: #c3c2b7; --muted: #898781;
  --grid: #2c2c2a; --axis: #383835; --ring: rgba(255,255,255,0.10);
  --accent: #3987e5; --accent-soft: #184f95;
  --neg: #3987e5; --pos: #e66767;
  --good: #0ca30c; --good-text: #0ca30c; --bad: #e66767;
  --rule: #d95926;
  --seq-0: #383835; --seq-1: #104281; --seq-2: #184f95; --seq-3: #1c5cab;
  --seq-4: #256abf; --seq-5: #3987e5; --seq-6: #6da7ec; --seq-7: #9ec5f4;
  --si-0: #ffffff; --si-1: #ffffff; --si-2: #ffffff; --si-3: #ffffff;
  --si-4: #ffffff; --si-5: #0b0b0b; --si-6: #0b0b0b; --si-7: #0b0b0b;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--page); color: var(--ink);
  font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
header { padding: 20px 24px 0; max-width: 1200px; margin: 0 auto; }
h1 { font-size: 22px; margin: 0 0 4px; font-weight: 650; }
h2 { font-size: 17px; margin: 0 0 4px; font-weight: 600; }
h3 { font-size: 15px; margin: 16px 0 6px; font-weight: 600; }
p { margin: 6px 0; }
.sub { color: var(--ink-2); max-width: 820px; }
.small { font-size: 13px; color: var(--ink-2); }
main { max-width: 1200px; margin: 0 auto; padding: 12px 24px 48px; }
nav { display: flex; gap: 4px; flex-wrap: wrap; margin: 14px 0 0;
  border-bottom: 1px solid var(--grid); }
nav button { background: none; border: 0; padding: 8px 12px; font: inherit; color: var(--ink-2);
  border-bottom: 2px solid transparent; cursor: pointer; }
nav button[aria-selected="true"] { color: var(--ink); border-bottom-color: var(--accent); font-weight: 600; }
.controls { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; margin: 14px 0; }
select, input[type=search] { font: inherit; padding: 5px 8px; border-radius: 6px;
  border: 1px solid var(--axis); background: var(--surface); color: var(--ink); max-width: 100%; }
.card { background: var(--surface); border: 1px solid var(--ring); border-radius: 10px;
  padding: 16px; margin: 14px 0; overflow-x: auto; }
.card .lede { color: var(--ink-2); margin-bottom: 10px; max-width: 900px; }
svg text { fill: var(--ink-2); font: 12px system-ui, -apple-system, "Segoe UI", sans-serif; }
svg .ink { fill: var(--ink); }
svg .muted { fill: var(--muted); }
table { border-collapse: collapse; font-size: 13px; width: 100%; }
th, td { padding: 5px 8px; border-bottom: 1px solid var(--grid); text-align: left; vertical-align: top; }
th { color: var(--ink-2); font-weight: 600; position: sticky; top: 0; background: var(--surface); }
td.num { font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; }
td.qcol { min-width: 280px; max-width: 360px; }
td.acol, td.ans { min-width: 130px; }
.ok { color: var(--good-text); } .no { color: var(--bad); }
.pill { display: inline-block; padding: 0 6px; border-radius: 99px; background: var(--surface-2);
  color: var(--ink-2); font-size: 12px; margin-left: 4px; }
pre { white-space: pre-wrap; word-break: break-word; background: var(--surface-2); padding: 12px;
  border-radius: 8px; font: 12px/1.45 ui-monospace, SFMono-Regular, Menlo, monospace;
  max-height: 520px; overflow: auto; margin: 6px 0; }
.two { display: grid; grid-template-columns: 300px minmax(0, 1fr); gap: 16px; }
.two > * { min-width: 0; }
.list { max-height: 640px; overflow: auto; border: 1px solid var(--ring); border-radius: 8px; }
.list button { display: block; width: 100%; text-align: left; border: 0; background: none; font: inherit;
  padding: 6px 10px; border-bottom: 1px solid var(--grid); color: var(--ink); cursor: pointer; }
.list button[aria-current="true"] { background: var(--accent-soft); }
.list button .small { display: block; }
.boardtable { font-size: 12px; }
.boardtable th, .boardtable td { padding: 3px 6px; white-space: nowrap; }
.board h3, .board h4 { font-size: 14px; }
.legend { display: flex; gap: 16px; flex-wrap: wrap; font-size: 13px; color: var(--ink-2); margin: 6px 0; }
.key { display: inline-block; width: 12px; height: 12px; border-radius: 3px; vertical-align: -1px; margin-right: 5px; }
.keyline { display: inline-block; width: 14px; height: 0; border-top: 2px solid; vertical-align: 3px; margin-right: 5px; }
#tip { position: fixed; pointer-events: none; background: var(--surface); color: var(--ink);
  border: 1px solid var(--ring); box-shadow: 0 4px 16px rgba(0,0,0,.15); border-radius: 8px;
  padding: 8px 10px; font-size: 13px; max-width: 320px; display: none; z-index: 10; }
#tip strong { font-weight: 650; }
.theme { margin-left: auto; }
.banner { background: var(--surface-2); border-radius: 8px; padding: 8px 12px; margin: 10px 0;
  color: var(--ink-2); font-size: 13px; }
@media (max-width: 760px) {
  header, main { padding-left: 16px; padding-right: 16px; }
  .two { grid-template-columns: minmax(0, 1fr); }
  .list { max-height: 260px; }
}
</style>
</head>
<body>
<header>
  <div class="controls" style="margin:0">
    <div>
      <h1>Swarm SAGAT Explorer</h1>
      <p class="sub">Every frozen moment, every question, every answer. Freeze an AI swarm (the AI
      Village) at a random moment, show an AI analyst a view of it, ask 11 situation-awareness
      questions, and score the answers against what really happened. Use this page to check any
      claim in the notebook for yourself.</p>
    </div>
    <button class="theme" id="theme" type="button" aria-label="Toggle light or dark theme">◐ Theme</button>
  </div>
  <nav role="tablist" id="tabs"></nav>
</header>
<main>
  <div class="controls">
    <label>Moment set <select id="set"></select></label>
    <span class="small" id="setnote"></span>
  </div>
  <div id="publicnote"></div>
  <section id="tab-results"></section>
  <section id="tab-moments" hidden></section>
  <section id="tab-questions" hidden></section>
  <section id="tab-try" hidden></section>
  <section id="tab-method" hidden></section>
</main>
<div id="tip" role="tooltip"></div>
<script id="data" type="application/json">/*__DATA__*/</script>
<script>
"use strict";
const D = JSON.parse(document.getElementById("data").textContent);
const $ = (s, r = document) => r.querySelector(s);
const el = (tag, attrs = {}, ...kids) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "text") n.textContent = v; else if (k === "on") for (const [e, f] of Object.entries(v)) n.addEventListener(e, f);
    else if (v !== null && v !== undefined && v !== false) n.setAttribute(k, v);
  }
  for (const k of kids.flat()) if (k !== null && k !== undefined) n.append(k.nodeType ? k : document.createTextNode(String(k)));
  return n;
};
const NS = "http://www.w3.org/2000/svg";
const sv = (tag, attrs = {}, text) => {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  if (text !== undefined) n.textContent = text;
  return n;
};
const fmt = (x, d = 2) => x === null || x === undefined ? "–" : Number(x).toFixed(d);
const LEVELS = [["L1", "What's going on"], ["L2", "What it means"], ["L3", "What happens next"]];
const LEVEL_NAME = Object.fromEntries(LEVELS);
const QS = D.questions;

// tooltip
const tip = $("#tip");
function showTip(ev, rows) {
  tip.replaceChildren(...rows.map((r, i) => el("div", {}, i === 0 ? el("strong", { text: r }) : r)));
  tip.style.display = "block";
  const x = Math.min(ev.clientX + 14, innerWidth - tip.offsetWidth - 8);
  const y = Math.min(ev.clientY + 14, innerHeight - tip.offsetHeight - 8);
  tip.style.left = x + "px"; tip.style.top = y + "px";
}
const hideTip = () => { tip.style.display = "none"; };
function hover(node, rows) {
  node.setAttribute("tabindex", "0");
  node.addEventListener("pointermove", e => showTip(e, rows()));
  node.addEventListener("pointerleave", hideTip);
  node.addEventListener("focus", e => { const b = node.getBoundingClientRect(); showTip({ clientX: b.right, clientY: b.top }, rows()); });
  node.addEventListener("blur", hideTip);
}

// theme toggle (per-viewer convenience; works without storage)
$("#theme").addEventListener("click", () => {
  const r = document.documentElement;
  const dark = r.dataset.theme ? r.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  r.dataset.theme = dark ? "light" : "dark";
  try { localStorage.setItem("sagat-theme", r.dataset.theme); } catch (e) {}
});
try { const t = localStorage.getItem("sagat-theme"); if (t) document.documentElement.dataset.theme = t; } catch (e) {}

// state
const state = { set: 0, tab: "results", moment: null, question: "next_speaker" };
const S = () => D.sets[state.set];
const viewByKey = () => Object.fromEntries(S().views.map(v => [v.key, v]));

// tabs
const TABS = [["results", "Results"], ["moments", "Moments"], ["questions", "Questions"], ["try", "Try it yourself"], ["method", "Method & data"]];
for (const [k, name] of TABS) {
  $("#tabs").append(el("button", { role: "tab", "aria-selected": String(k === state.tab), "data-k": k, text: name,
    on: { click: () => { state.tab = k; render(); } } }));
}
D.sets.forEach((s, i) => $("#set").append(el("option", { value: i, text: s.title })));
$("#set").addEventListener("change", e => { state.set = +e.target.value; state.moment = null; render(); });
if (D.public) $("#publicnote").append(el("div", { class: "banner", text:
  "Public build: the AI Village's own text (what the analyst was shown, multiple-choice option wording, database queries) is withheld under the dataset's research-only licence. Answers, true answers and scores are all here. With dataset access, run `uv run python -m sagat explorer` to build the full version." }));

function render() {
  for (const b of $("#tabs").children) b.setAttribute("aria-selected", String(b.dataset.k === state.tab));
  for (const [k] of TABS) $("#tab-" + k).hidden = k !== state.tab;
  const s = S();
  $("#setnote").textContent = `${s.freezes.length} moments · ${s.views.length - 1} analyst views · ${s.runs.length} analyst runs`;
  ({ results: renderResults, moments: renderMoments, questions: renderQuestions, try: renderTry, method: renderMethod })[state.tab]();
}

// ---------------------------------------------------------------- Results
function renderResults() {
  const root = $("#tab-results"); root.replaceChildren();
  const s = S();
  const card1 = el("div", { class: "card" },
    el("h2", { text: "Score by level, for every view" }),
    el("p", { class: "lede", text: "Each dot is a view's average score across the moments (0 = always wrong, 1 = always right); the bar either side is its ~95% margin of error. The orange line is the “nothing changes” rule: assume the next couple of hours look like the last half hour. On the first two levels the rule is perfect by construction (the answers are countable from the record), so it is a ceiling there; on “what happens next” it is the bar to beat." }));
  card1.append(levelChart(s));
  root.append(card1);

  const card2 = el("div", { class: "card" },
    el("h2", { text: "Moment by moment: did view A beat view B?" }),
    el("p", { class: "lede", text: "Averages can hide luck. Here each dot is one frozen moment: how much better (right) or worse (left) view A scored than view B at that same moment. The black bar is the average difference and its margin of error; if it doesn't cross zero, the difference is one we report. Click a dot to open that moment." }));
  const pairSel = el("select", { "aria-label": "Comparison" });
  s.pairs.forEach((p, i) => pairSel.append(el("option", { value: i, text: `${nameOf(p.a)}  vs  ${nameOf(p.b)}` })));
  const lvSel = el("select", { "aria-label": "Level" });
  [...LEVELS, ["all", "All questions"]].forEach(([k, n]) => lvSel.append(el("option", { value: k, text: n })));
  lvSel.value = "L3";
  const def = s.pairs.findIndex(p => p.a.endsWith("· dashboard") && p.b.startsWith("heuristic"));
  if (def >= 0) pairSel.value = def;
  const holder = el("div");
  const draw = () => holder.replaceChildren(pairChart(s, s.pairs[+pairSel.value], lvSel.value));
  pairSel.addEventListener("change", draw); lvSel.addEventListener("change", draw);
  card2.append(el("div", { class: "controls" }, el("label", {}, "Compare ", pairSel), el("label", {}, "on ", lvSel)), holder);
  root.append(card2); draw();

  const card3 = el("div", { class: "card" },
    el("h2", { text: "Why forecasts fail: analysts bet on activity stopping" }),
    el("p", { class: "lede", text: "The two yes/no forecasting questions (“will agent X post in the next 30 minutes?”, “will a human post in the next 2 hours?”). Bars count wrong answers by direction: left = said “no, it won't happen” but it did; right = said “yes” but it didn't. Activity in this swarm usually continues, and analysts mostly err by predicting it will stop." }));
  card3.append(directionChart(s));
  root.append(card3);

  const card4 = el("div", { class: "card" },
    el("h2", { text: "Every question, every view" }),
    el("p", { class: "lede", text: "Average score per question; the stronger the blue, the higher the score. Low cells in an otherwise good view point at something the view doesn't show (e.g. who talks to whom on the original dashboard)." }));
  card4.append(heatmap(s));
  root.append(card4);
}
const nameOf = k => (viewByKey()[k] || { name: k }).name;

function levelChart(s) {
  const views = s.views;
  const W = 1120, rowH = 30, top = 34, left = 330, panelW = 220, gap = 50;
  const H = top + views.length * rowH + 30;
  const svg = sv("svg", { viewBox: `0 0 ${W} ${H}`, width: "100%", role: "img",
    "aria-label": "Dot plot of score by level for each view" });
  views.forEach((v, i) => {
    const y = top + i * rowH + rowH / 2;
    const t = sv("text", { x: left - 12, y: y + 4, "text-anchor": "end", class: v.cond === "rule" ? "ink" : "" }, v.name);
    svg.append(t);
    if (v.no_answer) svg.append(sv("text", { x: left - 12, y: y + 16, "text-anchor": "end", class: "muted", "font-size": "10" }, `${v.no_answer} run(s) with no answer excluded`));
  });
  const rule = views.find(v => v.cond === "rule");
  LEVELS.forEach(([lv, lname], p) => {
    const x0 = left + p * (panelW + gap), sx = x => x0 + x * panelW;
    svg.append(sv("text", { x: x0, y: 16, class: "ink", "font-weight": "600" }, lname));
    for (const g of [0, 0.25, 0.5, 0.75, 1]) {
      svg.append(sv("line", { x1: sx(g), x2: sx(g), y1: top - 6, y2: H - 24, stroke: "var(--grid)", "stroke-width": 1 }));
      svg.append(sv("text", { x: sx(g), y: H - 8, "text-anchor": "middle", class: "muted" }, g.toFixed(2).replace(/0$/, "")));
    }
    if (rule) svg.append(sv("line", { x1: sx(rule.levels[lv]), x2: sx(rule.levels[lv]), y1: top - 6, y2: H - 24,
      stroke: "var(--rule)", "stroke-width": 2 }));
    views.forEach((v, i) => {
      if (v.cond === "rule") return;
      const y = top + i * rowH + rowH / 2, m = v.levels[lv], h = v.ci[lv] || 0;
      if (m === null || m === undefined) return;
      svg.append(sv("line", { x1: sx(Math.max(0, m - h)), x2: sx(Math.min(1, m + h)), y1: y, y2: y,
        stroke: "var(--accent)", "stroke-width": 2, "stroke-linecap": "round", opacity: 0.45 }));
      const dot = sv("circle", { cx: sx(m), cy: y, r: 5, fill: "var(--accent)", stroke: "var(--surface)", "stroke-width": 2 });
      const hit = sv("circle", { cx: sx(m), cy: y, r: 12, fill: "transparent" });
      hover(hit, () => [`${fmt(m)} ± ${fmt(h)}`, v.name, `${lname} · ${v.n} moments scored`,
        rule ? `rule: ${fmt(rule.levels[lv])}` : ""]);
      svg.append(dot, hit);
    });
  });
  const wrap = el("div");
  wrap.append(el("div", { class: "legend" },
    el("span", {}, el("span", { class: "key", style: "background:var(--accent);border-radius:50%" }), "view average (bar = margin of error)"),
    el("span", {}, el("span", { class: "keyline", style: "border-color:var(--rule)" }), "“nothing changes” rule")), svg);
  wrap.append(tableToggle(["View", "n", "No answer", "What's going on", "What it means", "What happens next", "All", "$ / moment"],
    views.map(v => [v.name, v.n, v.no_answer, ...["L1", "L2", "L3", "all"].map(l => `${fmt(v.levels[l])} ± ${fmt(v.ci[l])}`),
      v.cost === null ? "–" : "$" + v.cost.toFixed(3)])));
  return wrap;
}

function pairChart(s, pair, lv) {
  const L = pair.levels[lv];
  const ids = Object.keys(L.diffs);
  const counts = {};
  ids.forEach(f => { const k = Math.round(L.diffs[f] * 40); counts[k] = (counts[k] || 0) + 1; });
  const maxStack = Math.max(1, ...Object.values(counts));
  const half = Math.ceil(maxStack / 2) * 11 + 8, dotMid = 24 + half, meanY = dotMid + half + 34;
  const W = 1000, H = meanY + 56, pad = 40, sx = x => pad + (x + 1) / 2 * (W - 2 * pad);
  const svg = sv("svg", { viewBox: `0 0 ${W} ${H}`, width: "100%", role: "img", "aria-label": "Per-moment differences" });
  for (const g of [-1, -0.5, 0, 0.5, 1]) {
    svg.append(sv("line", { x1: sx(g), x2: sx(g), y1: 16, y2: meanY + 10, stroke: g === 0 ? "var(--axis)" : "var(--grid)", "stroke-width": 1 }));
    svg.append(sv("text", { x: sx(g), y: meanY + 26, "text-anchor": "middle", class: "muted" }, (g > 0 ? "+" : "") + g));
  }
  svg.append(sv("text", { x: sx(-1), y: H - 6, class: "muted" }, "← B better"));
  svg.append(sv("text", { x: sx(1), y: H - 6, "text-anchor": "end", class: "muted" }, "A better →"));
  // beeswarm-ish: stack equal values
  const buckets = {};
  ids.forEach(f => {
    const d = L.diffs[f], k = Math.round(d * 40);
    const n = (buckets[k] = (buckets[k] || 0) + 1) - 1;
    const y = dotMid + (n % 2 ? 1 : -1) * Math.ceil(n / 2) * 11;
    const fz = s.freezes.find(x => x.id === f);
    const c = sv("circle", { cx: sx(d), cy: y, r: 4.5, fill: d > 0 ? "var(--pos)" : d < 0 ? "var(--neg)" : "var(--muted)",
      stroke: "var(--surface)", "stroke-width": 2, style: "cursor:pointer" });
    const hit = sv("circle", { cx: sx(d), cy: y, r: 10, fill: "transparent", style: "cursor:pointer" });
    hover(hit, () => [(d > 0 ? "+" : "") + fmt(d), `${fz.t_pt} PT · ${fz.roster.length} agents`, "click to open this moment"]);
    hit.addEventListener("click", () => { state.tab = "moments"; state.moment = f; render(); });
    svg.append(c, hit);
  });
  if (L.mean !== null) {
    svg.append(sv("line", { x1: 0, x2: W, y1: meanY - 22, y2: meanY - 22, stroke: "var(--grid)", "stroke-width": 1 }));
    svg.append(sv("line", { x1: sx(L.mean - L.ci), x2: sx(L.mean + L.ci), y1: meanY, y2: meanY, stroke: "var(--ink)", "stroke-width": 2, "stroke-linecap": "round" }));
    svg.append(sv("circle", { cx: sx(L.mean), cy: meanY, r: 5, fill: "var(--ink)" }));
    svg.append(sv("text", { x: sx(L.mean + L.ci) + 10, y: meanY + 4, class: "ink" },
      `average ${L.mean > 0 ? "+" : ""}${fmt(L.mean)} ± ${fmt(L.ci)}`));
  }
  const wins = ids.filter(f => L.diffs[f] > 0).length, losses = ids.filter(f => L.diffs[f] < 0).length;
  const crosses = L.mean === null || (L.mean - L.ci <= 0 && L.mean + L.ci >= 0);
  return el("div", {}, el("div", { class: "legend" },
    el("span", {}, el("span", { class: "key", style: "background:var(--pos);border-radius:50%" }), "A scored higher"),
    el("span", {}, el("span", { class: "key", style: "background:var(--neg);border-radius:50%" }), "B scored higher"),
    el("span", {}, el("span", { class: "key", style: "background:var(--muted);border-radius:50%" }), "tie")),
    svg, el("p", { class: "small", text: `A won at ${wins} moments, B at ${losses}, tied at ${ids.length - wins - losses}. ` +
      (crosses ? "The margin of error crosses zero: not a difference we'd claim." : "The margin of error excludes zero: a real difference.") }));
}

function directionChart(s) {
  const rows = s.direction.filter(d => d.n);
  const max = Math.max(1, ...rows.map(r => Math.max(r.wrong_no, r.wrong_yes)));
  const W = 1000, rowH = 28, left = 360, mid = left + (W - left) / 2, half = (W - left) / 2 - 40, top = 26;
  const H = top + rows.length * rowH + 10;
  const svg = sv("svg", { viewBox: `0 0 ${W} ${H}`, width: "100%", role: "img", "aria-label": "Wrong no versus wrong yes" });
  svg.append(sv("text", { x: mid - 8, y: 14, "text-anchor": "end", class: "ink" }, "← wrongly said “no”"));
  svg.append(sv("text", { x: mid + 8, y: 14, class: "ink" }, "wrongly said “yes” →"));
  svg.append(sv("line", { x1: mid, x2: mid, y1: top - 4, y2: H - 4, stroke: "var(--axis)", "stroke-width": 1 }));
  rows.forEach((r, i) => {
    const y = top + i * rowH + 6, h = 16, v = viewByKey()[r.key];
    svg.append(sv("text", { x: left - 12, y: y + 12, "text-anchor": "end" }, v ? v.name : r.key));
    const wn = r.wrong_no / max * half, wy = r.wrong_yes / max * half;
    const bn = sv("path", { d: roundedBar(mid - 1 - wn, y, wn, h, "left"), fill: "var(--neg)" });
    const by = sv("path", { d: roundedBar(mid + 1, y, wy, h, "right"), fill: "var(--pos)" });
    svg.append(bn, by,
      sv("text", { x: mid - 6 - wn, y: y + 12, "text-anchor": "end", class: "ink" }, r.wrong_no),
      sv("text", { x: mid + 6 + wy, y: y + 12, class: "ink" }, r.wrong_yes));
    const hit = sv("rect", { x: left, y: y - 4, width: W - left, height: rowH, fill: "transparent" });
    hover(hit, () => [`${r.wrong_no} wrong “no” · ${r.wrong_yes} wrong “yes”`, v ? v.name : r.key, `out of ${r.n} yes/no forecasts`]);
    svg.append(hit);
  });
  return el("div", {}, el("div", { class: "legend" },
    el("span", {}, el("span", { class: "key", style: "background:var(--neg)" }), "said it won't happen, but it did"),
    el("span", {}, el("span", { class: "key", style: "background:var(--pos)" }), "said it will happen, but it didn't")), svg,
    tableToggle(["View", "Wrong “no”", "Wrong “yes”", "Forecasts"], rows.map(r => [nameOf(r.key), r.wrong_no, r.wrong_yes, r.n])));
}
function roundedBar(x, y, w, h, dir) {
  if (w <= 0) return "";
  const r = Math.min(4, w);
  return dir === "right"
    ? `M${x},${y} H${x + w - r} Q${x + w},${y} ${x + w},${y + r} V${y + h - r} Q${x + w},${y + h} ${x + w - r},${y + h} H${x} Z`
    : `M${x + w},${y} H${x + r} Q${x},${y} ${x},${y + r} V${y + h - r} Q${x},${y + h} ${x + r},${y + h} H${x + w} Z`;
}

function heatmap(s) {
  const qids = Object.keys(s.qmeta).sort((a, b) => (s.qmeta[a] + a).localeCompare(s.qmeta[b] + b));
  const t = el("table");
  const group = el("tr", {}, el("th", { text: "" }));
  for (const [lv, name] of LEVELS) {
    const n = qids.filter(q => s.qmeta[q] === lv).length;
    if (n) group.append(el("th", { colspan: n, style: "border-bottom:2px solid var(--axis)", text: name }));
  }
  const head = el("tr", {}, el("th", { text: "View" }));
  qids.forEach(q => head.append(el("th", { style: "min-width:84px;font-weight:500", text: QS[q] || q })));
  t.append(group, head);
  for (const v of s.views) {
    const tr = el("tr", {}, el("td", { style: "min-width:230px", text: v.name }));
    for (const q of qids) {
      const xs = v.per_q[q] || [];
      const m = xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null;
      const step = m === null ? 0 : Math.min(7, Math.round(m * 7));
      const td = el("td", { class: "num", style: `background:var(--seq-${step});color:var(--si-${step})`,
        text: m === null ? "–" : m.toFixed(2) });
      hover(td, () => [m === null ? "no data" : m.toFixed(2), v.name, `${QS[q]} · ${xs.length} moments`]);
      tr.append(td);
    }
    t.append(tr);
  }
  return t;
}

function tableToggle(headers, rows) {
  const det = el("details", {}, el("summary", { class: "small", text: "Show as a table" }));
  const t = el("table", {}, el("tr", {}, headers.map(h => el("th", { text: h }))));
  rows.forEach(r => t.append(el("tr", {}, r.map((c, i) => el("td", { class: i ? "num" : "", text: String(c) })))));
  det.append(t);
  return det;
}

// ---------------------------------------------------------------- Moments
function answerCell(q, a, sc) {
  if (a === undefined) return el("td", { class: "small", text: "no answer" });
  let shown = Array.isArray(a) ? (a.length ? a.join(", ") : "(none)") : (a === null ? "(skipped)" : String(a));
  if (q.kind === "set" && Array.isArray(a)) {
    const T = new Set(q.truth), A = new Set(a);
    const missed = q.truth.filter(x => !A.has(x)), extra = a.filter(x => !T.has(x));
    shown = !missed.length && !extra.length ? (T.size ? `all ${T.size} right` : "correctly said none") :
      [missed.length ? `missed: ${missed.join(", ")}` : "", extra.length ? `extra: ${extra.join(", ")}` : ""].filter(Boolean).join(" · ");
  }
  const icon = sc === 1 ? "✓ " : sc === 0 ? "✗ " : "◐ ";
  return el("td", { class: "ans" }, el("span", { class: sc === 1 ? "ok" : sc === 0 ? "no" : "", text: icon }),
    shown, sc !== 1 && sc !== 0 ? el("span", { class: "pill", text: fmt(sc) }) : null);
}
function truthText(q, t) {
  if (Array.isArray(t)) return q.kind === "single" ? t.join(" or ") : (t.length ? t.join(", ") : "(none)");
  return String(t);
}
function renderMoments() {
  const root = $("#tab-moments"); root.replaceChildren();
  const s = S();
  if (!state.moment || !s.freezes.find(f => f.id === state.moment)) state.moment = s.freezes[0].id;
  const list = el("div", { class: "list", role: "list" });
  for (const f of s.freezes) {
    list.append(el("button", { "aria-current": String(f.id === state.moment), on: { click: () => { state.moment = f.id; renderMoments(); } } },
      `${f.t_pt.slice(0, 16)} PT`, el("span", { class: "small", text: `${f.roster.length} agents · focal: ${f.focal}` })));
  }
  const f = s.freezes.find(x => x.id === state.moment);
  const runs = s.runs.filter(r => r.freeze === f.id);
  const keys = s.views.filter(v => v.cond !== "rule").map(v => v.key).filter(k => runs.some(r => r.key === k));
  const detail = el("div");
  detail.append(el("h2", { text: `Frozen at ${f.t_pt} Pacific time` }),
    el("p", { class: "small", text: `${f.roster.length} agents on the roster · agent X for this moment: ${f.focal} · id ${f.id}` }));
  const t = el("table");
  t.append(el("tr", {}, el("th", { text: "Question" }), el("th", { text: "True answer" }), el("th", { text: "“Nothing changes” rule" }),
    keys.map(k => el("th", { text: nameOf(k) }))));
  for (const q of f.queries) {
    const tr = el("tr", {}, el("td", { class: "qcol" }, el("span", { class: "pill", style: "margin:0 6px 0 0", text: LEVEL_NAME[q.level] }),
      el("div", { style: "font-weight:600", text: QS[q.id] || q.id }), el("div", { class: "small", text: q.text }),
      q.options && q.options.length ? el("div", { class: "small" }, q.options.map((o, i) => el("div", { text: `${"ABCD"[i]}. ${o}` }))) : null),
      el("td", { class: "acol", text: q.kind === "set" ? (q.truth.length ? `${q.truth.length} agents: ${truthText(q, q.truth)}` : "none") : truthText(q, q.truth) }));
    const ruleSc = (viewByKey()["heuristic (persistence)"].scores[f.id] || {})[q.id];
    tr.append(answerCell(q, q.heuristic, ruleSc));
    for (const k of keys) {
      const r = runs.find(x => x.key === k);
      if (!r || !r.answers) { tr.append(el("td", { class: "small", text: r ? `no answer (${r.stop})` : "not run" })); continue; }
      const sc = ((viewByKey()[k].scores || {})[f.id] || {})[q.id];
      tr.append(answerCell(q, r.answers[q.id], sc));
    }
    t.append(tr);
  }
  detail.append(el("div", { class: "card" }, el("h3", { text: "Questions and answers" }), t));
  const runInfo = el("table", {}, el("tr", {}, ["View", "Requests", "Database queries", "Stop", "Cost"].map(h => el("th", { text: h }))));
  for (const k of keys) {
    const r = runs.find(x => x.key === k);
    runInfo.append(el("tr", {}, el("td", { text: nameOf(k) }), el("td", { class: "num", text: r.requests }),
      el("td", { class: "num", text: r.n_sql }), el("td", { text: r.stop || "" }), el("td", { class: "num", text: "$" + r.cost.toFixed(4) })));
  }
  detail.append(el("div", { class: "card" }, el("h3", { text: "Runs at this moment" }), runInfo));
  // what the analyst saw
  const seen = el("div", { class: "card" }, el("h3", { text: "What the analyst was shown" }));
  if (D.public) {
    seen.append(el("p", { class: "small", text: "Withheld in the public build (AI Village dataset text). Build the full explorer locally to see it." }));
  } else {
    const conds = [...new Set(keys.map(k => k.split(" · ")[1]))];
    const sel = el("select", { "aria-label": "View" });
    conds.forEach(c => sel.append(el("option", { value: c, text: nameOf(keys.find(k => k.endsWith("· " + c))).split(" · ")[0] })));
    const box = el("div");
    const show = () => {
      const c = sel.value, txt = s.prompts[`${c}|${f.id}`] || "(not recorded)";
      const parts = [el("details", {}, el("summary", { class: "small", text: "Instructions given to every analyst (same for all views)" }), el("pre", { text: s.prompts.__system__ }))];
      if (c === "raw" || c === "both") parts.push(el("details", {}, el("summary", { class: "small", text: "Database tool description" }), el("pre", { text: s.prompts.__sql_tool__ })));
      parts.push(el("pre", { text: txt }));
      const sqlRuns = runs.filter(r => r.key.endsWith("· " + c) && r.sql.length);
      for (const r of sqlRuns) parts.push(el("details", {}, el("summary", { class: "small", text: `Database queries the analyst ran (${r.sql.length}) · ${nameOf(r.key)}` }),
        el("pre", { text: r.sql.map((q, i) => `-- ${i + 1}\n${q}`).join("\n\n") })));
      box.replaceChildren(...parts);
    };
    sel.addEventListener("change", show);
    seen.append(el("div", { class: "controls" }, el("label", {}, "View ", sel)), box); show();
  }
  detail.append(seen);
  root.append(el("div", { class: "two" }, list, detail));
}

// ---------------------------------------------------------------- Questions
function renderQuestions() {
  const root = $("#tab-questions"); root.replaceChildren();
  const s = S();
  const qids = Object.keys(s.qmeta).sort((a, b) => (s.qmeta[a] + a).localeCompare(s.qmeta[b] + b));
  if (!qids.includes(state.question)) state.question = qids[0];
  const sel = el("select", { "aria-label": "Question" });
  qids.forEach(q => sel.append(el("option", { value: q, text: `${LEVEL_NAME[s.qmeta[q]]}: ${QS[q] || q}` })));
  sel.value = state.question;
  sel.addEventListener("change", () => { state.question = sel.value; renderQuestions(); });
  const keys = s.views.filter(v => v.cond !== "rule").map(v => v.key);
  const t = el("table");
  t.append(el("tr", {}, el("th", { text: "Moment" }), el("th", { text: "True answer" }), el("th", { text: "Rule" }), keys.map(k => el("th", { text: nameOf(k) }))));
  let qtext = "";
  for (const f of s.freezes) {
    const q = f.queries.find(x => x.id === state.question);
    if (!q) continue;
    qtext = q.text.replace(f.focal, "agent X");
    const tr = el("tr", {}, el("td", { style: "min-width:120px" }, el("a", { href: "#", text: f.t_pt.slice(0, 16), on: { click: e => { e.preventDefault(); state.tab = "moments"; state.moment = f.id; render(); } } }),
      el("div", { class: "small", text: `${f.roster.length} agents` })), el("td", { text: truthText(q, q.truth) }));
    tr.append(answerCell(q, q.heuristic, (viewByKey()["heuristic (persistence)"].scores[f.id] || {})[q.id]));
    for (const k of keys) {
      const r = s.runs.find(x => x.key === k && x.freeze === f.id);
      if (!r || !r.answers) { tr.append(el("td", { class: "small", text: r ? "no answer" : "–" })); continue; }
      tr.append(answerCell(q, r.answers[q.id], ((viewByKey()[k].scores || {})[f.id] || {})[q.id]));
    }
    t.append(tr);
  }
  root.append(el("div", { class: "controls" }, el("label", {}, "Question ", sel)),
    el("p", { class: "sub", text: qtext }),
    el("div", { class: "card" }, t));
}

// ---------------------------------------------------------------- Try it yourself
// Same scoring rules as sagat/queries.py: set -> F1 (empty vs empty = 1);
// single -> right if among the accepted answers; bool / mc -> exact match.
function scoreAnswer(q, a) {
  if (q.kind === "set") {
    const A = new Set(a || []), T = new Set(q.truth);
    if (!A.size && !T.size) return 1;
    let tp = 0; A.forEach(x => { if (T.has(x)) tp++; });
    return tp ? 2 * tp / (A.size + T.size) : 0;
  }
  if (q.kind === "single") return q.truth.includes(a) ? 1 : 0;
  return a === q.truth ? 1 : 0;
}
const tryState = { moment: null, view: "dashboard", hide: false, phase: "look", answers: {} };
function loadTally() { try { return JSON.parse(localStorage.getItem("sagat-tally") || "[]"); } catch (e) { return []; } }
function saveTally(t) { try { localStorage.setItem("sagat-tally", JSON.stringify(t)); } catch (e) {} }
let tally = loadTally();
function renderTry() {
  const root = $("#tab-try"); root.replaceChildren();
  const s = S();
  if (D.public) {
    root.append(el("div", { class: "card" }, el("h2", { text: "Try it yourself" }),
      el("p", { text: "This tab shows you the same status board an analyst saw at a frozen moment, asks you the same 11 questions and scores you against what really happened. The status board is AI Village dataset text, so it is only in the full, locally built explorer: with dataset access, run `uv run python -m sagat explorer`." })));
    return;
  }
  const views = [...new Set(s.runs.map(r => r.key.split(" · ")[1]))].filter(c => c.startsWith("dashboard"));
  if (!views.includes(tryState.view)) tryState.view = views[0];
  if (!tryState.moment || !s.freezes.find(f => f.id === tryState.moment)) newMoment(s);
  const f = s.freezes.find(x => x.id === tryState.moment);
  const viewSel = el("select", { "aria-label": "Status board version" });
  views.forEach(c => viewSel.append(el("option", { value: c, text: COND_LABEL[c] || c })));
  viewSel.value = tryState.view;
  viewSel.addEventListener("change", () => { tryState.view = viewSel.value; tryState.phase = "look"; tryState.answers = {}; renderTry(); });
  const hide = el("input", { type: "checkbox", id: "hide" }); hide.checked = tryState.hide;
  hide.addEventListener("change", () => { tryState.hide = hide.checked; renderTry(); });
  root.append(el("div", { class: "card" },
    el("h2", { text: "Try it yourself: how much situation awareness does the dashboard give you?" }),
    el("p", { class: "lede", text: "You get exactly what the AI analyst got at one frozen moment: the status board and 11 questions. Answer, submit, and you're scored with the same rules, next to the analysts and the “nothing changes” rule. Classic SAGAT hides the display while you answer, which tests what you took in rather than what you can look up." }),
    el("div", { class: "controls" }, el("label", {}, "Status board ", viewSel),
      el("label", {}, hide, " Classic SAGAT: hide the board while I answer"),
      el("button", { type: "button", text: "New random moment", on: { click: () => { newMoment(s); renderTry(); } } })),
    el("p", { class: "small", text: `Moment: ${f.t_pt} PT · ${f.roster.length} agents · agent X = ${f.focal}` })));
  const promptText = s.prompts[`${tryState.view}|${f.id}`] || "";
  const board = promptText.slice(promptText.indexOf("# Village status board"), promptText.lastIndexOf("You have no other access"));
  if (tryState.phase === "look" && tryState.hide) {
    root.append(el("div", { class: "card" }, el("h3", { text: "Study the board, then hide it to answer" }), boardNote(), renderBoard(board),
      el("button", { type: "button", text: "Hide the board and answer →", on: { click: () => { tryState.phase = "answer"; renderTry(); } } })));
    return;
  }
  if (!tryState.hide) root.append(el("div", { class: "card" }, el("h3", { text: "Status board" }), boardNote(), renderBoard(board)));
  const form = el("div", { class: "card" }, el("h3", { text: tryState.phase === "done" ? "Your answers, scored" : "Your answers" }));
  for (const q of f.queries) {
    const box = el("div", { style: "margin:12px 0;padding-bottom:10px;border-bottom:1px solid var(--grid)" },
      el("div", { style: "font-weight:600" }, el("span", { class: "pill", style: "margin:0 6px 0 0", text: LEVEL_NAME[q.level] }), QS[q.id] || q.id),
      el("div", { class: "small", text: q.text }));
    const done = tryState.phase === "done";
    const cur = tryState.answers[q.id];
    const opts = q.kind === "mc" ? q.options.map((o, i) => ["ABCD"[i], `${"ABCD"[i]}. ${o}`])
      : q.kind === "bool" ? [[true, "Yes"], [false, "No"]] : f.roster.map(n => [n, n]);
    const wrap = el("div", { style: "display:flex;flex-wrap:wrap;gap:4px 14px;margin-top:6px" });
    opts.forEach(([val, label], i) => {
      const id = `a-${q.id}-${i}`;
      const input = el("input", { type: q.kind === "set" ? "checkbox" : "radio", name: q.id, id, disabled: done });
      input.checked = q.kind === "set" ? (cur || []).includes(val) : cur === val;
      input.addEventListener("change", () => {
        if (q.kind === "set") {
          const xs = new Set(tryState.answers[q.id] || []); input.checked ? xs.add(val) : xs.delete(val); tryState.answers[q.id] = [...xs];
        } else tryState.answers[q.id] = val;
      });
      wrap.append(el("label", { for: id, class: "small", style: "color:var(--ink)" }, input, " ", label));
    });
    box.append(wrap);
    if (done) {
      const sc = scoreAnswer(q, cur);
      const rule = scoreAnswer(q, q.heuristic);
      const analysts = s.runs.filter(r => r.freeze === f.id && r.key.endsWith("· " + tryState.view) && r.answers)
        .map(r => `${MODEL_LABEL(r.key)} ${fmt(scoreAnswer(q, r.answers[q.id]))}`);
      box.append(el("div", { class: "small", style: "margin-top:6px" },
        el("span", { class: sc === 1 ? "ok" : sc === 0 ? "no" : "", text: (sc === 1 ? "✓ " : sc === 0 ? "✗ " : "◐ ") + `you ${fmt(sc)}` }),
        ` · true answer: ${truthText(q, q.truth)} · rule ${fmt(rule)}` + (analysts.length ? ` · ${analysts.join(" · ")}` : "")));
    }
    form.append(box);
  }
  if (tryState.phase !== "done") {
    form.append(el("button", { type: "button", text: "Submit and score", on: { click: () => {
      tryState.phase = "done";
      const lv = {}; for (const q of f.queries) (lv[q.level] = lv[q.level] || []).push(scoreAnswer(q, tryState.answers[q.id]));
      tally.push({ set: s.name, moment: f.id, view: tryState.view, hidden: tryState.hide, at: new Date().toISOString(),
        levels: Object.fromEntries(Object.entries(lv).map(([k, v]) => [k, v.reduce((a, b) => a + b, 0) / v.length])),
        answers: tryState.answers });
      saveTally(tally); renderTry();
    } } }));
  }
  root.append(form);
  if (tally.length) {
    const t = el("table", {}, el("tr", {}, ["Moment", "Board", "Board hidden", ...LEVELS.map(l => l[1])].map(h => el("th", { text: h }))));
    tally.slice(-12).reverse().forEach(r => t.append(el("tr", {}, el("td", { text: r.moment }), el("td", { text: COND_LABEL[r.view] || r.view }),
      el("td", { text: r.hidden ? "yes" : "no" }), ...LEVELS.map(([k]) => el("td", { class: "num", text: fmt(r.levels[k]) })))));
    root.append(el("div", { class: "card" }, el("h3", { text: `Your attempts (${tally.length}, saved in this browser only)` }), t,
      el("div", { class: "controls" },
        el("button", { type: "button", text: "Download my attempts (CSV)", on: { click: () => download("sagat_my_attempts.csv",
          [["set", "moment", "board", "board_hidden", "at", "L1", "L2", "L3", "answers_json"], ...tally.map(r => [r.set, r.moment, r.view, r.hidden, r.at, r.levels.L1, r.levels.L2, r.levels.L3, JSON.stringify(r.answers)])]) } }),
        el("button", { type: "button", text: "Clear", on: { click: () => { tally = []; saveTally(tally); renderTry(); } } }))));
  }
}
// Minimal renderer for the status-board markdown (headings, tables, lists,
// **bold**). Same text the analyst saw, laid out for a human reader; every
// string goes in via textContent.
function renderBoard(md) {
  const out = el("div", { class: "board" });
  const lines = md.split("\n");
  const inline = (text) => {
    const span = el("span");
    text.split(/(\*\*[^*]+\*\*)/).forEach(part => {
      if (part.startsWith("**") && part.endsWith("**") && part.length > 4) span.append(el("strong", { text: part.slice(2, -2) }));
      else if (part) span.append(part);
    });
    return span;
  };
  let i = 0, list = null;
  while (i < lines.length) {
    const line = lines[i];
    if (line.startsWith("|")) {
      const rows = [];
      while (i < lines.length && lines[i].startsWith("|")) { rows.push(lines[i]); i++; }
      const cells = r => r.replace(/^\|/, "").replace(/\|\s*$/, "").split("|").map(c => c.trim());
      const t = el("table", { class: "boardtable" });
      t.append(el("tr", {}, cells(rows[0]).map(c => el("th", { text: c }))));
      rows.slice(1).filter(r => !/^\|[-|\s]+\|?$/.test(r)).forEach(r => t.append(el("tr", {}, cells(r).map(c => el("td", { text: c })))));
      out.append(el("div", { style: "overflow-x:auto" }, t)); list = null; continue;
    }
    const h = line.match(/^(#{1,3})\s+(.*)/);
    if (h) { out.append(el(h[1].length === 1 ? "h3" : "h4", { text: h[2], style: "margin:14px 0 6px" })); list = null; }
    else if (line.startsWith("- ")) { if (!list) { list = el("ul", { style: "margin:4px 0;padding-left:20px" }); out.append(list); } list.append(el("li", { class: "small", style: "color:var(--ink)" }, inline(line.slice(2)))); }
    else if (line.trim()) { out.append(el("p", {}, inline(line))); list = null; }
    else list = null;
    i++;
  }
  return out;
}
function newMoment(s) {
  const pick = s.freezes[Math.floor(Math.random() * s.freezes.length)];
  tryState.moment = pick.id; tryState.phase = "look"; tryState.answers = {};
}
const boardNote = () => el("p", { class: "small", text: "The same text the AI analyst received, laid out as tables for easier reading. The raw version is in the Moments tab." });
const COND_LABEL = { dashboard: "Original dashboard", dashboard2: "+ who-talks-to-whom + patterns", dashboard3: "+ patterns + agents' plans" };
const MODEL_LABEL = k => k.includes("sonnet") ? "Sonnet" : k.includes("deepseek") ? "DeepSeek" : k.split(" · ")[0];

// ---------------------------------------------------------------- Method & data
function csvEscape(v) { const s = v === null || v === undefined ? "" : (Array.isArray(v) ? v.join("; ") : String(v)); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; }
function download(name, rows) {
  const blob = new Blob([rows.map(r => r.map(csvEscape).join(",")).join("\n")], { type: "text/csv" });
  const a = el("a", { href: URL.createObjectURL(blob), download: name }); document.body.append(a); a.click(); a.remove();
}
function renderMethod() {
  const root = $("#tab-method"); root.replaceChildren();
  const s = S();
  const answersCsv = () => {
    const rows = [["set", "moment_id", "moment_pt", "agents_on_roster", "focal_agent", "question", "level", "kind", "true_answer", "view", "model", "condition", "answer", "score"]];
    for (const set of D.sets) for (const f of set.freezes) for (const q of f.queries) {
      const vk = Object.fromEntries(set.views.map(v => [v.key, v]));
      rows.push([set.name, f.id, f.t_pt, f.roster.length, f.focal, q.id, q.level, q.kind, q.truth, "rule", "", "rule", q.heuristic, (vk["heuristic (persistence)"].scores[f.id] || {})[q.id]]);
      for (const r of set.runs.filter(x => x.freeze === f.id)) {
        const [m, c] = r.key.split(" · ");
        rows.push([set.name, f.id, f.t_pt, f.roster.length, f.focal, q.id, q.level, q.kind, q.truth, vk[r.key] ? vk[r.key].name : r.key, m, c,
          r.answers ? r.answers[q.id] : "NO ANSWER", r.answers ? ((vk[r.key].scores[f.id] || {})[q.id]) : ""]);
      }
    }
    download("sagat_answers.csv", rows);
  };
  const runsCsv = () => {
    const rows = [["set", "moment_id", "model", "condition", "answered", "requests", "database_queries", "stop_reason", "served_by", "cost_usd"]];
    for (const set of D.sets) for (const r of set.runs) { const [m, c] = r.key.split(" · "); rows.push([set.name, r.freeze, m, c, !!r.answers, r.requests, r.n_sql, r.stop, r.served_by, r.cost]); }
    download("sagat_runs.csv", rows);
  };
  root.append(el("div", { class: "card" },
    el("h2", { text: "How to check our claims" }),
    el("p", { text: "Every number on this page comes from the files below; nothing is typed in by hand. The page is generated by the same scoring code that writes the summary tables in the repo, from the saved answers of every analyst run." }),
    el("ul", {},
      el("li", { text: "Download every answer (one row per moment × question × view, with the true answer and score) or every run (cost, number of requests, why it stopped) as CSV below, and re-tally anything." }),
      el("li", { text: "The “Moments” tab shows, for any moment, the exact text the analyst was shown and every answer. The “Questions” tab lines up one question across every moment." }),
      el("li", { text: "Moments that were blocked or returned no answers are excluded from averages and counted separately (see the notebook, Entries 7 and 9)." }),
      el("li", { text: "To rebuild everything from the raw dataset: get access to the AI Village dataset on Hugging Face, then follow the repo README (prep → freezes → run → score → explorer). Moment selection is seeded, so the same moments come back." })),
    el("div", { class: "controls" },
      el("button", { type: "button", on: { click: answersCsv }, text: "Download every answer (CSV)" }),
      el("button", { type: "button", on: { click: runsCsv }, text: "Download every run (CSV)" })),
    el("p", { class: "small", text: `Generated ${D.generated}. Data: AI Digest / AI Village dataset (research-only licence).` + (D.public ? " Public build: dataset text withheld." : " Full build: contains dataset text; do not redistribute.") })));
  root.append(el("div", { class: "card" }, el("h2", { text: "The views in this set" }),
    el("table", {}, el("tr", {}, ["View", "Moments scored", "No answer", "Avg cost per moment"].map(h => el("th", { text: h }))),
      s.views.map(v => el("tr", {}, el("td", { text: v.name }), el("td", { class: "num", text: v.n }), el("td", { class: "num", text: v.cond === "rule" ? "–" : v.no_answer }),
        el("td", { class: "num", text: v.cost === null ? "–" : "$" + v.cost.toFixed(3) }))))));
}

render();
</script>
</body>
</html>
"""
