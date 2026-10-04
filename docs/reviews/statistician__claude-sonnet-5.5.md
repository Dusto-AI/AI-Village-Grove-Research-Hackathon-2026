## 1. Statements most likely wrong, unsupported, or inconsistent

**a. "A plain dashboard takes an analyst from guessing to perfect on every level. It beat guessing at every one of the 26 moments tested."**
- The first results table contradicts this. The dashboard scores 0.71–0.73 on comprehension and 0.55–0.57 on projection, which is not perfect.
- On projection, the cheap dashboard (0.55 ± 0.09) is barely distinguishable from cheap guessing (0.44 ± 0.08). "Every one of the 26 moments" is very unlikely at that margin.
- No per-moment win count is shown for this claim. The only per-moment count in the document is "7 better, 1 worse" in finding 2.

**b. "scores on that question rose from 0.29 to 0.84"** (In short) versus **"That question rose from 0.58 to 0.84"** (finding 2)
- These are inconsistent. The 0.29 is the original dashboard on the first 26 moments. The 0.58 is presumably the original dashboard on the fresh 26.
- The headline therefore compares different moment sets, which undermines the "moment-by-moment, held-out" safeguard. The like-for-like gain is 0.58 → 0.84.
- The original dashboard also scored higher overall on the fresh set (0.80 vs 0.71 on comprehension), so the moment sets differ in difficulty.

**c. "the wrong answers were overwhelmingly 'yes, that will happen' when it didn't: 16–17 such errors against 1–3 the other way."**
- This is reversed relative to the table. The 16–17 figures are in the column "wrongly said 'no'".
- The summary ("betting that activity will stop") matches the table, but the finding 4 text says the opposite. Either the prose or the column labels are wrong, and a reader can't tell which.

**d. "Showing analysts 'typical patterns' nearly halved that bias"**
- The typical-patterns history was bundled with the new interaction panel, so the effect cannot be attributed to it.
- Total errors barely moved for the cheap model: 20 → 16, with "yes" errors rising from 3 to 7. Much of this is a swap of error types, not an improvement.
- The strong improved-dashboard row has no strong original-dashboard counterpart on the fresh set, so there is no clean "before".
- With about 52 yes/no items per row, differences of a few errors are noise.

**e. "digging through raw data isn't better, just pricier… It did better on 'what it means' (0.85 vs 0.71), largely because of the blind spot below. And it cost about 4× as much."**
- The sentence contradicts itself: raw data is "not better" yet better on comprehension.
- The 0.85 vs 0.71 gap sits inside the ± of 0.10–0.11 on each side.
- "Largely because of the blind spot" is asserted with no per-question breakdown.
- The 4× cost figure appears nowhere else in the document.
- The 0.88 vs 1.00 "slightly worse" has ± 0.12, so it is also noise.

**f. "we found no evidence that what agents *say* they'll do adds anything"**
- The data are underpowered to show this. Plans moved the cheap model from 0.62 to 0.60 and the strong model from 0.65 to 0.67, with SEs of about 0.07 on n = 26.
- That is absence of evidence, not evidence of absence.
- The "best combination" (0.67) was also selected post hoc from about six variants, which invites winner's-curse reading.
- The headline "Nothing beat 'nothing changes'" is fair as a description. The explanatory claims built on it ("fixing it doesn't produce foresight", "plans add nothing") are not supported.

**g. "The obvious 'error rate' metric is about 40% noise in this dataset"**
- The basis is "a rough text check" on a sample of flagged actions. There is no validation of the check, no confidence interval, and no statement of how the sample was drawn.
- A heuristic misclassification rate is presented as a dataset-level fact in the headline.
- The finding 5 numbers are also unsupported: "whose actions produce errors (0.04)" and "human recently posted (0.23–0.24)". The human-post score is below chance for a yes/no question. This is odd and unexplained, and it may reflect a bug or a question-format issue.

**Smaller items**
- "515 of 515 recomputed answers matched" does not equal 52 × 11 = 572 answers. The gap is unexplained.
- "A safety filter blinded the overseer, twice… exactly the activity an overseer would most want to see" draws a conclusion from n = 2. Excluding blocked runs from scoring also biases the strong-model results.

## 2. What was confusing or counter-intuitive

- What "±" means. SE, SD, or CI? Is it across moments or across questions? It is never defined.
- How a score is computed on projection questions. Accuracy, or some mix of set overlap and yes/no? The rule's 0.59 and 0.65 are presented without any uncertainty.
- A "dashboard" analyst scores 1.00 on perception, yet the "nothing changes" rule is called the "ceiling" because it is perfect "by construction". That makes the perception and comprehension levels close to trivial, and the headline "perfect" mostly shows the questions are countable from the dashboard.
- Why a human posting in the last 30 minutes scores 0.23 for the memory analysts. That is worse than coin-flipping.

## 3. Where an example or clearer explanation is most needed

- One worked example of a moment: the dashboard as shown, one question, the analyst's answer, the key.
- A concrete example of the forecast questions and how "yes/no" correctness is scored.
- The "typical patterns" panel and the interaction panel. What do they contain?
- How the cost multiples (4×, 70–180×) were computed.
- A per-question table for comprehension. Finding 2 hinges on one question, and others may have moved the other way.

## 4. What I would most want added or changed

- Define the error bars, and give paired per-moment differences with CIs or sign tests. For example, 7 better vs 1 worse is p ≈ 0.07 two-sided, not clearly significant.
- Ablate the improved dashboard: interaction panel alone versus typical patterns alone, rather than bundling them.
- Run the original dashboard with the strong model on the fresh set, so there is a matched comparison.
- Count the comparisons made (views × levels × questions) and either correct for them or label the findings as exploratory.
- Fix the 0.29 / 0.58 and "yes"/"no" inconsistencies, and soften "perfect on every level".
- Validate the error-flag heuristic against a hand-labelled subset, and report its precision.
- State the base rate of "yes" for the forecast questions, and the rule's accuracy on them.
- Explain the 515 vs 572 answer count.
- Present the 7 blocked-run and plan findings as anecdotes, not as findings.

## 5. Verdict

The idea of applying SAGAT to a recorded swarm, with a "nothing changes" baseline and a held-out retest, is good, and the headline negative result on forecasting is plausible. The write-up undermines itself with internal contradictions (0.29 vs 0.58, reversed yes/no direction, "perfect on every level" against its own table). It also draws causal and "no effect" conclusions from n = 26, undefined error bars, bundled interventions, and uncorrected comparisons. As a methodology proposal it is persuasive. As empirical evidence for the specific findings, it is not yet.