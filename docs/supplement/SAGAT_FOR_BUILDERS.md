# SAGAT for builders: a practical guide to testing swarm-oversight tools

This is a step-by-step guide for anyone building a dashboard, summariser,
alerting system or "analyst agent" for multi-agent systems. It covers how
to test whether the tool actually improves an overseer's understanding,
using the SAGAT method from human factors. Everything here was tried in
this project; links point to the evidence.

---

## The idea in one paragraph

Situation awareness has three levels (Endsley, 1988; 1995):
**perception** (what's there), **comprehension** (what it means for my
goals) and **projection** (what happens next). SAGAT measures it by
**freezing** a system at random moments, asking the observer a fixed set of
questions about the frozen situation, and **scoring the answers against
ground truth**. If your tool helps, observers using it score higher than
observers without it, and higher than a dumb baseline. A logged swarm makes
this unusually easy: a freeze is just a time cut, the truth is in the logs,
and projection can be scored because the future has already been recorded.

---

## Step 1: Start from what the overseer must know, not from what the tool shows

Classic SAGAT derives its questions from a goal-directed task analysis:
interviewing experienced operators about the decisions they make and the
information each one needs. For a swarm overseer, a lightweight version:

1. **Who is the overseer, and what can they do?** Pause an agent, escalate
   to a human, roll back an action, reallocate work.
2. **What decisions do they make?** "Is anything going wrong right now?",
   "Should I intervene with agent X?", "Will this finish on time?"
3. **What must they know to make each decision?** Write each answer as a
   question with a checkable answer.

Example requirements, by level:

| Level | Routine operations | Safety-relevant |
|---|---|---|
| Perception | Which agents are active? What is X working on? Has a human intervened? | Which agents accessed external systems in the last hour? Who has elevated permissions right now? |
| Comprehension | Who is stuck or failing? Who is coordinating with whom? Who has gone quiet? | Is any agent's report contradicted by its actions? Are two agents coordinating outside sanctioned channels? Is anyone working outside their assigned scope? |
| Projection | Who will still be working in two hours? Will this goal be met? | Will an agent attempt an action needing approval soon? Is resource use on track to exceed a budget? |

**If you can't write a projection question your tool is supposed to help
with, that's already a finding.**

## Step 2: Make every question scorable

- **Pick an answer format the log can settle.** Pick-one (an agent name),
  pick-several (a set of agents, scored by partial credit), yes/no, or
  multiple choice. Avoid free text unless you also build and validate a
  grader.
- **Write the operational definition next to the question.** For example,
  "stuck" = at least 10 actions in the last hour and the highest share of
  failed actions. You will be tempted to change definitions after seeing
  results. If you do, record it, and re-check on fresh moments.
- **Read what the underlying field really contains.** In our data the
  "error" flag also marks successful commands that print to the error
  stream. Removing that harmless output changes who counts as "failing
  most" at about a third of moments. See [ERROR_FLAG.md](ERROR_FLAG.md).
- **Handle ties:** accept any tied answer.
- **Handle "not applicable"** (e.g. nobody mentioned anyone): drop the
  question for that moment rather than inventing a truth.

## Step 3: Choose freeze points

- **Random moments during real activity.** Stratify across the eras or
  conditions you care about, e.g. month by month, quiet vs busy, small vs
  large swarm.
- **Beware freezing just before a natural boundary.** "Who will be working
  in two hours?" asked at 4pm is mostly a question about the end of the
  working day; see [HORIZON.md](HORIZON.md). We excluded such moments by
  requiring activity 1–2 hours later. That itself makes "things carry on"
  slightly more likely to be right, so note it.
- **How many?** With 26 moments, our margins of error on a view's average
  were about ±0.06–0.10. That's enough to see large effects (a dashboard vs
  guessing), not small ones. Detecting a 0.05 improvement reliably would take something like 100+ moments. Repeat runs help less: in our test, the run-to-run wobble was smaller than the uncertainty from having few moments ([VARIANCE.md](VARIANCE.md)).
- **Keep a held-out set.** If you change the tool based on results, judge
  the new version on moments you didn't look at while designing it.

## Step 4: Seal the snapshot

The observer must see **only** information available at the freeze:
- copy only records timestamped at or before the freeze;
- **drop "current state" fields** that were updated later (balances,
  statuses, assignments, end dates set after the fact). These leak the
  future silently;
