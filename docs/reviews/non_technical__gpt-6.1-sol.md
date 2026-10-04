## 1. Statements most likely wrong, unsupported or overstated

**1. “A plain dashboard takes an analyst from guessing to perfect on every level.”**

This is plainly contradicted by both results tables. On the first 26 moments, the cheap dashboard analyst scored **1.00, 0.71 and 0.55** across the three levels. Even the best combination on the fresh moments scored **1.00, 0.93 and 0.67**. That is not “perfect on every level.” The evidence supports near-perfect answers about current activity—not perfect understanding or forecasting.

**2. “We added that, retested on 26 *fresh* moments, and scores on that question rose from 0.29 to 0.84.”**

This mixes two sets of moments and makes the improvement look larger than the direct comparison supports. Finding 2 says the original dashboard scored **0.58 on the fresh moments**, rising to **0.84** after the changes. The earlier **0.29** came from the first set.

The clean comparison is **0.58 versus 0.84 on the same fresh moments**. Also, you added both an interaction panel and history information, so this does not isolate which addition caused the improvement.

**3. “On the yes/no forecasts, the wrong answers were overwhelmingly "yes, that will happen" when it didn't: 16–17 such errors against 1–3 the other way.”**

This reverses the table immediately above it. The table reports **16–17 wrongly said “no”**, versus **1–3 wrongly said “yes.”**

The table supports the section’s headline—analysts incorrectly expected activity to stop—but this sentence says the opposite. This is a major proofreading error because it reverses the explanation of the main forecasting failure.

**4. “A dashboard is enough for the present, and digging through raw data isn't better, just pricier.”**

Your own table shows raw records doing **better on “what it means”: 0.85 versus 0.71**. The paragraph even acknowledges that improvement.

You can say raw records were more expensive and worse at identifying current activity. You cannot fairly summarise them as “isn't better, just pricier” when they improved one of your three main measures. Nor does a perfect score on four narrow activity questions establish that a dashboard is “enough for the present.”

**5. “Dashboards and "analyst agents" are being built to help, but almost nobody tests whether they actually improve anyone's understanding.”**

No evidence is provided for “almost nobody.” There is no survey, comparison with other projects or supporting reference.

More importantly, this write-up itself does not test whether dashboards improve **people’s** understanding: the limitations explicitly say you tested AI analysts, not people. That does not invalidate the experiment, but the opening makes its relevance to human overseers sound more established than it is.

## 2. What confused me or felt counter-intuitive

- **The “nothing changes” rule somehow knows the present perfectly.** A forecasting rule should predict the future. Here it also gets perfect scores for current facts “by construction.” It sounds as though one row combines an answer key for the present with a prediction rule for the future. Those are different things and should be labelled separately.

- **Much of “what it means” appears to be counting.** Who talks to whom most, who has gone quiet and who produces flagged errors are useful facts. But how do they demonstrate that an analyst understands the swarm’s situation? I expected questions about stalled work, coordination failures or whether a goal is in trouble.

- **Your version of SAGAT may test reading rather than retained understanding.** The aviation example blanks the screens before questioning. Later, the human explorer has a special “classic mode” that hides the dashboard. Did the AI analysts keep access to the dashboard while answering? That distinction matters.

- **I cannot interpret the scores confidently.** Does 0.84 mean 84% of answers were completely correct, or partly correct answers earned points? What does “±” mean? Why is 0.67 versus 0.65 a tie, but other differences are treated as improvements?

- **The verification count does not explain itself.** There are 52 moments and 11 questions, which suggests 572 answers. Why were 515 answers independently checked? There may be a straightforward reason, but it is missing.

## 3. Where an example, image, definition or clearer explanation is most needed

**Most urgently: show one complete worked example.** Give a frozen moment, the dashboard the analyst saw, one question, its answer, the correct answer and how the score was calculated. That would make the entire experiment much easier to evaluate.

Also needed:

- **A before-and-after dashboard image**, highlighting the new interaction panel and history information.
- **A concrete “nothing changes” example** for each forecasting question, especially “Who speaks next?”
- **A short scoring explanation:** what 0–1 means, partial credit, the “±” values and how blocked runs affect comparisons.
- **An error-flag example:** one genuinely failed action and one successful action incorrectly flagged as an error.

## 4. What I would most want added or changed

1. **Fix the three obvious numerical or directional problems first:** “perfect on every level,” the 0.29-to-0.84 comparison and the reversed yes/no errors.
2. **Make the central claim narrower:** this is evidence about AI analysts answering specific log-based questions in one small swarm—not yet evidence that people understand swarms better.
3. **Add a practical oversight scenario.** What important mistake could an overseer avoid with this dashboard? Accurate counts are not automatically useful understanding.
4. **Explain whether the test rewards understanding or copying displayed answers.** Both can be useful, but they are not the same achievement.
5. **Clarify the contaminated error question’s consequences.** Did you recalculate results without it? Rebuilding an answer key identically verifies consistency, not whether its definition captures actual failures.
6. **Make the evidence accessible in the write-up itself.** Notebook entry numbers are not substitutes for the few essential details needed to judge each claim.

## 5. Overall verdict

The practical argument—test a dashboard, identify missing information, fix it and retest—is convincing. The stronger claim that this demonstrates improved understanding is not yet convincing: the study tests AI answers to narrow questions, and several prominent summaries contradict the results. Fix those contradictions and distinguish accurate information retrieval from genuine understanding, and this becomes a much more credible write-up.