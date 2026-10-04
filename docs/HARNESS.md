# The harness: how it works, and how to reproduce everything

This is the technical reference: what each part of the code does, how
leakage and scoring work, and the exact commands behind every result. For
the findings themselves, read [WRITEUP.md](WRITEUP.md).

## Setup

- **Python 3.12+** and [uv](https://docs.astral.sh/uv/). Run everything
  as `uv run python -m sagat <command>` from the repo root.
- **Data:** gated access to the AI Village dataset
  (huggingface.co/datasets/aidigestorg/ai-village; research-only licence).
  Results here use export revision **`838b4150`** (exported 2026-09-20).
  You need these files from it, about 5 GB compressed:
  - `agents.jsonl.gz`
  - `chat_messages.jsonl.gz`
  - `computer_use_sessions.jsonl.gz`
  - `village_goals.jsonl.gz`
  - `agent_memories.jsonl.gz`
  - `computer_use_turns.jsonl.gz`
- **Model keys (only for running analysts):** OpenRouter models use
  `--model openrouter:<provider/model>`. The key comes from
  `OPENROUTER_API_KEY`, or else the macOS Keychain service `openrouter`
  (change it with `OPENROUTER_KEYCHAIN_SERVICE`). Claude models can also go
  direct: `--model claude-…`, with the key from `ANTHROPIC_API_KEY` or the
  Keychain service `anthropic_api_key`.

```bash
uv run python -m sagat build-data --raw /path/to/hf/files --out data   # ~2 min, several GB
uv run python -m sagat prep                                            # small indexed cache
```

`data/`, `work/`, `results/runs/` and `results/freezes_*.jsonl` are
git-ignored because they hold dataset content. Everything in them
regenerates locally.

## The pieces

| File | What it does |
|---|---|
| `sagat/build_data.py` | Raw export → `data/village.db` + `data/traces.db` (one row per agent action, with reasoning and narration extracted) |
| `sagat/prep.py` | Small indexed cache of chat, sessions, goals and agents |
| `sagat/freeze.py` | Samples freeze moments; builds a **sealed snapshot** per moment |
| `sagat/queries.py` | The 11 questions, their ground-truth extractors, and the "nothing changes" baseline |
| `sagat/dashboard.py` | The status boards the analyst sees (original, + who-talks-to-whom and typical patterns, + agents' plans) |
| `sagat/analyst.py`, `sagat/openrouter.py` | Runs an AI analyst on a moment (Anthropic API or OpenRouter); answers come back through a fixed-format tool |
| `sagat/score.py` | Scoring, per-level averages, paired moment-by-moment comparisons |
| `sagat/plant.py` | Planted-misreport test sets |
| `sagat/explorer.py` | The offline explorer page (full or public) |
| `sagat/figures.py`, `sagat/example.py` | Write-up figures; the worked example |
| `sagat/export.py` | Every answer, truth and score as CSV, with no dataset text |
| `examples/minimal_dashboard.py` | Template: plug in your own dashboard |
| `scripts/` | Supplementary analyses, the reviewer test, and a CSV-only rescorer |

## How a test works

1. **Freeze.** Pick a moment *t* mid-workday with at least 4 agents
   active, and the village still active 1–2 hours later (this avoids trick
   questions at the end of the day).
2. **Seal.** Copy only records timestamped at or before *t* (96-hour
   lookback) into a fresh SQLite file. Drop fields that describe the live
   system's *current* state (balances, statuses, room membership, goal end
   times set later). An automated check confirms nothing postdates *t*.
3. **Ask.** Give the analyst a view of the snapshot and the 11 questions.
   Answers must use agent names from the roster, through a fixed-format
   answer tool.
4. **Score** against truth computed from the full logs, including what
   happened after *t*.

**Views** (`--cond`):

| Condition | The analyst sees |
|---|---|
| `none` | Agent roster and freeze time only (the guessing floor) |
| `dashboard` | Original status board: per-agent task, activity, error rate, chat counts, last 25 messages |
| `dashboard2` | Plus who-talks-to-whom and typical-patterns panels |
| `dashboard3` | Plus each agent's own stated plans |
| `raw` | Read-only SQL over the snapshot, no board |
| `both` | Board + SQL (available, not used in the study) |
| `self` | Only one agent's memory file and its last 30 actions |
| `custom` + `--dashboard file.py` | Your own `render(frozen_db_path, freeze_pt) -> str` |

**Scoring.**
- Pick-several questions get partial credit (F1); an empty answer to an
  empty truth scores 1.
- Pick-one questions are right if they match any tied correct answer.
- Yes/no and multiple choice need an exact match.
- Scores are averaged per moment, then across moments.
- Runs that returned no answers (a provider filter, or a harness failure)
  are excluded and counted separately.
- Comparisons are paired by moment.

## Reproducing every result

Freeze sets are rebuilt exactly from the published timestamps; the seed is
stored in the file:

```bash
uv run python -m sagat freezes --name v1 --times results/freeze_times_v1.txt   # design set
uv run python -m sagat freezes --name v2 --times results/freeze_times_v2.txt   # held-out set
```

| Result | Commands | Approx. cost |
|---|---|---|
| Main study, first 26 moments | `run --name v1 --model openrouter:deepseek/deepseek-v4-flash --cond none,dashboard,raw,self`, then the same with `--model openrouter:anthropic/claude-sonnet-5.5 --cond none,dashboard,self` | $3.60 + $1.90 |
| Improved dashboards, fresh 26 | `run --name v2 --model openrouter:deepseek/deepseek-v4-flash --cond none,dashboard,dashboard2,dashboard3`, then the same with `--model openrouter:anthropic/claude-sonnet-5.5 --cond dashboard2,dashboard3` | $1.30 + $1.30 |
| Chat-feed template | `run --name v2 --cond custom --dashboard examples/minimal_dashboard.py --model openrouter:deepseek/deepseek-v4-flash` | $0.90 |
| Scores and tables | `score --name v1`, `score --name v2` → `results/summary_*.md` | free |
| Figures, worked example | `figures`; `example --name v2 --freeze 20251225T181018Z` | free |
| Explorer | `explorer` (full, local, `work/`) · `explorer --public` (`docs/`) | free |
| Planted misreports | `plant --from v2 --name v2plant3 --real`, then `run --name v2plant3 --cond dashboard,dashboard2,custom --dashboard examples/minimal_dashboard.py --model openrouter:deepseek/deepseek-v4-flash`, then `python scripts/planted.py v2plant3` | $0.80 |
| Run-to-run noise | copy `results/freezes_v2.jsonl` to `freezes_v2r2.jsonl` / `freezes_v2r3.jsonl`, run `dashboard,dashboard2` on each, then `python scripts/variance.py` | $1.55 |
| Error flag, horizon, swarm size | `python scripts/error_flag.py <computer_use_turns.jsonl.gz>`, `scripts/horizon.py`, `scripts/roster_size.py` | free |
| Reviewer test | `python scripts/run_reviews.py docs/reviews` | $0.55 |
| Public export and rescore | `export`, then `python3 scripts/rescore_public.py` | free |

All `run` commands skip moments that already have results, so an
interrupted run resumes. AI analysts don't answer identically every time:
expect level averages within about ±0.05 of ours
([supplement/VARIANCE.md](supplement/VARIANCE.md)).

## Testing your own dashboard

Write `render(frozen_db_path, freeze_pt) -> str` (see
`examples/minimal_dashboard.py` for the snapshot's tables), then:

```bash
uv run python -m sagat show  --name v2 20251225T181018Z --cond custom --dashboard my_board.py   # preview
uv run python -m sagat run   --name v2 --cond none,custom --dashboard my_board.py --model openrouter:deepseek/deepseek-v4-flash
uv run python -m sagat score --name v2
```

To add a question, write a function in `sagat/queries.py` that returns a
`Query` with a truth and a past-only baseline answer (see
`q_focal_partner`), then add it to `TEMPLATES`. For a fuller method guide,
see [supplement/SAGAT_FOR_BUILDERS.md](supplement/SAGAT_FOR_BUILDERS.md).

## Checks built in

- **Leakage:** no snapshot record postdates its freeze, across all 52
  moments.
- **Reproducibility:** a fresh build from the raw export reproduced all 52
  moments, with identical questions and truths.
- **Scoring consistency:** the explorer's scoring matches Python on all
  3,575 analyst answers.
- **Answer key:** an independent SQL re-implementation matched 515 of 515
  truths. The one known validity issue is the dataset's error flag; see
  [supplement/ERROR_FLAG.md](supplement/ERROR_FLAG.md).