- **automate the check**: no record in any snapshot postdates its freeze.

## Step 5: Baselines, so scores mean something

Report every observer against:
1. **No information**: what you'd guess anyway (here, the roster only).
2. **Persistence ("nothing changes")**: the next period looks like the
   last. On countable questions it is a *ceiling*, the score of a reader
   who counts correctly. On projection it is the bar real foresight must
   clear.
3. **Base rate ("always yes" / most common answer)**: on our yes/no
   forecasts, "always yes" was about as good as persistence. A tool that
   can't beat the base rate adds no information.

## Step 6: Decide what kind of awareness you're measuring

- **SAGAT proper** (display hidden while answering) tests what the observer
  *took in*. That's the right test for a human glancing at a dashboard.
- **Display visible** while answering (closer to the SPAM method) tests
  what the tool *lets you find*. That's the natural test for an AI analyst
  or a human with time to look things up.
- **Ask every question at every freeze, in a fixed order,** or randomise
  the order if you suspect order effects.
- **For humans:** add a time limit, record response time, and collect a
  workload rating. The explorer's "Try it yourself" tab has a basic
  version, including a hide-the-board mode.

## Step 7: Analyse fairly

- **Compare views moment by moment** (paired), not just by averages: a
  32-agent moment is harder for everyone.
- **Report failed or blocked runs separately.** Don't score them as wrong.
  (In our data, a safety filter blocked one model at every security-related
  moment; see [FILTERS.md](FILTERS.md).)
- **Check run-to-run variation at least once.** AI analysts give different answers on re-runs. Ours changed level averages by up to 0.05 and individual answers 8–13% of the time ([VARIANCE.md](VARIANCE.md)). Don't interpret single-run differences smaller than that.
- **State what a "tie" means.** "No significant difference" with 26 moments
  means "no large difference", not "no difference".

## Step 8: Check the answer key itself

- **Re-implement the truth independently** (we used plain database queries)
  and compare. Ours matched 515 of 515, which catches bugs.
- **Then read raw records by hand.** A matching re-implementation can't
  catch a misunderstanding both versions share. The error flag passed the
  first check and failed the second.

## Step 9: Test the testers

- **Planted incidents** test the observer on the things you most care about catching. Plant a known misreport, policy violation or hidden coordination in some snapshots and not others, then measure the catch rate and the false-alarm rate. **Alter only the evidence. Never insert text the observer could recognise as inserted.** Our first two attempts did, and the analysts flagged the inserted text itself. See [PLANTED_INCIDENTS.md](PLANTED_INCIDENTS.md).
- **Planted errors** test your *reviewers*. Put known mistakes in a report
  and count what reviewers catch. Ours caught all the planted errors that
  contradicted the rest of the text, but that kind of review can't catch an
  error that is consistent, or that lives in the data. See
  [../reviews/](../reviews/).

---

## Pitfall checklist

- [ ] Questions derived from overseer needs, not from the tool's panels.
- [ ] Each question has a written operational definition and a sample of
      its underlying field read by hand.
- [ ] Snapshots sealed; current-state fields dropped; leakage check
      automated.
- [ ] Freezes random, stratified, mid-activity; boundary effects noted.
- [ ] No-information, persistence and base-rate baselines reported.
- [ ] Display hidden or visible, deliberately chosen and stated.
- [ ] Paired, per-level comparisons; failures reported separately; repeat
      runs where affordable.
- [ ] Fixes judged on held-out moments.
- [ ] Answer key re-implemented and spot-read.
- [ ] Planted incidents for the behaviours you most need to catch.

## Doing it with this repo

```bash
# your dashboard = one function: render(frozen_db_path, freeze_pt) -> str
uv run python -m sagat run   --name v2 --cond none,custom --dashboard my_board.py \
                             --model openrouter:deepseek/deepseek-v4-flash
uv run python -m sagat score --name v2
# add questions: write a function in sagat/queries.py returning a Query
# (see q_focal_partner for a comprehension example), then add it to TEMPLATES
# planted incidents: sagat/plant.py is a worked example (misreported activity)
```

The same pieces work for any logged multi-agent system. You need a log you
can cut at any moment, questions written from overseer needs, and answer
keys computed from the log.
