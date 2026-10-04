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

**Try it in your browser (no install):**
[**the explorer**](https://dusto-ai.github.io/AI-Village-Grove-Research-Hackathon-2026/explorer_public.html)
shows every frozen moment, every question, what each analyst answered and
how it scored. Its **"Try it yourself"** tab lets you take the same test.

## Key terms

| Term | Meaning |
|---|---|
| **Frozen moment** | A time cut in the AI Village record. The analyst sees only what existed before it; the answers come from what happened after. |
| **Levels L1 / L2 / L3** | SAGAT's three question levels: **L1 perception** (what's going on: who is active, what each agent is doing), **L2 comprehension** (what it means: who is working with whom), **L3 projection** (what happens next: will X post in the next 30 minutes, who speaks next). 11 questions per moment in total. |
| **View** | What the analyst is given. `none` = only the agent list (pure guessing). `dashboard` = the original status board. `dashboard2` = the **improved** board (adds who-talks-to-whom). `dashboard3` = board plus each agent's own plans. `raw` = searches the records itself. `self` = one agent's memory file only. Chat feed = `custom-minimal_dashboard`, the example plug-in. Full table: [HARNESS.md](docs/HARNESS.md#how-a-test-works). |
| **Score** | 0 = wrong, 1 = right, with partial credit on "which agents…" questions. Averaged over questions, then over moments. |
| **"Nothing changes" rule** | The no-intelligence baseline: assume the next couple of hours look like the last half hour. Perfect on L1/L2 by construction (it reads the record correctly); on L3 it is the bar any real foresight must beat. |
| **Analysts** | "Cheap" = DeepSeek V4 Flash; "strong" = Claude Sonnet 5.5. Both via OpenRouter. |
| **Sets** | `v1` = first 26 moments; `v2` = 26 fresh moments used to retest the improved board; `v2r2`/`v2r3` = reruns of `v2` to measure noise; `v2plant3` = the planted-misreport test. |

## How to read the figures

| Figure | What it shows | How to read it |
|---|---|---|
| [fig_design_levels.svg](docs/fig_design_levels.svg) | Each view's score at L1/L2/L3, first 26 moments | Dots further right are better. Bars are margins of error; overlapping bars mean the difference may be luck. The orange line is the "nothing changes" rule. |
| [fig_fresh_levels.svg](docs/fig_fresh_levels.svg) | Same, on the 26 fresh moments, cheap vs strong analyst | As above. Compare `dashboard` with `dashboard2` on L2 to see the improvement from the fix. |
| [fig_forecast_errors.svg](docs/fig_forecast_errors.svg) | Wrong answers on the two "will it happen?" forecasts | Blue (left) = said "no" but it happened; red (right) = said "yes" but it didn't. Mostly blue = analysts bet on activity stopping. |
| [fig_planted_v2plant3.svg](docs/supplement/fig_planted_v2plant3.svg) | Planted misreports caught, by view | Higher catches with fewer false alarms is better. |
| [Supplement figures](docs/supplement/README.md) | Noise between reruns, forecast horizon, swarm size | Each supplement page explains its own figure. |

The one-minute check below prints the same numbers as a table: one row per
set × analyst × view, with the average L1/L2/L3 score.

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

To browse every frozen moment, answer and chart, open the
[explorer](https://dusto-ai.github.io/AI-Village-Grove-Research-Hackathon-2026/explorer_public.html)
(or `docs/explorer_public.html` locally; it works offline). It withholds
the dataset's own text, so to see exactly what each analyst was shown,
build the full explorer (below).

## Replicate it (needs dataset access)

Needs Python 3.12+, [uv](https://docs.astral.sh/uv/), the AI Village export
from Hugging Face, and an OpenRouter key in `$OPENROUTER_API_KEY` (setup
details in [HARNESS.md](docs/HARNESS.md#setup)).

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
