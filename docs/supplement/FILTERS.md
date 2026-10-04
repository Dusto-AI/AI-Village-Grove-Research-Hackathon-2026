# Supplement: which AI overseers go blind on security work?

*Extends finding 7 of the write-up. Cost: $1.32.*

## The question

During the main runs, Claude Sonnet 5.5 refused to analyse both of the frozen moments we had sampled from the two weeks (12–26 January 2026) when the village's goal was
to hack OWASP Juice Shop, a deliberately vulnerable website built for
security training. Is that one provider's filter, or a general problem?

## What we did

We sent the same two prompts the analysts received to six model families
via OpenRouter, for three moments:
- the two security-period moments in our samples (19 and 23 January 2026);
- one ordinary moment (25 December 2025) as a control.

The two prompts were the minimal one (agent list, the 11 questions and the
four task options) and the full status dashboard. DeepSeek V4 Flash,
already tested in the main runs, answered all of these.

## What we found

| Model | Security moments (4 prompts) | Ordinary moment (2 prompts) |
|---|---|---|
| Claude Sonnet 5.5 | **blocked, all 4** (content filter) | answered |
| GPT-6.1 Sol | answered | answered |
| Gemini 3.8 Flash | answered | answered |
| Grok 4.7 | answered | answered |
| Kimi K3 | answered | answered |
| DeepSeek V4 Flash (main runs) | answered | answered |
| Meta Muse Spark 1.3 | not tested: the account needs an age confirmation setting first | |

- **One provider's filter blocked every security-period prompt, and none
  of the others did.** The block happened even with the minimal prompt,
  which contains only agent names, generic questions and short task titles naming the training exercises.
- **The block is consistent:** the same moments were blocked in the main
  runs and again here.

## What it means

- **An oversight tool built on a single model provider can go dark exactly
  when the swarm does something security-sensitive.** Here the activity was
  benign training. In a real incident it might not be, and that's when the
  overseer most needs to see.
- **The failure is visible but uninformative.** The analyst returns
  nothing, not a wrong answer. A dashboard that silently drops the
  analyst's summary would look like "nothing to report".
- **Mitigations:** route oversight queries to a second provider when the
  first refuses; surface refusals loudly rather than as empty results; and
  include security-flavoured moments in any SAGAT test of an AI analyst,
  so the gap shows up before an incident does.
- **Caveat:** a small sample (two moments, one goal period) and one
  wording. Other phrasings, or the provider's own fallback options, may
  behave differently.
