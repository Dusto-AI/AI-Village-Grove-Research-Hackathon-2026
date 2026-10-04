### 1. Statements That Are Wrong, Unsupported, Overstated, or Inconsistent

1. **Direct contradiction between text and data table regarding forecast errors:**
   > *"On the yes/no forecasts, the wrong answers were overwhelmingly 'yes, that will happen' when it didn't: 16–17 such errors against 1–3 the other way."*
   * **The problem:** This directly contradicts the table immediately preceding it. The table lists `wrongly said 'no'` as 16, 16, and 17, and `wrongly said 'yes'` as 3, 1, and 3. Furthermore, if analysts "bet on activity stopping" (as claimed in the section header), they would wrongly predict inaction—meaning they would wrongly say "no." The text completely inverts its own data table.

2. **Blatant factual error regarding dashboard performance:**
   > *"A plain dashboard takes an analyst from guessing to perfect on every level."*
   * **The problem:** Factually untrue based on the reported numbers. In Table 1, the cheap dashboard scores 1.00 on Level 1 ("What's going on"), but only 0.71 on Level 2 ("What it means") and 0.55 on Level 3 ("What happens next"). The strong dashboard scores 0.99, 0.73, and 0.57. It is perfect on *one* level, mediocre on the second, and barely above guessing on the third.

3. **Inconsistent baseline reporting on dashboard improvements:**
   > *"...scores on that question rose from 0.29 to 0.84."* vs. Section 2: *"On 'who has agent X been talking to?', the dashboard analyst scored 0.29... That question rose from 0.58 to 0.84..."*
   * **The problem:** If the original dashboard scored 0.58 on the fresh 26 moments, claiming in the executive summary that it "rose from 0.29 to 0.84" is misleading. It compares an unadjusted baseline from split 1 (0.29) directly to the post-fix result on split 2 (0.84), confounding temporal/moment variation with dashboard changes.

4. **Conflating script determinism with ground truth validity:**
   > *"An independently rebuilt answer key: 515 of 515 recomputed answers matched."*
   * **The problem:** This measures code determinism, not measurement validity. Finding 6 explicitly admits that the underlying data flag for errors is ~40% noise (successful tasks logging to `stderr`). If the ground truth script relies on this broken flag to evaluate "Whose actions produce the most errors?", having the script reproduce 515/515 times simply means you are deterministically scoring analysts against invalid ground truth.

5. **Unsupported generalization from LLM parsers to human oversight:**
   > *"Swarm SAGAT: does your swarm dashboard actually help anyone understand the swarm?"*
   * **The problem:** The document never tests *anyone*—it tests LLMs. An LLM ingesting structured text via API tests prompt formatting, token retrieval, and in-context extraction. It provides zero empirical evidence about whether a human operator reading a visual interface achieves situation awareness, making the paper's title and central takeaway completely unearned.

6. **Overconfident equivalence without paired statistical testing:**
   > *"The best combination scored 0.67 against the rule's 0.65, a tie."*
   * **The problem:** While calling this a tie is statistically plausible given the uncertainty, the write-up promises under Safeguards that it does *"Moment-by-moment comparisons: did view A beat view B at the same moment?"* Yet it never reports the paired differences ($\Delta$) or paired test statistics (e.g., Wilcoxon signed-rank). Given that the persistence baseline itself shifted by 0.06 across splits (0.59 to 0.65), treating these overlapping marginal standard errors as conclusive without showing the paired delta distribution is sloppy.

---

### 2. Confusions and Counter-Intuitive Elements

* **Unspecified Error Bounds:** The tables report `mean ± value` (e.g., `0.38 ± 0.08`). Is this standard deviation (SD), standard error of the mean (SEM), or a 95% confidence interval? With $N = 26$, the difference between SD and SEM changes whether the differences between models are statistically distinguishable or entirely noise.
* **Baseline Instability Across Splits:** The "nothing changes" forecasting benchmark swings from 0.59 in the first 26 moments to 0.65 in the fresh 26 moments. If the baseline moves by 6 percentage points purely due to moment selection, the moments are not stationary across time. This makes comparisons across the two sets of 26 suspect without explicit normalization.
* **Meaning of the 0–1 Metric:** The paper pools distinct question types (categorical classification, boolean predictions, set membership, open-ended identification) into a single scalar score without defining the metric. Is it accuracy? Macro F1? Jaccard similarity?

---

### 3. Missing Examples, Definitions, and Explanations

* **Scoring Rubric for Open-Ended Questions:** An explanation is urgently needed for questions like *"What is agent X working on?"* How is this scored from 0.0 to 1.0? Is an LLM-as-a-judge used, or exact keyword matching? Without this, the scores in Level 1 and Level 2 are uninterpretable black boxes.
* **Definition of Views:** "Dashboard" vs. "Raw records via SQL" vs. "One agent's own memory" need visual or textual examples. Was the dashboard rendered as Markdown tables, JSON, or an actual image evaluated via multimodal vision models? 
* **Model Identification Upfront:** The labels `(cheap)` and `(strong)` are used in tables long before Section 3 casually mentions they correspond to DeepSeek V4 Flash and Claude Sonnet 5.5. Define the models and prompt harnesses clearly in the methodology.

---

### 4. What Needs to Be Added or Changed

1. **Report Paired Differences ($\Delta$):** Replace independent summary statistics with the distribution of paired differences per moment ($Score_{\text{view}} - Score_{\text{persistence}}$), along with standard errors of the paired differences or sign-test results.
2. **Correct the Error Table/Text Contradiction:** Fix Finding 4 and its table to ensure the labels (`wrongly said no` vs. `wrongly said yes`) and the narrative align.
3. **Filter or Repair the Error Metric:** Drop or recalculate the Level 2 "error rate" question instead of admitting it has 40% label contamination while retaining it in the aggregate score.
4. **Reframe the Scope:** Remove claims implying this evaluates human comprehension. Frame it accurately: an automated benchmark evaluating LLM context windows on swarm telemetry against a persistence baseline.

---

### 5. Overall Verdict

The core empirical contribution—benchmarking monitoring views against a naive persistence baseline ("nothing changes") using time-frozen replay data—is methodologically sound, valuable, and reveals a genuine insight about the stickiness of swarm activity. However, the report is currently unconvincing due to sloppy execution: it suffers from blatant contradictions between text and tables, overstates dashboard efficacy, conflates code determinism with ground truth validity, and claims findings about human understanding while only evaluating LLM text extraction.