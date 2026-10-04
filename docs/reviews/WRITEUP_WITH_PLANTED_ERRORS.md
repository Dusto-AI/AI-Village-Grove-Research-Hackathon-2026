> **Archived test copy. Do not quote.** This is an earlier draft of the write-up, exactly as sent to the 15 AI reviewers, with **three deliberately planted errors** (see `PLANTED_KEY.txt`) and the figures replaced by text tables. Its links were written for `docs/` and don't resolve from this folder. The real write-up is [../WRITEUP.md](../WRITEUP.md). *(This banner was added afterwards.)*

# Swarm SAGAT: does your swarm dashboard actually help anyone understand the swarm?

*AI Swarm Dynamics Hackathon (AI Village × Grove Research), 3–4 October 2026.
Solo entry. Data: AI Digest / AI Village dataset, export `838b4150`.*

## In short

People overseeing AI agent swarms need to know **what is going on, what it
means, and what happens next**. Dashboards and "analyst agents" are being
built to help, but almost nobody tests whether they actually improve anyone's
understanding. We borrowed **SAGAT**, a standard test from aviation and
control-room research, and applied it to the AI Village. We froze the swarm
at 52 moments across a year, asked AI analysts 11 questions about each
moment, and scored their answers against what really happened.

- **A plain dashboard takes an analyst from guessing to perfect on every level.** It beat guessing at every one of the 26 moments tested.
- **The test found a specific blind spot in the dashboard, and fixing it
  worked.** It didn't show who interacts with whom. We added that, retested
  on 26 *fresh* moments, and scores on that question rose from 0.29 to 0.84.
- **Nothing beat "assume nothing changes" at forecasting.** Not a much
  stronger model, raw data access, history panels, or the agents' own
  written plans. The best combination scored 0.67 against the rule's 0.65,
  a tie.
- **The analysts' typical mistake: betting that activity will stop.** In
  this swarm, activity usually continues. Showing analysts "typical
  patterns" nearly halved that bias, but didn't produce real foresight.
- **The obvious "error rate" metric is about 40% noise in this dataset,**
  and one agent's own memory says little about the wider swarm's condition.

Everything is reproducible. All the analyst runs together cost **$8.07**.

## The problem

When thousands of agents coordinate (as in the incidents that motivated this
hackathon), the people responsible need *situation awareness*. A tool can
look informative without delivering it. A busy dashboard full of numbers
may leave an overseer no better at answering the questions that matter. We
wanted a way to **measure** whether a swarm-oversight tool helps, rather than
judge it by how it looks.

## The method

**SAGAT** (Situation Awareness Global Assessment Technique; Endsley, 1988).
A pilot flies a simulator. At a random moment it freezes, the screens blank,
and the pilot answers questions at three levels: **perception** (what's
there), **comprehension** (what it means) and **projection** (what happens
next). Answers are checked against the simulator's truth. If a new display
helps, scores go up.

**Why a recorded swarm suits SAGAT.** The AI Village logs everything its
agents do, so:
- **a "freeze" is just a time cut**: hide everything after the chosen
  moment;
- **the right answers are already in the record**, so scoring is automatic;
- **even "what happens next" can be scored**, because the future has
  already happened. Live SAGAT studies rarely manage this.

**What we built.**
- **52 frozen moments**, spread month by month from Sep 2025 to Sep 2026,
  each mid-workday with real activity. Village size ranges from 6 to 32
  agents.
- **A sealed snapshot for each moment.** It holds only the four days before
  the freeze, with anything describing the live system's *current* state
  removed. An automated check found no record dated after its freeze.
- **11 questions** with answers computed from the logs:

  | Level | Questions |
  |---|---|
  | What's going on | Who acted in the last 30 min? What is agent X working on? Who's been chattiest? Did a human post recently? |
  | What it means | Who has X been talking to most? Who has gone quiet? Whose actions produce the most errors? |
  | What happens next | Who'll be working 1.5–2 h later? Who speaks next? Will X post in the next 30 min? Will a human post in the next 2 h? |

- **Different views for the analyst:** nothing but the agent list
  (guessing); a status **dashboard**; **raw records** it can search itself;
  and **one agent's own memory file** and recent actions (does the swarm know
  its own state?).
