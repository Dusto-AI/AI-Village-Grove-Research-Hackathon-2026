## 1. Statements most likely wrong, unsupported, or overstated

1. **“A plain dashboard takes an analyst from guessing to perfect on every level.”**

   Directly contradicted by both tables. On the first 26 moments, the cheap dashboard analyst scores **1.00, 0.71, and 0.55** across the three levels; the strong analyst scores **0.99, 0.73, and 0.57**. Even the best improved configuration is not perfect on comprehension or forecasting. Replace this with “The dashboard substantially improved answers about current activity.”

2. **“We added that, retested on 26 *fresh* moments, and scores on that question rose from 0.29 to 0.84.”**

   This mixes results from different test sets. Finding 2 says the original-to-improved comparison on the fresh moments was **0.58 to 0.84**, not 0.29 to 0.84. The original dashboard already performed better on those fresh moments, so the headline exaggerates the improvement attributable to the fix. Also, you added both an interaction panel and history: the experiment does not isolate which addition caused the improvement.

3. **“On the yes/no forecasts, the wrong answers were overwhelmingly "yes, that will happen" when it didn't: 16–17 such errors against 1–3 the other way.”**

   The table says exactly the opposite: **16–17 wrongly said “no”**, versus **1–3 wrongly said “yes.”** This also contradicts the heading “analysts bet on activity stopping.” Correct the prose before drawing any conclusions about forecast bias.

4. **“A dashboard is enough for the present, and digging through raw data isn't better, just pricier.”**

   Your own table shows raw-record access doing better on comprehension: **0.85 versus 0.71** for the cheap dashboard analyst. Comprehension concerns the present, too. The paragraph acknowledges this immediately after making the opposite claim. A defensible conclusion is that raw access was worse for basic state extraction, better for the original dashboard’s missing relationship information, and more expensive.

5. **“The AI Village logs everything its agents do, so:”**

   Finding 5 later says agents remember recent conversation **“that the records don't keep.”** That undermines the claim of complete logging. More importantly, a log-derived answer key establishes truth about recorded events and your operational definitions—not necessarily the swarm’s actual condition. State what the export captures, what it omits, and which questions remain valid despite those omissions.

6. **“No view, model or panel beat "nothing changes" at forecasting.”**

   Numerically, one did: **0.67 versus 0.65**. You can say you found **no statistically convincing improvement**, but the write-up does not show the analysis needed to establish that. The “±” values are undefined, the baseline has no uncertainty shown, and marginal uncertainty intervals do not replace a paired comparison at the same moments. “A tie” also overstates the evidence: failing to detect a difference is not establishing equivalence.

## 2. What confused me or felt counter-intuitive

- **Is this SAGAT, or a dashboard question-answering benchmark?** Your explanation of SAGAT requires blanking the display before questioning. You never clearly say whether the AI analysts lose dashboard and tool access while answering. The human explorer’s optional “classic mode” makes this distinction especially important. Reading answers off a visible dashboard tests information accessibility, not necessarily retained situation awareness.

- **“Nothing changes” is doing two different jobs.** It is an oracle for perception and comprehension, but a persistence heuristic for forecasting. Perfect present-state answers are not produced by assuming nothing changes; they come from computing the answer key. Present these as two separate references.

- **“What it means” mostly looks like more counting.** Most frequent conversation partner, inactivity, and error counts can all be extracted mechanically. Why are these comprehension rather than perception? None obviously tests whether an analyst understands a dependency failure, coordination bottleneck, or operational consequence.

- **The snapshot definition is unclear.** You remove material describing the live system’s “current” state, yet ask questions about current activity and provide a status dashboard. Presumably you mean state at export time rather than at the historical freeze. Say that explicitly.

- **Blocked runs are excluded from accuracy, but matter operationally.** Separating refusal from wrong answers is sensible for diagnosis. However, an overseer that refuses to answer has still failed to provide oversight. I want both conditional accuracy and an all-request success rate.

## 3. Where an example, image, definition, or clearer explanation is most needed

**The biggest missing artifact is one complete worked freeze.** Show:

- The timestamp and relevant input records.
- The original and improved dashboard, side by side.
- One question at each level.
- The analyst’s answers and the computed reference answers.
- Exactly how each answer receives its score.
- The persistence forecast for the same questions.

That would make the experiment much easier to understand than another aggregate table.

Also define:

- **Scoring:** What does 0.84 mean for “who has X been talking to”? Exact match, set overlap, partial credit, or something else? How are ties and ambiguous task descriptions handled?
- **Uncertainty:** What do the “±” values represent? What is the sampling unit, and how do you handle moments from the same swarm being correlated?
- **Forecast targets:** How is “who speaks next” predicted by persistence? What happens if nobody speaks within the observed window?
- **Metric validity:** Include actual examples of stderr output classified as failure versus harmless output, and explain how the estimated 40% contamination was checked.

## 4. What I would most want added or changed

**Give me a next-week implementation guide, not just a reproduction guide for your dataset.** I need:

1. **Minimum telemetry schema:** agent identity, event time, action type, conversation recipients, human/agent attribution, outcome, and any required task metadata. Explain what remains testable when fields are missing.
2. **A custom-data adapter example:** a small sample input and the commands or functions that turn my logs into snapshots, questions, answer keys, and reports.
3. **The actual analyst configuration:** model identifiers, prompts, tool permissions, context limits, sampling settings, retry policy, and whether the dashboard stays available during answers.
4. **A leakage checklist:** timestamp checks alone do not catch a pre-freeze record later edited to contain post-freeze information. Explain how retrospective summaries, memory updates, and export-time state are handled.
5. **A clean evaluation protocol:** select questions before tuning; compare original and improved dashboards on the same held-out moments; report paired differences and uncertainty. Test panel additions separately if you want to attribute improvements.
6. **Real deployment requirements and cost:** distinguish the $8.07 model bill from data preparation, engineering time, hosting, and human testing. Clarify the research-only licence and whether the tooling itself can be used commercially with my own data.

I would also change the framing. This currently supports **“we can detect missing information in a dashboard using narrow, log-scored questions answered by LLMs.”** It does not yet support **“this dashboard helps people understand a swarm.”** Add a small human evaluation before making that leap, and test questions that correspond to actual intervention decisions—not just activity counts.

## 5. Overall verdict

The core idea is convincing as a practical dashboard-testing loop: define operational questions, replay historical moments, identify missing information, and retest. The evidence is not convincing as proof of improved human situation awareness or forecasting, and the headline exaggeration, mixed test-set comparison, and reversed error explanation need fixing before I would trust the reported results. I could pilot the approach next week, but not from this write-up alone without the scoring specification, input schema, and custom-data integration instructions.