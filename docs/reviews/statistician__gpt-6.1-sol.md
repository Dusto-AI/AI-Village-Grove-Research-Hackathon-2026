## 1. Statements most likely wrong, unsupported, or inconsistent

### 1. “A plain dashboard takes an analyst from guessing to perfect on every level.”

**Directly contradicted by both tables.** On the first 26 moments, dashboard comprehension scores are 0.71–0.73 and forecasting scores are 0.55–0.57. Even perception is 0.99, not perfect, for the stronger model. On the fresh moments, no dashboard configuration reaches perfection in comprehension or forecasting.

The supported claim is much narrower: the dashboard makes **the tested perception questions almost perfectly answerable by these AI analysts**. That is not perfection “on every level,” nor evidence that it improves human understanding.

### 2. “We added that, retested on 26 *fresh* moments, and scores on that question rose from 0.29 to 0.84.”

**This mixes improvement from the intervention with differences between samples.** The detailed results say the original dashboard scored **0.58 on the fresh moments**, versus 0.84 for the improved dashboard. The same-moment improvement is therefore **0.26**, not 0.55.

The original dashboard itself went from 0.29 on the development set to 0.58 on the fresh set. That large difference makes the misleading comparison especially consequential. Report both comparisons, but use **0.58 → 0.84** to describe the tested improvement. Also, you added both an interaction panel and history: without separate conditions, you cannot isolate which addition caused the gain.

### 3. “On the yes/no forecasts, the wrong answers were overwhelmingly "yes, that will happen" when it didn't: 16–17 such errors against 1–3 the other way.”

**The error direction is reversed.** The table labels the 16–17 errors as **“wrongly said 'no'”**, and the 1–3 errors as **“wrongly said 'yes'.”** The prose describes false positives; the table describes predominantly false negatives.

The heading and summary agree with the table: analysts supposedly predict activity stopping when it actually continues. Fix the prose—or, if the prose is right, fix the table and the central interpretation.

### 4. “A dashboard is enough for the present, and digging through raw data isn't better, just pricier.”

**Your own numbers show a meaningful advantage for raw data on comprehension:** 0.85 versus 0.71 for the cheap dashboard analyst. You acknowledge this immediately afterward.

Raw data performs worse on perception and better on comprehension. That is a trade-off, not “isn't better.” If you want an overall ranking, specify how the levels are weighted and whether the score improvement justifies the additional cost. Otherwise say the dashboard is cheaper and better for the tested perception tasks, while raw access helps with information the dashboard omits.

### 5. “No view, model or panel beat "nothing changes" at forecasting.”

**Too categorical for the evidence presented.** The best reported score is **0.67 versus 0.65**: it beats the baseline numerically. You may mean that no configuration demonstrated a statistically reliable improvement, but the write-up does not provide the paired difference, its confidence interval, or a test.

Likewise, calling this “a tie” turns uncertainty into equivalence. Failure to establish superiority does not establish equal performance. With 26 moments and many configurations tried, the defensible conclusion is: **no clear forecasting improvement was demonstrated in this experiment**. Show paired uncertainty and disclose how the multiple comparisons were handled.

### 6. “The obvious "error rate" metric is about 40% noise in this dataset,”

**The supporting analysis measures something narrower and less certain.** A rough text check classified about 40% of **60,000 flagged actions** as normal output. That estimates possible contamination among flagged actions—not the overall error rate’s measurement error, the false-positive rate among all successful actions, or the accuracy of agent rankings.

There is no sampling method, manual validation, or classifier accuracy reported. False negatives are also unexamined. The evidence supports “many error flags appear to be normal output,” not a precise characterization of the metric as “40% noise.”

## 2. What confused me or felt counter-intuitive

- **515 verified answers versus 572 nominal answers.** There are 52 moments and 11 questions per moment: 572 possible answers. Why were only 515 recomputed? Some questions may be inapplicable, but the missing 57 need an accounting. This is not necessarily an error; it is an unexplained denominator.
- **The “nothing changes” baseline is actually two different things.** For perception and comprehension it is an oracle answer key, perfect by construction. For forecasting it is a persistence heuristic. Putting both under one label obscures the distinction.
- **More false negatives do not, alone, establish a behavioral bias.** If positive outcomes are much more common, false negatives may dominate even without a special tendency to predict inactivity. Show outcome prevalence, prediction frequencies, and class-conditional error rates.
- **The information-access rules are unclear.** You remove material describing the live system’s current state, yet the dashboard reports current status. Is status reconstructed from historical logs? What exactly is removed, and from which conditions?
- **“Blocked or broken runs counted separately” leaves the score denominators unclear.** Excluding blocked security-related cases can make successful-run performance look better than operational performance. Both should be reported.

## 3. Where an example, image, definition, or clearer explanation is most needed

**One complete worked freeze is the highest-value addition.** Show:

1. What the analyst can see.
2. The exact 11 questions.
3. The ground-truth answers.
4. The analyst’s answers and awarded scores.
5. The persistence baseline’s predictions.

That would expose whether the dashboard supports inference or simply displays the answers.

Also define:

- What every **±** means: standard deviation, standard error, or confidence interval.
- How partial credit, ties, missing answers, and multi-agent answers are scored.
- The operational meanings of “working,” “quiet,” “talking to,” and “errors.”
- How each forecasting question maps to the persistence rule.
- Whether the dashboard remains visible during answering. Your description of classic SAGAT blanks the display; an open-dashboard task measures something different.

## 4. What I would most want added or changed

- **Correct the headline contradictions first.** They undermine confidence in the otherwise useful results.
- **Publish denominators and exclusions for every condition**, including usable moments, questions scored, blocked runs, and broken runs.
- **Report paired differences with uncertainty**, preferably respecting clustering by moment and possible dependence between nearby dates. Explain moment selection and whether model runs were repeated.
- **Separate development from held-out evidence.** Use the fresh-set original dashboard as the comparison for the improved dashboard, and disclose which additional variants were selected after seeing held-out results.
- **Add stronger forecasting baselines:** always-yes/always-no for binary questions, historical prevalence, and simple agent-specific persistence. A single persistence rule is not enough to establish that useful forecasting is unavailable.
- **Validate the error labels manually** on a documented sample before treating error-related answers as ground truth. Rebuilding the same answer-key logic independently checks implementation consistency, not whether the target represents genuine failures.
- **Narrow the scope of the claims.** This evaluates AI answers to countable questions about one swarm. Human situation awareness, oversight decisions, and general swarm safety remain untested.

## 5. Overall verdict

The core argument—that dashboards should be evaluated with explicit questions, held-out moments, and simple baselines—is convincing. The claimed empirical success is not yet convincing as written: major summary statements contradict the tables, and the forecasting conclusions exceed the uncertainty analysis provided. This is a useful pilot with a promising evaluation loop, not evidence of perfect understanding or forecasting equivalence.