- **A yardstick:** the **"nothing changes" rule**. It assumes the next
  couple of hours look like the last half hour. It is perfect on the first
  two levels by construction, since those answers can be counted from the
  record, so it marks the ceiling there. On forecasting, it is the bar to
  beat.

**Safeguards.**
- **Moment-by-moment comparisons:** did view A beat view B at the *same*
  moment? This keeps easy and hard moments from distorting the averages.
- **A held-out test:** the improved dashboard was judged only on 26 fresh
  moments we hadn't designed it against.
- **An independently rebuilt answer key:** 515 of 515 recomputed answers
  matched.
- **Blocked or broken runs counted separately,** never scored as wrong.

## What we found

[Figure, shown here as a table: First 26 moments: what each view gives an analyst]
| view | What's going on | What it means | What happens next |
|---|---|---|---|
| “nothing changes” rule | 1.00 | 1.00 | 0.59 |
| Guessing (cheap) | 0.38 ± 0.08 | 0.33 ± 0.11 | 0.44 ± 0.08 |
| Guessing (strong) | 0.31 ± 0.07 | 0.39 ± 0.09 | 0.37 ± 0.07 |
| Dashboard (cheap) | 1.00 ± 0.00 | 0.71 ± 0.10 | 0.55 ± 0.09 |
| Dashboard (strong) | 0.99 ± 0.02 | 0.73 ± 0.07 | 0.57 ± 0.09 |
| Raw records via SQL (cheap) | 0.88 ± 0.12 | 0.85 ± 0.11 | 0.49 ± 0.08 |
| One agent's own memory (cheap) | 0.45 ± 0.08 | 0.35 ± 0.10 | 0.39 ± 0.09 |
| One agent's own memory (strong) | 0.58 ± 0.07 | 0.45 ± 0.09 | 0.42 ± 0.09 |

**1. A dashboard is enough for the present, and digging through raw data
isn't better, just pricier.** With the dashboard, the analyst was perfect on
"what's going on". Searching the raw records itself, it did slightly worse
on that level (0.88). It did better on "what it means" (0.85 vs 0.71), largely because of the blind spot below. And it cost about 4× as much.
*(Notebook Entry 8)*

**2. The test pinpointed what the dashboard was missing.** On "who has agent
X been talking to?", the dashboard analyst scored 0.29. The dashboard showed
each agent's activity but nothing about who interacts with whom. We added a
panel for that, plus "typical patterns" history, and **retested on 26 fresh
moments**. That question rose from 0.58 to 0.84, and "what it means" overall
improved (better at 7 moments, worse at 1). This is the loop we'd recommend
to anyone: **test, find the gap, fix it, retest on new moments.**
*(Entries 8, 10)*

[Figure, shown here as a table: Fresh 26 moments]
| view | What's going on | What it means | What happens next |
|---|---|---|---|
| “nothing changes” rule | 1.00 | 1.00 | 0.65 |
| Guessing (cheap) | 0.40 ± 0.07 | 0.31 ± 0.12 | 0.46 ± 0.08 |
| Original dashboard (cheap) | 1.00 ± 0.00 | 0.80 ± 0.09 | 0.58 ± 0.07 |
| Improved dashboard (cheap) | 1.00 ± 0.00 | 0.88 ± 0.08 | 0.62 ± 0.07 |
| Improved + agents' plans (cheap) | 1.00 ± 0.00 | 0.86 ± 0.08 | 0.60 ± 0.06 |
| Improved dashboard (strong) | 1.00 ± 0.00 | 0.90 ± 0.07 | 0.65 ± 0.06 |
| Improved + plans (strong) | 1.00 ± 0.00 | 0.93 ± 0.08 | 0.67 ± 0.07 |

**3. No view, model or panel beat "nothing changes" at forecasting.** Here
is everything we tried on forecasting, against the rule:
- a model roughly 70–180× pricier per token (Claude Sonnet 5.5 vs DeepSeek
  V4 Flash): no better on the same dashboard;
- raw data access;
- history panels;
- **the agents' own written plans** for what they'll do next.

The best combination (Sonnet, improved dashboard, plans) scored 0.67 against
the rule's 0.65, well within the margin of error. Over the next half-hour to two hours, we found no evidence that what agents *say* they'll do adds anything to what they've *been* doing. *(Entries 9–11, 13)*

