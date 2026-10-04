### 1. Statements that are wrong, unsupported, overstated, or inconsistent

1. **"A plain dashboard takes an analyst from guessing to perfect on every level."** *(Under "In short")*  
   **The problem:** This is flatly contradicted by the document’s own tables. In the first table, the plain dashboard scores 0.71 (cheap) and 0.73 (strong) on "What it means," and 0.55 and 0.57 on "What happens next." Even the "improved" dashboard in the second table only reaches 0.90 and 0.65. It was only "perfect" (1.00) on the first level ("What's going on"), and even then, only for the cheap model. Calling it "perfect on every level" is a blatant falsehood.

2. **"On the yes/no forecasts, the wrong answers were overwhelmingly 'yes, that will happen' when it didn't: 16–17 such errors against 1–3 the other way."** *(Under Finding 4)*  
   **The problem:** The text directly contradicts the table immediately above it. The table lists `wrongly said 'no'` as 16 to 17, and `wrongly said 'yes'` as only 1 to 3. If the analysts wrongly said "no," they predicted something would *not* happen when it actually did. The text says the exact opposite ("overwhelmingly 'yes'").

3. **"That question rose from 0.58 to 0.84..."** *(Under Finding 2)* vs. **"...scores on that question rose from 0.29 to 0.84."** *(Under "In short")**  
   **The problem:** In the summary, the score for "who has agent X been talking to?" reportedly jumps from 0.29 to 0.84. In Finding 2, the text states the original score was 0.29, but then claims two sentences later that it "rose from 0.58 to 0.84." The document gives two completely different baseline numbers (0.29 vs. 0.58) for the exact same result.

4. **"With the dashboard, the analyst was perfect on 'what's going on'."** *(Under Finding 1)*  
   **The problem:** In the first table, the stronger analyst scored `0.99 ± 0.02` on "What's going on." 0.99 is not perfect (1.00). 

5. **"When thousands of agents coordinate (as in the incidents that motivated this hackathon), the people responsible need situation awareness."** *(Under "The problem")*  
   **The problem:** This overstates the study's scope. Under "What we built," the actual swarms tested ranged from only "6 to 32 agents." Stating that this addresses coordination problems of "thousands of agents" is unsupported; tracking 10 or 20 agents is fundamentally different from tracking thousands.

6. **"An independently rebuilt answer key: 515 of 515 recomputed answers matched."** *(Under Safeguards)* vs. **"The obvious 'error rate' metric is heavily contaminated... about 40% were normal output."** *(Under Finding 6)*  
   **The problem:** Presenting a 100% match on recomputed answers as proof that the scoring was reliable is misleading. As admitted in Finding 6, the underlying data flag was 40% noise, meaning the "correct" answers on error questions were frequently wrong in reality. Recomputing the same flawed formula identically only proves the code ran consistently, not that the answer key was accurate.

---

### 2. What confused me or felt counter-intuitive

* **AI testing AI:** The introduction talks about helping *people* oversee swarms. It was very confusing to discover later that no humans actually looked at the dashboards. Instead, computer programs (AI models) were "looking" at screens designed for humans. If a dashboard is meant for human eyes, testing an AI on it doesn't prove it will work for a person.
* **The "nothing changes" rule:** The text says this rule assumes the next couple of hours look like the last half hour, yet claims it is "perfect on the first two levels by construction." How can a forecasting rule be scored on the past and present? Calling a simple database lookup of past facts the "nothing changes rule" makes no sense.
* **Cheaper models beating expensive ones:** It felt completely counter-intuitive that the "cheap" model tied or beat the model that cost up to 180 times more (e.g., getting 1.00 vs 0.99 on current state, and 0.38 vs 0.31 on guessing). The write-up does not explain why paying 180× more produced equal or worse results.
* **The dates:** The document is dated October 2026 and talks about data from September 2026. Without context explaining that this is a simulated future or a fictional hackathon scenario, it reads like an error.

---

### 3. Where an example, image, or clearer explanation is most needed

* **An image or mockup of the dashboard:** What does a "plain dashboard" actually look like? Is it a visual web page with graphs, or just a block of raw text fed into a computer? 
* **The nature of the "swarm":** An intelligent outsider has no idea what these "agents" are actually doing. Are they writing software, trading stocks, or chatting? Brief concrete examples (e.g., "Agent A was downloading a file while Agent B wrote code") are needed to ground the test.
* **The scoring numbers:** Numbers like `0.71 ± 0.10` are thrown around without explanation. Does 0.71 mean 71% of questions were answered correctly? What does the `± 0.10` mean to an ordinary reader?

---

### 4. What a reader like me would most want added or changed

* **Clarify who is being tested right away:** State plainly in the introduction that AI models were used as stand-ins for human analysts, rather than burying that detail.
* **Provide one concrete question-and-answer walkthrough:** Walk through a single moment: show what was happening, what the dashboard displayed, what question was asked, how the AI answered, and what the correct answer was. 
* **Reconcile the data errors:** Fix the glaring contradictions between the text and the tables regarding the yes/no forecasting errors and the 0.29 vs. 0.58 baseline score.

---

### 5. Overall verdict

The core idea—borrowing a freeze-frame simulation test from aviation to measure whether a monitoring screen actually informs the viewer—is intuitive and clever. However, the argument is unconvincing because it tests other AI programs rather than actual human overseers, and the write-up is undermined by basic mathematical and textual contradictions in its primary findings. Until the data errors are corrected and tested on real people, the dashboard cannot be declared a success.