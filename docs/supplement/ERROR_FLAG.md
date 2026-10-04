# Supplement: the "error" signal, and why an error-rate panel misleads

*Supports finding 6 of the write-up. Script: `scripts/error_flag.py`; no
model calls.*

## The question

The AI Village dataset marks each agent action with an `error` field. The
natural dashboard panel, "error rate in the last hour", which our own
dashboard has, is built on it. How much of what it flags is a real failure?

## What we did

1. We read every flagged action in the dataset: 153,245 of them.
2. We sorted each one with simple rules:
   - **Tool errors** (e.g. the screen-clicking tool failing to find a button)
     always count as genuine failures.
   - **Command-line errors** count as **harmless** when the error text looks
     like normal output of a successful command: a code push ("main ->
     main"), a branch switch, a download progress meter, a warning. They
     also must contain no failure words ("error:", "fatal", "not found",
     "Traceback", "timed out", …). Anything else counts as a genuine
     failure.
3. We hand-checked 20 random examples from each class.
4. We recomputed "who is failing most" at all 52 frozen moments using only
   genuine failures.

## What we found

| | Flagged actions | Share |
|---|---|---|
| Command-line, harmless by the rules | 62,475 | 40.8% |
| Command-line, failure by the rules | 75,547 | 49.3% |
| Tool errors (always failures) | 15,223 | 9.9% |

**The rules undercount the harmless share.** All 20 sampled "harmless"
cases really were harmless. But of 20 sampled "failures", 5 were harmless
too: a web server logging a successful request, a successful file checkout,
a "binary file matches" note, a browser start-up warning and a tool's
version banner. So the true harmless share is likely **between about 40%
and 60%** of everything flagged. The sample is too small to be more
precise.

**It changes the answer that matters.** Even with the conservative rules,
removing harmless output changes **who counts as "failing most" at 14 of 48
moments**, nearly a third. (The other 4 moments had no flagged actions at
all.)

## What it means for dashboard builders

- An "error rate" panel built on raw stderr would point an overseer at the
  wrong agent about a third of the time in this swarm, and would make
  healthy, busy agents look like they're failing.
- **Your answer key inherits the same flaw.** Our own question "whose
  actions are failing most?" was scored on the raw flag. That's why we
  relabelled it "whose actions produce the most error output". An analyst
  that reads the dashboard's error column scores well on it while being
  told the wrong thing.
- **The fix is cheap:** classify errors by what they say, or better, record
  the command's exit status. The rules here are a starting point, not a
  solution. They catch the obvious cases (pushes, progress meters) and
  miss subtler ones (server logs, warnings without the word "warning").
- **The general lesson:** before building a panel on a field, read a random
  sample of what the field actually contains.
