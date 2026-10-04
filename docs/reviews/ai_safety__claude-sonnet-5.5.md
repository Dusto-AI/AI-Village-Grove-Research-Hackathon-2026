## 1. Statements most likely wrong, unsupported, or overstated

**a. "A plain dashboard takes an analyst from guessing to perfect on every level. It beat guessing at every one of the 26 moments tested."**
The document's own table contradicts this. The cheap dashboard scores 0.71 on "what it means" and 0.55 on "what happens next". The strong dashboard scores 0.73 and 0.57. Only perception is perfect. On forecasting, the dashboard (0.55 ± 0.09) is barely separable from cheap guessing (0.44 ± 0.08) and is below the "nothing changes" rule (0.59). "Beat guessing at every one of the 26 moments" is not supported anywhere in the body. It is also implausible for a metric this noisy, and for perception it is trivial anyway, since the answers are lookups.

**b. "scores on that question rose from 0.29 to 0.84"**
The summary and the body disagree. The body says the original dashboard scored 0.29 on the first 26 moments. The fresh-set comparison, the only valid held-out one, is "0.58 to 0.84". The headline stitches a pre-fix score on the design set to a post-fix score on the held-out set, which inflates the effect. Also, the "improved" dashboard bundled two changes, an interaction panel and "typical patterns" history. The gain cannot be attributed to the fix the text credits.

**c. "the wrong answers were overwhelmingly 'yes, that will happen' when it didn't: 16–17 such errors against 1–3 the other way."**
This is backwards relative to the table and the summary. The table shows 16–17 "wrongly said 'no'" against 1–3 "wrongly said 'yes'". The bias is predicting that activity stops, as the summary says, and the body text inverts it. "That held for both models and both sets of moments" is also not shown. There is no row for the strong model with the original dashboard on the fresh set.

**d. "Showing analysts 'typical patterns' nearly halved that bias" / "Showing typical patterns roughly balanced the errors."**
Again, the improved dashboard changed several things at once. "Wrongly yes" errors rose from 3 to 7 for the cheap model, so this looks like a threshold shift, not better calibration. Total errors went from 20 to 16, which is not meaningful at this n. The document concedes the result is a tie with the baseline. "Halved" is a framing of a bias swap.

**e. "digging through raw data isn't better, just pricier" … "It did better on 'what it means' (0.85 vs 0.71), largely because of the blind spot below."**
The first sentence is contradicted by the second. Raw access was substantially better on comprehension (0.85 vs 0.71), and was tested only with the cheap model. "Largely because of the blind spot" is asserted with no per-question breakdown. The "4× cost" claim is also confounded by the raw-records condition being a different kind of task (SQL agent loops).

**f. "The obvious 'error rate' metric is about 40% noise in this dataset"**
The evidence is "a rough text check" on a sample of flagged actions. It estimates a false-positive share among flagged actions at best. It does not measure how noisy the metric is, because false negatives are not assessed. The check itself is unvalidated. This also undermines the results that use the flag. The "whose actions produce errors" score (0.04) may reflect a bad answer key, not analyst failure. The "nothing changes" rule's "perfect by construction" status on that question is vacuous if the key is wrong. The "515 of 515 recomputed answers matched" check cannot catch this, because a rebuild from the same flag reproduces the same flaw.

*(Also overstated: "A safety filter blinded the overseer… exactly the activity an overseer would most want to see." Practice exercises on deliberately vulnerable sites are not evidence of dangerous swarm behaviour, and two blocked runs show nothing about oversight coverage.)*

## 2. What confused me or felt counter-intuitive

- The "nothing changes" rule is "perfect by construction" on levels 1–2. If a trivial counting script gets 1.00 on "comprehension", then those questions test retrieval, not comprehension. That makes "the dashboard reached 0.99/1.00" uninteresting, and it undercuts the SAGAT framing.
- The "who has X talked to" numbers (0.29, 0.58, 0.84) come from different sets and conditions, and the reader has to reconstruct which is which.
- 52 moments × 11 questions is 572, but the answer-key check covers 515. The gap is never explained.
- The framing is "thousands of agents" and "incidents that motivated this hackathon". The data is one village of 6–32 agents doing mostly benign work.
- Plans appear to help the strong model (0.65 → 0.67) and hurt the cheap one (0.62 → 0.60). The text reads both as "no evidence", with no power discussion.

## 3. Where examples or clearer explanation are most needed

- One worked example of a frozen moment: what the dashboard shows, the question, the truth, and an analyst answer, especially for the yes/no forecasts and for "who has gone quiet".
- The exact definitions of the three scored levels. Is each question scored as exact match, set overlap, or something else? What does 0.58 mean for a "who has X talked to" question?
- A table of per-question scores, not only per-level, to show which question the improvement came from.
- How the "nothing changes" rule answers each forecast question, and why it scores 0.59 and 0.65 on the two sets.
- What "typical patterns" and the "agents' plans" panels contain.

## 4. What I'd most want added or changed

- **Threat-model linkage.** Which dangerous swarm behaviours (collusion, deception, goal drift, cascading failures, resource grabbing) would these questions catch? Currently none of the 11 questions probes anything adversarial or safety-relevant. Even one safety-relevant question, such as "is any agent acting outside its assigned task?", would help.
- **Honest statistics.** Give confidence intervals on the rule's score, paired differences with CIs for key comparisons, and a power statement. "No evidence" at n=26 is not "no effect".
- **Ablations.** Separate the interaction panel from the typical-patterns panel. Test the strong model on raw records. Run more than one agent for the memory condition.
- **Leakage check beyond timestamps.** Agent memory files and summaries can reference future events, so a date filter is insufficient.
- **Answer-key validity, not just reproducibility.** Fix or drop the error-flag question and re-score. Consider how missed or blocked runs bias the strong-model averages.
- Reframe the claim. This tests whether an LLM can read a static summary, not whether a human overseer's awareness improves. The human-study "Try it yourself" tab is an invitation, not evidence.
- Fix the inconsistent headline numbers (a–c above).

## 5. Verdict

The idea is good. Porting SAGAT to logged swarm data and insisting on a "nothing changes" baseline is a useful methodological contribution, and the held-out retest loop is the right practice. But the headline claims are sloppier than the data. Several are contradicted by the write-up's own tables or text (perfect on every level, 0.29 vs 0.58, the inverted error direction). The questions mostly test retrieval of counts, and nothing connects them to dangerous swarm behaviour. I'd treat this as a promising evaluation template, not as evidence about oversight quality.