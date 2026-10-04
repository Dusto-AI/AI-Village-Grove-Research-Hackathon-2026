# Swarm SAGAT: does your swarm dashboard actually help anyone understand the swarm?

*AI Swarm Dynamics Hackathon (AI Village × Grove Research), October 2026.*

People overseeing AI agent swarms rely on dashboards, summaries and AI
analysts to tell them what's going on. Those tools look more polished every
month, and polish is easy to mistake for understanding. This project
borrows **SAGAT**, a standard test from aviation and control-room research,
to *measure* whether an oversight tool helps. We freeze the swarm at a
random moment, ask the observer what's going on, what it means and what
happens next, and score the answers against what really happened. We
applied it to a year of the [AI Village](https://theaidigest.org/village),
at 52 frozen moments.

**Headline results**
- **A plain dashboard gets an AI analyst from guessing to perfect on
  "what's going on".**
- **The test found a gap in the dashboard** (it didn't show who works with
  whom). Fixing it and retesting on fresh moments raised that score from
  0.58 to 0.84.
- **Nothing reliably beat "assume nothing changes" at forecasting:** not a
  stronger model, raw data, history panels, or the agents' own plans.
- **Catching an agent that misreports its work depends on the view.** The
  improved dashboard caught 8 of 9 planted misreports; a chat feed alone
  caught none.
- **Some obvious signals mislead.** The dataset's "error" flag is largely
  harmless output, and one provider's safety filter blinded the analyst
  during security work.

## Where to start

| If you want… | Read |
|---|---|
| The short version | [docs/SUBMISSION.md](docs/SUBMISSION.md) (one page) |
| The full argument, with figures | [docs/WRITEUP.md](docs/WRITEUP.md) |
| Every decision, why, and what it changed, including our mistakes | [docs/NOTES.md](docs/NOTES.md) (project notebook) |
| To test your own dashboard or tool | [docs/supplement/SAGAT_FOR_BUILDERS.md](docs/supplement/SAGAT_FOR_BUILDERS.md) and [examples/minimal_dashboard.py](examples/minimal_dashboard.py) |
| The safety angle | [docs/supplement/SAFETY.md](docs/supplement/SAFETY.md) and [PLANTED_INCIDENTS.md](docs/supplement/PLANTED_INCIDENTS.md) |
| To check our claims | [docs/VERIFY.md](docs/VERIFY.md) (20-minute spot-check) and the explorer below |
| How it works and how to reproduce it | [docs/HARNESS.md](docs/HARNESS.md) |
| Deeper analyses | [docs/supplement/](docs/supplement/README.md) |

## Check our numbers in one minute (no dataset, no API key)

Every answer, true answer and score is in `results/public/answers.csv`.
This recomputes the headline tables from it, using only the standard
library:

```bash
python3 scripts/rescore_public.py
```

To browse every frozen moment, answer and chart, open
[`docs/explorer_public.html`](docs/explorer_public.html) in a browser. It
works offline. It withholds the dataset's own text, so to see exactly what
each analyst was shown, build the full explorer (below).

## Replicate it (needs dataset access)

```bash
# once: raw Hugging Face export -> local databases in ./data (git-ignored)
uv run python -m sagat build-data --raw /path/to/hf/files --out data
uv run python -m sagat prep

# rebuild exactly our 52 moments, then score and explore
uv run python -m sagat freezes --name v1 --times results/freeze_times_v1.txt
uv run python -m sagat freezes --name v2 --times results/freeze_times_v2.txt
uv run python -m sagat run --name v2 --cond none,dashboard,dashboard2 \
    --model openrouter:deepseek/deepseek-v4-flash         # ~$1 for 26 moments
uv run python -m sagat score --name v2
uv run python -m sagat explorer                           # full explorer, incl. "Try it yourself"
```

The table in [docs/HARNESS.md](docs/HARNESS.md#reproducing-every-result)
gives the command and cost for every result. AI analysts vary slightly
between runs; expect averages within about ±0.05 of ours.

## Test your own dashboard

Your dashboard is one function, `render(frozen_db_path, freeze_pt) -> str`.
It gets a sealed snapshot of the swarm at a frozen moment and returns what
your dashboard would show:

```bash
uv run python -m sagat run --name v2 --cond none,custom --dashboard my_board.py \
    --model openrouter:deepseek/deepseek-v4-flash
uv run python -m sagat score --name v2     # your board vs every other view
```

## What's in the repo

```
docs/            write-up, one-page summary, notebook, spot-check guide, harness reference
  supplement/    deeper analyses: builder's guide, safety, planted incidents, noise, filters, …
  reviews/       15 AI reviews of an earlier draft, with three planted errors (and the key)
sagat/           the harness (python -m sagat …)
examples/        template for plugging in your own dashboard
scripts/         supplementary analyses, the reviewer test, the CSV-only rescorer
results/         published freeze times, summary tables, public answers/scores (results/public/)
```

## How this was made

Built solo, in about a day, with an AI coding agent doing most of the
implementation. That is part of the point. The write-up's "Who checks the
checker?" section describes what was verified mechanically, what wasn't,
and a test of AI reviewers using planted errors. Model calls for the whole
project cost about $18.

## Data and licence

Code: **MIT** (see [LICENSE](LICENSE)). The licence covers the code and our
write-ups, not the dataset.

Data: **AI Digest / AI Village, *AI Village dataset*** (Hugging Face:
`aidigestorg/ai-village`), used under its research-only licence (no AI
training). No dataset content is committed beyond agent names, answers and
scores (and the write-up's one worked example). Rebuild everything else
locally.
