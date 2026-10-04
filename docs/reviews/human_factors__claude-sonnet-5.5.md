## 1. Statements most likely wrong, unsupported, or inconsistent

**1. "A plain dashboard takes an analyst from guessing to perfect on every level. It beat guessing at every one of the 26 moments tested."**
The first table contradicts this. The dashboard is perfect only on perception (1.00). On comprehension it scores 0.71–0.73 and on projection 0.55–0.57. Projection is barely above guessing (0.37–0.44), and the ±0.09 intervals overlap. "Every one of the 26 moments" is not backed by any per-moment result in the document. The section 3 text also says the analyst never beat the rule on forecasting. The headline bullet is the most misleading sentence in the piece.

**2. "scores on that question rose from 0.29 to 0.84"** (In short) versus **"That question rose from 0.58 to 0.84"** (Finding 2)
These are different baselines. 0.29 is the original dashboard on the first 26 moments. 0.58 is presumably the original dashboard on the fresh 26, which is the only like-for-like comparison with 0.84. The summary mixes moment sets and inflates the gain, and it does so in the very place the held-out design was meant to prevent. The 0.29 → 0.58 jump with no change in the dashboard also shows how much the question score varies with the moment set. That undermines confidence in a single 26-moment retest.

**3. "the wrong answers were overwhelmingly 'yes, that will happen' when it didn't: 16–17 such errors against 1–3 the other way."**
This is backwards relative to the table. The 16–17 figures are in the column "wrongly said 'no'". The headline claim, "betting that activity will stop", matches the table, not this sentence. As written, the explanation describes the opposite bias to the one claimed. Either the prose or the column labels are wrong, and a reader cannot tell which finding is real.

**4. "That held for both models and both sets of moments."**
The table does not cross these factors. The strong model appears only on the first 26 with the original dashboard. The fresh-26 original dashboard appears only with the cheap model. The claim is therefore partly untested. The related claim that "typical patterns… nearly halved that bias" is also confounded. The improved dashboard bundled the interaction panel and the typical-patterns history, so the effect can't be attributed to patterns. The error totals also fell only modestly (20 → 16 for cheap), so the bias shifted more than accuracy improved.

**5. "A dashboard is enough for the present, and digging through raw data isn't better, just pricier."**
The same paragraph says raw records scored better on comprehension (0.85 vs 0.71), and the table agrees. The finding only holds after the fix, which the text itself calls a blind spot. The "slightly worse" 0.88 on perception carries ±0.12, so it is not distinguishable from 1.00. The "4× as much" cost figure appears nowhere else in the document and is cited only to a notebook entry.

**6. "The obvious 'error rate' metric is about 40% noise in this dataset"**
The body says "a rough text check suggests about 40%". The headline drops that hedge. There is no description of how "normal output" was classified, no validation, and no precision or recall. The limitations section admits one question ("whose actions produce errors") is scored against this contaminated flag. The question's scores (0.04) are therefore uninterpretable, yet they are still reported as findings. The "515 of 515 recomputed answers matched" safeguard shows only that the key is reproducible, not that it is valid. The write-up conflates the two.

## 2. What confused or felt counter-intuitive

- **Calling the "nothing changes" rule "perfect by construction" and using it as a ceiling.** It is computed from the same record as the answer key, so scoring 1.00 says nothing about SA. It is an oracle, not a competitor. For projection it is a reasonable persistence baseline, but the paper treats the two roles interchangeably.
- **Why the improved dashboard scores 0.84 and not about 1.0 on "who has X been talking to".** If the panel displays the quantity, remaining errors are about reading or reasoning, and that deserves discussion. It also makes the "fix" partly circular: you added the answer to the screen and the question became answerable.
- **"Does the swarm know its own state?" as the motivation for the single-agent-memory condition.** An LLM given one agent's memory and its last 30 actions is not that agent's awareness. The construct slides from "agent self-knowledge" to "an analyst's inference from a partial view".
- **The "lower bound" claim in finding 5** is asserted without evidence. Unrecorded conversations could just as easily be irrelevant.

## 3. Where an example, image, or definition is most needed

- **A worked example of one frozen moment:** the dashboard as shown, one question per level, the key, and an LLM answer, right and wrong. At present I can't judge how question scoring works. Is "who has gone quiet" set-overlap, exact match, or F1? How is a yes/no forecast scored against a 0.5 chance rate?
- **Definitions of "cheap" vs "strong"** appear only in passing, and "± " is never defined (SE? CI? across moments? across questions?).
- **A picture of the original vs improved dashboard.**
- **The base rates for the two yes/no forecasts.** The bias analysis means nothing without them. If a human post occurs in 70% of windows, "no" errors are expected.
- **Which analysts failed in which blocked moments, and how those were excluded from means.**

## 4. What I'd most want added or changed

- **Fidelity to SAGAT (and SPAM).** In SAGAT, displays are blanked during queries and freezes are randomized. Here the analyst has the dashboard in front of it while answering, and the moments were selected ("mid-workday with real activity"). That is closer to SPAM (query with the display present), or just a retrieval test. Level 1 scoring 1.00 reflects lookup, not memory or awareness. Say so, and either adopt SPAM terminology or run the blanked mode.
- **No operator goals or task.** SA is defined relative to goals and decisions. Here the questions are countable proxies, as the limitations section admits, and nothing links them to an overseer's decisions. Also report whether answers were necessary for any oversight decision.
- **The "Live SAGAT studies rarely manage this" claim** is overstated. Projection items scored against simulator ground truth are standard in SAGAT.
- **Paired statistics.** The text promises moment-by-moment comparisons but reports unpaired-looking ± values. Give paired differences with intervals, especially for "tie" claims. A tie at n=26 with SE ≈0.07 is not evidence of equivalence, and "no evidence that plans add anything" is absence of evidence. Plans scored lower than no plans in the cheap row (0.60 vs 0.62).
- **A per-question table** rather than level averages.
- **An ablation of the two dashboard changes** (interaction panel vs typical patterns).
- **Leakage beyond timestamps.** The check shows no records dated after the freeze, but the models may have seen this public swarm in training data.
- **Transfer.** The swarm has 6–32 agents, while the framing is thousands. Human results are absent, so claims about "anyone understanding the swarm" in the title are unsupported. An LLM's lookup success says little about operator workload, time pressure, or attention.
- **The 515 vs 572 discrepancy** (52 × 11): explain it.

## 5. Ver