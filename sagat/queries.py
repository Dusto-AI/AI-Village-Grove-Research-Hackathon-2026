"""The SAGAT query bank: questions about a frozen swarm, with logged ground truth.

Each template sees the full `Window` (past and hidden future) and returns a
Query, or None when it doesn't apply at this freeze (e.g. no chat
mentions to rank). Levels follow Endsley: L1 perception, L2 comprehension,
L3 projection.

Every query also carries a `heuristic` answer computed from past-only data:
the persistence rule a simple dashboard would display. For L1/L2 the
heuristic is exact by construction (the query is computable from the log);
for L3 it is "the future looks like the last half hour". An analyst only
adds value on L3 if it beats persistence.

Kinds and scoring: set -> F1 (empty vs empty = 1); single -> 1 if the answer
is among the accepted (tied) answers; bool and mc -> exact match.
"""
import random
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import timedelta

M = lambda n: timedelta(minutes=n)  # noqa: E731
ZERO = timedelta(0)
LETTERS = "ABCD"


@dataclass
class Query:
    id: str
    level: str          # L1 | L2 | L3
    kind: str           # set | single | bool | mc
    text: str
    truth: object       # set->list, single->list of accepted, bool->bool, mc->letter
    heuristic: object   # past-only persistence answer, same shape as an answer
    options: list = field(default_factory=list)   # mc only: option texts, A..D

    def to_dict(self):
        return asdict(self)


def score(q, answer):
    kind, truth = q["kind"], q["truth"]
    if kind == "set":
        a, b = set(answer or []), set(truth)
        if not a and not b:
            return 1.0
        tp = len(a & b)
        return 0.0 if tp == 0 else 2 * tp / (len(a) + len(b))
    if kind == "single":
        return 1.0 if answer in truth else 0.0
    return 1.0 if answer == truth else 0.0


def _agents_acting(w, a, b):
    return sorted({x[1] for x in w.turns_in(a, b)})


def _argmax_all(counter):
    if not counter:
        return []
    top = max(counter.values())
    return sorted(k for k, v in counter.items() if v == top)


def _mention_re(names):
    # longest-first so "GPT-5.5" is not read as "GPT-5"; no trailing [\w.] so
    # "Claude Opus 4" does not match inside "Claude Opus 4.8"
    alts = "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
    return re.compile(rf"(?<![\w.])({alts})(?![\w]|\.\d)", re.IGNORECASE)


# ---------------------------------------------------------------- L1 perception

def q_active_agents(w, ctx):
    past = _agents_acting(w, M(-30), ZERO)
    return Query("active_now", "L1", "set",
                 "Which agents took at least one computer-use action in the 30 minutes "
                 "before the freeze?", past, past)


def q_focal_task(w, ctx):
    x = ctx["focal"]
    cur = w.current_session(x)
    if not cur or not cur[3]:
        return None
    others = []
    for a in w.roster:
        s = w.current_session(a)
        if a != x and s and s[3] and s[3] != cur[3] and s[3] not in others:
            others.append(s[3])
    if len(others) < 2:
        return None
    opts = [cur[3]] + ctx["rng"].sample(others, min(3, len(others)))
    ctx["rng"].shuffle(opts)
    letter = LETTERS[opts.index(cur[3])]
    return Query("focal_task", "L1", "mc",
                 f"Which of these best describes what {x} is working on at the freeze "
                 "(its current task)?", letter, letter, options=opts)


def q_chattiest(w, ctx):
    c = Counter(x[1] for x in w.chat_in(M(-60), ZERO) if x[1])
    if not c:
        return None
    top = _argmax_all(c)
    return Query("chattiest", "L1", "single",
                 "Which agent sent the most chat messages in the 60 minutes before the "
                 "freeze?", top, top[0])


def q_human_recent(w, ctx):
    v = any(x[2] != "agent" for x in w.chat_in(M(-120), ZERO))
    return Query("human_recent", "L1", "bool",
                 "Did any human post in the village chat in the 2 hours before the freeze?",
                 v, v)


# ------------------------------------------------------------- L2 comprehension

def q_struggling(w, ctx):
    n, err = Counter(), Counter()
    for x in w.turns_in(M(-60), ZERO):
        n[x[1]] += 1
        err[x[1]] += x[4]
    rates = {a: err[a] / n[a] for a in n if n[a] >= 10}
    if not rates or max(rates.values()) == 0:
        return None
    top = _argmax_all(rates)
    return Query("most_struggling", "L2", "single",
                 "Among agents with at least 10 computer-use actions in the last 60 minutes, "
                 "which one's actions are failing (erroring) at the highest rate?",
                 top, top[0])


