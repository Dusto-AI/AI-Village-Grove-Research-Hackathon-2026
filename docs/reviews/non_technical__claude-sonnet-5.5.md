## 1. Statements most likely wrong, unsupported, overstated or inconsistent

**a. "A plain dashboard takes an analyst from guessing to perfect on every level. It beat guessing at every one of the 26 moments tested."**
- The first table contradicts this. The dashboard scores about 0.71–0.73 on "what it means" and 0.55–0.57 on "what happens next". Only the first level is near perfect.
- The forecasting gap over guessing is small (0.55 vs 0.44, with ±0.09 error bars). Beating guessing at *every* moment is very unlikely, and no moment-by-moment data is shown to back it up.

**b. "scores on that question rose from 0.29 to 0.84" (summary) vs. "That question rose from 0.58 to 0.84" (finding 2)**
- The same improvement is given two different starting points. 0.29 is the dashboard's score on the first 26 moments, and 0.58 seems to be the original dashboard on the fresh 26.
- The headline therefore mixes two different sets of moments. That undercuts the "retested on fresh moments" claim, because the real before/after on the fresh set is 0.58 → 0.84.

**c. "the wrong answers were overwhelmingly 'yes, that will happen' when it didn't: 16–17 such errors against 1–3 the other way."**
- This is backwards compared with the table. The 16–17 errors are in the column "wrongly said 'no'", meaning the analyst predicted nothing would happen and something did.
- The summary says analysts bet that "activity will stop", which matches the table but not this sentence. The text and the table disagree about the central finding on forecasting.

**d. "digging through raw data isn't better, just pricier."**
- The same paragraph says raw records did better on "what it means" (0.85 vs 0.71). It also scored lower on the first level (0.88 vs 1.00), but that difference sits inside the error bars (±0.12).
- "Largely because of the blind spot below" is asserted, not shown. "About 4× as much" has no cost figures anywhere in the document.
- Raw records were tested only with the cheap model.

**e. "The obvious 'error rate' metric is about 40% noise in this dataset"**
- The body says only that "a rough text check" on a sample "suggests about 40%" of flagged actions were normal output. A rough estimate became a flat statistic.
- Being 40% of *flagged* actions is not the same as the metric being 40% noise.
- The document also uses this flawed flag as the answer key for "whose actions produce errors". The 0.04 score on that question may therefore say more about the key than about the analysts.

**f. "Showing analysts 'typical patterns' nearly halved that bias"**
- The improved dashboard changed two things at once: the interaction panel and the typical patterns. The effect can't be pinned on patterns alone.
- "Wrongly said no" fell from 17 to 9, but "wrongly said yes" rose from 3 to 7. The total errors only fell from 20 to 16. "Halved" is selective.

(Also overstated: "A safety filter blinded the overseer, twice... exactly the activity an overseer would most want to see." Two blocked runs is too thin to support that.)

## 2. What confused me or felt counter-intuitive

- The "nothing changes" rule scores a perfect 1.00 on two levels "by construction". If it is the answer key in disguise, it is not a meaningful opponent. I couldn't tell why that makes it a "ceiling" rather than an artifact.
- "Perfect on the first two levels" sits oddly next to the claim that the error question is badly flawed.
- 52 moments × 11 questions is 572, but "515 of 515 answers" were checked. Why 515?
- What are the "±" numbers? Standard error, a range, something else? "Well within the margin of error" depends on it.
- The first-26 and fresh-26 tables use different baselines (0.59 vs 0.65 for the rule), so cross-table comparison is confusing.
- "Memory file" and "agents' plans" are never explained. Is a memory file what the agent knows, and is it separate from plans?
- Wouldn't a good dashboard make the "no change" rule *more* useful, not less?

## 3. Where examples or explanations are most needed

- One worked example of a frozen moment: the dashboard as shown, a question, the true answer, and a cheap and strong analyst's answer.
- What the "interaction panel" and "typical patterns" actually look like.
- What "cheap" and "strong" mean in plain terms, and what "SQL" is.
- An explanation of how "sticky" activity makes "no change" hard to beat, with a concrete case.
- A plain definition of the two yes/no forecast questions and why "no" is the wrong bet.

## 4. What I'd want added or changed

- Fix the contradictions above (the 0.29 vs 0.58 figure, the direction of the forecasting errors, and "perfect on every level").
- Report costs per view so "4×" and "$8.07" can be checked.
- Test the interaction panel and typical patterns separately.
- Say clearly that the error question is unreliable, and either drop it or rescore without it.
- Explain the link between 6–32 agents and the motivating "thousands of agents".
- Back up or remove "live SAGAT studies rarely manage this".
- Tone down the language on findings that rest on two blocked runs, one agent's memory or a rough text check.
- A short plain-English summary of what the analysts' scores mean in practice.

## 5. Verdict

The idea (test whether oversight tools actually improve understanding, and compare against a "nothing changes" baseline) is sensible and the test-fix-retest loop is persuasive. But several headline claims are contradicted by the document's own tables (perfect on every level, the direction of forecasting errors, the mismatched 0.29/0.58). Because of that, I would trust the general message but not the specific numbers until they are cleaned up.