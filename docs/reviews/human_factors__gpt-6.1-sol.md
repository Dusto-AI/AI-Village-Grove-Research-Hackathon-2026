## 1. Statements most likely wrong, unsupported, or overstated

### A. The headline contradicts the results

> **A plain dashboard takes an analyst from guessing to perfect on every level.**

Your own tables disprove this. On the first 26 moments, the cheap dashboard analyst scored **1.00, 0.71, and 0.55** across the three levels; the strong analyst scored **0.99, 0.73, and 0.57**. Neither was perfect on every level. Even the improved dashboard was not.

Change this to “The dashboard substantially improved answers about recent activity.” That is supported; the current headline is not.

### B. The improvement claim mixes different test sets

> We added that, retested on 26 *fresh* moments, and scores on that question rose from 0.29 to 0.84.

Later, you report that the question rose **from 0.58 to 0.84 on the fresh moments**. That is the relevant same-moment comparison. The 0.29 score came from the first set, so comparing it directly with 0.84 confounds the display change with differences between moments.

Lead with **0.58 → 0.84 on held-out moments**. Also, you added both an interaction panel and history information. Without an ablation, the improvement cannot be attributed exclusively to the interaction panel.

### C. The explanation of forecast errors reverses the table

> On the yes/no forecasts, the wrong answers were overwhelmingly "yes, that will happen" when it didn't: 16–17 such errors against 1–3 the other way.

The table says the opposite: **16–17 wrongly said “no,” versus 1–3 wrongly said “yes.”** The heading and summary—analysts betting that activity will stop—agree with the table, not this sentence.

This is a substantive reversal of the error mechanism. Correct it, then report false-negative and false-positive **rates**, with their denominators. Error counts alone do not establish response bias when the event base rates may differ.

### D. The recommended procedure is not classic SAGAT

> Freeze a moment, show your tool, ask, and score against the record.

That describes a static information-retrieval or display-use test unless the tool is removed before questioning and the analyst has first been engaged in a representative operational task. Your own method description says classic SAGAT freezes the task and blanks the displays. Here, display hiding appears only as an optional mode in the human self-test; the AI procedure does not clearly establish it.

Access to the dashboard during questioning can measure finding or reading an answer, rather than awareness acquired during oversight. Call this a **SAGAT-inspired frozen-snapshot benchmark**, unless you demonstrate the missing procedural elements. Hiding a board alone would still not recreate ongoing supervisory work.

### E. The justification for projection scoring overclaims both the logs and SAGAT

> **even "what happens next" can be scored**, because the future has already happened. Live SAGAT studies rarely manage this.

SAGAT already includes projection questions; scoring them is not an unusual breakthrough. Simulation studies can use known scenario dynamics, system trajectories, and expert-defined criteria.

More importantly, an observed future is ground truth for **what happened**, not necessarily for **what was reasonably foreseeable at the freeze**. A sound prediction can lose to an unpredictable human intervention. Your retrospective scoring is legitimate as a forecasting benchmark, but it does not automatically validate these questions as Level 3 situation-awareness measures. That distinction needs to be explicit.

### F. Failure to demonstrate superiority is presented as a tie

> **Nothing beat "assume nothing changes" at forecasting.** Not a much stronger model, raw data access, history panels, or the agents' own written plans. The best combination scored 0.67 against the rule's 0.65, a tie.

The best combination **did numerically beat** the baseline. Whether that difference is distinguishable from noise is a separate question. You do not define the reported ± values, provide an uncertainty interval for the **paired difference**, or specify an equivalence margin.

“No demonstrated improvement” is defensible; “a tie” is not established. The same problem affects the conclusion about plans: a small, inconclusive comparison does not show that plans add nothing.

## 2. What confused me or felt counter-intuitive

- **The “nothing changes” rule is also a perfect present-state oracle.** Persistence forecasting and exact retrospective log queries are different things. Combining them in one row makes a forecast baseline look like a universally superior analyst. Separate the oracle ceiling from the persistence predictor.

- **Most “comprehension” questions look like perception or aggregation questions.** Counting interaction partners, inactivity, or flagged errors does not necessarily test understanding of operational meaning. Where are questions about dependencies, conflicting goals, bottlenecks, or consequences?

- **The study criticizes the error flag but still treats it as truth.** Matching independently rebuilt answers verifies computational consistency, not that “whose actions produce the most errors?” measures actual failures. A perfectly reproduced bad label remains a bad label.

- **“Logs everything” sits uneasily with the later claim that recent conversation is not retained.** Define the recording boundary. Missing conversational context matters to both the memory comparison and the claim that answers are already in the record.

- **The 515-answer audit is unexplained.** Fifty-two moments with 11 questions gives 572 potential answers. Why were 515 recomputed? There may be a valid explanation, but the reader needs it.

- **Blocked runs are operational failures, not merely statistical housekeeping.** Keeping them separate from answer accuracy is reasonable. But an overseer unavailable during security-related activity is a serious outcome. Report availability alongside accuracy, especially because missingness is not random.

## 3. Where examples, images, definitions, or clearer explanations are most needed

**Show one complete freeze.** Include the original dashboard, improved dashboard, exact questions, answer key, model answers, and scoring. State whether the display remained visible while answering. That would clarify the experiment more than another summary table.

Also define:

- **Scoring:** exact match, partial credit, set overlap, aggregation across questions, and treatment of abstentions.
- **The ± values:** standard deviation, standard error, or confidence interval—and across what units.
- **Forecast targets:** what counts as “working,” how the 1.5–2-hour window is scored, and what “who speaks next” means.
- **Persistence:** the actual prediction rule for each forecast question, including ties and previously inactive agents.
- **Exposure:** inspection time, query/token limits, number of model runs, and what “current state removed” means.
- **Error validation:** examples of genuine failures and benign stderr output, plus a manually checked estimate of the text classifier’s accuracy.

## 4. What I would most want added or changed

1. **Fix the contradictions before expanding the argument.** Correct the perfect-score headline, held-out improvement, and reversed forecast-error sentence.

2. **Reframe the construct claim.** You have promising evidence about AI analysts extracting information from displays. You do not yet have evidence that human operators gain situation awareness.

3. **Develop questions from an oversight task analysis.** Identify the decisions an operator must make, what information supports those decisions, and what constitutes a consequential misunderstanding. Do not assign SAGAT levels solely because a question concerns the present, an aggregate, or the future.

4. **Add a human study with representative work.** Have participants monitor evolving swarm activity and make interventions under realistic workload. Use task-appropriate, unpredictable freezes and hidden displays for SAGAT probes. If using SPAM, report response accuracy, response latency, and probe availability, while recognizing that display access and interruption produce a different measurement problem.

5. **Report paired effects and uncertainty.** Show per-moment changes, sample sizes after exclusions, and intervals for differences. Separate pilot-set discovery from held-out confirmation. Explain temporal dependence and why the selected mid-workday moments represent the intended oversight setting.

6. **Measure operational outcomes and costs.** Include missed hazards, intervention quality, response time, workload, and availability. Perfectly reading recent activity is not enough if the operator misses a developing coordination failure.

7. **Separate answer-key reliability from validity.** Validate the underlying labels, particularly errors and inferred work state. Automatic agreement between implementations cannot do that job.

## 5. Overall verdict

The core engineering argument is convincing: frozen records can support a cheap, repeatable benchmark that exposes missing dashboard information, and the held-out improvement is useful evidence. The claim that this faithfully applies SAGAT or demonstrates operator situation awareness is not convincing yet; it needs corrected reporting, validated questions, a clear display-removal protocol, and human operational testing.