[Figure, shown here as a table: wrong answers on the two yes/no forecasts]
| view | wrongly said 'no' | wrongly said 'yes' |
|---|---|---|
| Original dashboard, cheap, first 26 | 16 | 3 |
| Original dashboard, strong, first 26 | 16 | 1 |
| Original dashboard, cheap, fresh 26 | 17 | 3 |
| Improved dashboard, cheap, fresh 26 | 9 | 7 |
| Improved dashboard, strong, fresh 26 | 6 | 5 |

**4. Why forecasts fail: analysts bet on activity stopping.** On the yes/no
forecasts, the wrong answers were overwhelmingly "yes, that will happen"
when it didn't: 16–17 such errors against 1–3 the other way. That held for both
models and both sets of moments. Showing typical patterns roughly balanced
the errors. The stronger model made 6 errors one way and 5 the other. But
balanced errors still only *tie* the rule. Swarm activity is sticky, and
"it carries on" is a hard baseline to beat. *(Entries 10, 13)*

**5. One agent's memory says little about the wider swarm's condition.**
Given one agent's memory file and its last 30 actions, the cheap analyst did
no better than guessing overall. The strong one recovered some sense of who
else was active. Both did poorly on what that activity meant: whose actions produce errors (0.04), and whether a human had recently posted (0.23–0.24). This
is a lower bound, since agents also remember recent conversation that the
records don't keep. *(Entries 8, 9)*

**6. The obvious "error rate" metric is heavily contaminated.** The dataset
flags an action as an "error" whenever anything is printed to the error
stream, and many successful commands print there (code uploads, download
progress). In a sample of 60,000 flagged actions, a rough text check suggests about 40%
were normal output. A dashboard "error rate" built on this flag, ours included,
would show healthy agents as failing. The general lesson: **a SAGAT test is
only as good as its answer key, and the key needs the same scrutiny as the
tool.** *(Entry 14)*

**7. A safety filter blinded the overseer, twice.** During one week the
village worked through security-training exercises (deliberately vulnerable
practice websites). The AI provider's content filter then refused to let
the stronger analyst even read the questions. Both blocked moments fell in
that week. That's a small sample, but it is exactly the activity an overseer
would most want to see. *(Entries 9, 13)*

## What we'd tell people building swarm oversight tools

- **SAGAT-test your dashboard before you trust it.** Write the overseer's
  questions first, at all three levels. Freeze a moment, show your tool,
  ask, and score against the record. Low-scoring questions are your to-do
  list.
- **Always compare against "nothing changes".** A tool that can't beat it
  isn't helping anyone see ahead, however informative it looks.
- **Retest fixes on moments you didn't design against.**
- **Don't expect a smarter analyst to fix a thin display,** and check what
  your metrics actually measure.
- **Test people, not just AI.** We tested AI analysts because we had a day.
  The same frozen moments and questions work for humans. The repo's
  explorer has a **"Try it yourself"** tab where a person takes the same
  test on the same dashboards and is scored by the same rules (including a
  classic mode that hides the board while you answer). We haven't collected
  human results, but this is the use we most want to encourage.

## Check it yourself

- **[NOTES.md](NOTES.md):** the project notebook. 15 dated entries covering
  every decision, why it was made, what was found and how it changed the
  next step, including the mistakes we caught.
- **Explorer:** one offline web page built from the saved runs. It shows
  every moment, exactly what each analyst was shown, every answer against
  the truth, charts, CSV downloads and the self-test.
  `docs/explorer_public.html` is the shareable version with the dataset's
  own text withheld. With dataset access, `uv run python -m sagat explorer`
  builds the full one.
- **Rebuild from scratch:** the [README](../README.md) goes from the raw
  public export to every number here. The 52 moments are published as
  timestamps, and a fresh build reproduced all of them identically.

## Limitations

- **One swarm:** the agents-only AI Village, with data to 18 Sep 2026.
- **26 moments per comparison** is enough for broad differences, not fine
  ones.
- **The questions are narrow, countable definitions** of what an overseer
  cares about. One of them ("whose actions produce errors") rests on the
  noisy flag described in finding 6.
- **The dashboard was deliberately plain**, and we tested AI analysts, not
  people.
- **Forecast horizons were 30 minutes to 2 hours.** Longer-range foresight
  (e.g. "will this week's goal succeed?") is untested.

## Data and thanks

AI Digest / AI Village dataset, used under its research-only licence.
Thanks to the AI Village and Grove Research teams for the data and the
hackathon.