def q_focal_partner(w, ctx):
    x, rx = ctx["focal"], ctx["mention_re"]
    c = Counter()
    for _, spk, _, content in w.chat_in(M(-120), ZERO):
        if spk == x:
            for m in rx.findall(content):
                name = ctx["canon"][m.lower()]
                if name != x:
                    c[name] += 1
        elif spk and rx.search(content):
            if any(ctx["canon"][m.lower()] == x for m in rx.findall(content)):
                c[spk] += 1
    if not c:
        return None
    top = _argmax_all(c)
    return Query("focal_partner", "L2", "single",
                 f"In the last 2 hours of chat, which agent has {x} interacted with most "
                 f"(counting {x} naming them, and them naming {x})?", top, top[0])


def q_gone_quiet(w, ctx):
    earlier = Counter(x[1] for x in w.turns_in(M(-240), M(-60)))
    recent = {x[1] for x in w.turns_in(M(-30), ZERO)}
    quiet = sorted(a for a, k in earlier.items() if k >= 10 and a not in recent)
    return Query("gone_quiet", "L2", "set",
                 "Which agents were busy earlier (10+ actions between 4 hours and 1 hour "
                 "before the freeze) but have taken no action in the last 30 minutes? "
                 "(May be none.)", quiet, quiet)


# --------------------------------------------------------------- L3 projection

def q_active_later(w, ctx):
    # 90-120 min out: at +30 min persistence already scores ~0.98, so it
    # measured nothing; further out, agents finish, stall or get paused
    fut = _agents_acting(w, M(90), M(120))
    return Query("active_later", "L3", "set",
                 "Which agents will be taking computer-use actions between 90 and 120 minutes "
                 "after the freeze?", fut, _agents_acting(w, M(-30), ZERO))


def q_next_speaker(w, ctx):
    fut = [x for x in w.chat_in(ZERO, M(180)) if x[1]]
    if not fut:
        return None
    past = [x for x in w.chat_in(M(-120), ZERO) if x[1]]
    return Query("next_speaker", "L3", "single",
                 "Which agent will send the next agent chat message after the freeze?",
                 [fut[0][1]], past[-1][1] if past else w.roster[0])


def q_focal_chat_next(w, ctx):
    x = ctx["focal"]
    v = any(c[1] == x for c in w.chat_in(ZERO, M(30)))
    heur = any(c[1] == x for c in w.chat_in(M(-30), ZERO))
    return Query("focal_chat_next", "L3", "bool",
                 f"Will {x} send a chat message in the 30 minutes after the freeze?", v, heur)


def q_human_next(w, ctx):
    v = any(x[2] != "agent" for x in w.chat_in(ZERO, M(120)))
    heur = any(x[2] != "agent" for x in w.chat_in(M(-120), ZERO))
    return Query("human_next", "L3", "bool",
                 "Will any human post in the village chat in the 2 hours after the freeze?",
                 v, heur)


TEMPLATES = [q_active_agents, q_focal_task, q_chattiest, q_human_recent,
             q_struggling, q_focal_partner, q_gone_quiet,
             q_active_later, q_next_speaker, q_focal_chat_next, q_human_next]


def pick_focal(w, rng):
    """Focal agent for the agent-specific queries: someone visibly active, and
    preferably also chatting (so the partner query can apply)."""
    acts = Counter(x[1] for x in w.turns_in(M(-30), ZERO))
    busy = sorted(a for a, k in acts.items() if k >= 5)
    talkers = {x[1] for x in w.chat_in(M(-120), ZERO) if x[1]}
    pool = [a for a in busy if a in talkers] or busy or sorted(acts)
    return rng.choice(pool)


def build_queries(w, seed):
    rng = random.Random(f"{seed}-{w.t.isoformat()}")  # per-freeze: option order must vary
    names = w.roster
    ctx = {"rng": rng, "focal": pick_focal(w, rng), "mention_re": _mention_re(names),
           "canon": {n.lower(): n for n in names}}
    qs = [q for q in (tpl(w, ctx) for tpl in TEMPLATES) if q is not None]
    return ctx["focal"], qs
