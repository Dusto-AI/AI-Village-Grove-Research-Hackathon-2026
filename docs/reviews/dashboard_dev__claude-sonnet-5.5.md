## 1. Statements most likely wrong, unsupported, or inconsistent

1. **"A plain dashboard takes an analyst from guessing to perfect on every level. It beat guessing at every one of the 26 moments tested."**
   - The first table contradicts this. The dashboard scores 0.71–0.73 on "what it means" and 0.55–0.57 on "what happens next". Only "what's going on" is near perfect.
   - On forecasting, the cheap dashboard (0.55) is barely above cheap guessing (0.44) and below the "nothing changes" rule (0.59). The strong dashboard (0.57) is actually *better* than strong guessing (0.37) but still below the rule.
   - "Beat guessing at every one of the 26 moments" is not backed by anything shown. The tables give only means ± error, and no per-moment results appear.

2. **"scores on that question rose from 0.29 to 0.84"** (summary) vs. **"the dashboard analyst scored 0.29 ... That question rose from 0.58 to 0.84"** (finding 2)
   - The baseline changes within a single paragraph: 0.29 versus 0.58. Presumably 0.29 is from the first 26 moments and 0.58 is the original dashboard on the fresh 26.
   - The headline then compares a first-set baseline to a fresh-set result, which flatters the improvement. The honest same-moments comparison is 0.58→0.84.
   - Neither per-question figure appears in any table.

3. **"the wrong answers were overwhelmingly 'yes, that will happen' when it didn't: 16–17 such errors against 1–3 the other way."**
   - This is backwards relative to the table. The 16–17 count is in the column "wrongly said 'no'". Wrongly saying "yes" is 1–3.
   - The summary ("betting that activity will stop") matches the table, so finding 4 contradicts both. The core mechanism is garbled in the section that explains it.

4. **"A dashboard is enough for the present, and digging through raw data isn't better, just pricier."**
   - The same paragraph says raw access scored 0.85 vs 0.71 on "what it means", which is a large gain. That is not "isn't better".
   - "Largely because of the blind spot below" is asserted, not shown. No per-question breakdown for the raw-SQL run is given.
   - The raw-SQL view was only run with the cheap model on the first 26 moments.
   - "Slightly worse" (0.88 vs 1.00) is within the quoted ±0.12, so it's noise, not a finding.

5. **"The test found a specific blind spot in the dashboard, and fixing it worked."** Combined with **"We added a panel for that, plus 'typical patterns' history"**
   - Two changes were bundled, so you can't attribute the gain to the interaction panel. The write-up itself then credits "typical patterns" for the forecasting-bias shift.
   - The blind spot (no interaction data on a dashboard) is obvious from the design, and the question was written to need that data. Finding it is not much evidence that SAGAT is a discovery tool.
   - The "fresh" moments come from the same swarm and the same year, and the first 26 were seen before the redesign. That is a weak held-out test.
   - "Better at 7 moments, worse at 1" implies 18 ties. The effect on the aggregate score is modest (0.80→0.88).

6. **"The obvious 'error rate' metric is about 40% noise in this dataset"** (headline) vs. **"a rough text check suggests about 40% were normal output"** (body)
   - The headline presents a "rough" check on a 60,000-action sample as a solid figure.
   - "40% of flagged actions are benign" is not the same as "the metric is 40% noise".
   - The write-up also says "515 of 515 recomputed answers matched" as validation. That only shows reproducibility, not validity. The "whose actions produce errors" key is built on this contaminated flag, so the 0.04 score for that question may reflect a bad answer key rather than analyst failure.

Honorable mention: **"Both blocked moments fell in that week... exactly the activity an overseer would most want to see."** This is n=2, and it generalises about provider filters from one incident.

## 2. What confused me or felt counter-intuitive

- **The "nothing changes" rule scores 1.00 "by construction" on two levels.** I couldn't tell whether this is a real baseline or just the answer key restated. If the "who has X talked to most" answer is computed from the last 30 min, then "nothing changes" is the key itself. It is a ceiling, not a competitor, and the comparison table makes it look like one.
- **This isn't really SAGAT.** Classic SAGAT blanks the display before questions. Here the analyst has the dashboard in front of it while answering, so it measures lookup ability, not retained awareness. The "classic mode" exists only for the untested human version.
- **The forecasting "tie" is ambiguous.** Because the rule is so strong, "no better than the rule" could mean the questions are nearly deterministic from recent activity, not that the tools are weak.
- **The error-bar arithmetic is unclear.** Is it SE across moments, a bootstrap, or something else? The write-up never says.
- **"Projection" gets a 0.65 score for a rule that just copies the past.** What are the base rates for the yes/no questions? A majority-class baseline would help.

## 3. Where an example or clearer explanation is most needed

- **A real example of the dashboard.** What panels did it have? What did the analyst literally see for one moment? I can't judge "plain" or reproduce it without that.
- **One worked question end to end.** For example: the question text, the dashboard snapshot, the analyst answer, the truth, and the score. Include how "Who'll be working 1.5–2h later" is scored (set overlap? F1?).
- **The scoring rules per question type**, since 0–1 scores mix set overlap, binary, and ranking.
- **The error bars and how many answers underlie each cell.** The 515 figure suggests only a handful of questions per moment.
- **A per-question table.** Finding 2, finding 5 and finding 6 all rely on per-question numbers (0.29, 0.58, 0.84, 0.04, 0.23) that are not shown.
- **The "typical patterns" panel**, which is described only in one phrase but credited with the bias shift.

## 4. What I'd want added or changed

- **Fix the contradictions** in findings 1, 2 and 4, and the mislabelled summary claim.
- **Separate the two dashboard changes** (interaction panel vs. typical patterns) with an ablation. Otherwise "fixing the gap worked" isn't causal.
- **Report base rates** for the yes/no forecasts, and the majority-class baseline.
- **Show per-moment paired differences** with intervals, since you say you use moment-by-moment comparisons but report only marginal means ± error.
- **Give a minimal recipe I can port:** the question templates, the freeze/sealing logic, the scoring code. Explain what to do for my own dashboard when I don't have a complete event log with future "truth". A live dashboard has no sealed record to score against, so say what substitutes.
- **Address scale.** The motivation is "thousands of agents", but the test swarm has 6–32. Does the dashboard approach, or the "nothing changes" result, survive at scale?
- **Fix the error-flag question.** Either re-key "whose actions produce errors" with a cleaned flag, or drop it from the aggregate and say so.
- **Cost transparency.** A cost-per-view table would back the "4×" and "70–180×" claims, and show how $8.07 splits across them.
- **Tone down the claims** about plans ("no evidence they add anything" is fine) and about the safety filter.

## 5. Verdict

The idea is good: frozen-time SAGAT on logged swarm data, with a "nothing changes" baseline and a test-fix-retest loop. The forecasting-tie result is plausible and useful. But the write-up has internal contradictions (the "perfect on every level" claim, the 0.29/0.58 baseline, the reversed yes/no error direction), and several headline numbers rest on bundled changes, a weak held-out set, or a contaminated answer key. I'd borrow the method and the baseline, but I couldn't apply it next week without the dashboard spec, scoring rules, and per-question results, and I wouldn't cite the specific numbers until they're reconciled.