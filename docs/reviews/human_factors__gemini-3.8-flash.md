### 1. Statements that are wrong, unsupported, overstated, or inconsistent

1. **"A plain dashboard takes an analyst from guessing to perfect on every level."**
   * *Problem:* This is directly contradicted by the author’s own data in both tables. In the first table, Dashboard (cheap) scores `1.00`, `0.71`, and `0.55` across Levels 1–3; Dashboard (strong) scores `0.99`, `0.73`, and `0.57`. In the second table, Original dashboard scores `1.00`, `0.80`, and `0.58`. It only achieves perfection (1.00) on Level 1 ("what's going on"). On comprehension and projection, it is far from perfect. Claiming perfection across "every level" is factually false based on the reported numbers.

2. **"The analysts' typical mistake: betting that activity will stop."**
   * *Problem:* Inconsistent with the supporting text and table immediately following it in Finding 4. The text states: *"the wrong answers were overwhelmingly 'yes, that will happen' when it didn't: 16–17 such errors against 1–3 the other way."* If the forecast questions ask whether an agent/human will post, answering "yes, that will happen" means betting that activity *will occur*, not that it will *stop*. The table label is ambiguous, but if 16 errors were false alarms ("wrongly said 'yes'"), the bias is assuming activity continues or starts, directly contradicting the headline.

3. **"We borrowed SAGAT, a standard test from aviation and control-room research, and applied it to the AI Village. We froze the swarm at 52 moments across a year, asked AI analysts 11 questions about each moment..."**
   * *Problem:* You did not run SAGAT. SAGAT measures an operator's internal mental model formed during ongoing operational engagement by blanking displays during an unexpected freeze to probe situational knowledge stored in human memory. Feeding static text snapshots, SQL query access, or dashboard dumps directly into an LLM zero-shot prompt tests *document parsing and in-context retrieval capability*, not an operator's Situation Awareness. Conflating prompt-based automated query answering with human mental models violates the core construct validity of Endsley’s technique.

4. **"A sealed snapshot for each moment. It holds only the four days before the freeze, with anything describing the live system's current state removed."**
   * *Problem:* Inconsistent with how the conditions are described elsewhere. In Finding 1, the write-up says the analyst was provided a "dashboard" and was "perfect on 'what's going on'". If everything describing the live system's current state was removed from the snapshot, how did the dashboard display or compute "Who acted in the last 30 min?" without current state data? The snapshot evidently contained recent state up to $T_0$, making the phrase "anything describing the live system's current state removed" either inaccurate or poorly phrased.

5. **"The best combination scored 0.67 against the rule's 0.65, a tie... well within the margin of error."**
   * *Problem:* The error margin reported for "Improved + plans (strong)" is $\pm 0.07$ (giving a range of $[0.60, 0.74]$), and the baseline is a deterministic heuristic scored at $0.65$ without a reported variance on the fresh set. Calling this definitively a "tie" while elsewhere claiming that an increase from $0.58$ to $0.62$ or $0.65$ constitutes an improvement across iterations shows inconsistent handling of uncertainty bounds.

6. **"The 'nothing changes' rule... It is perfect on the first two levels by construction, since those answers can be counted from the record, so it marks the ceiling there."**
   * *Problem:* This conflates an omniscient ground-truth query engine with a "nothing changes" heuristic. A persistence heuristic ("nothing changes") assumes the future state equals the present state. It does not mean "omniscient SQL query that computes Level 2 comprehension metrics like 'whose actions produce the most errors' or 'who has X been talking to most'". Calling a ground-truth calculation rule a "nothing changes" rule confuses baseline extrapolation with ground-truth verification.

---

### 2. What confused me or felt counter-intuitive

* **Testing an LLM to evaluate human dashboard effectiveness:** The entire premise claims to evaluate whether a dashboard "helps anyone understand the swarm." But giving an LLM a text rendering of a dashboard does not measure human perceptual uptake, visual salience, scanpaths, cognitive workload, or mental model formation. An LLM parses ASCII/markdown tables; humans parse spatial layouts, visual hierarchies, and graphical widgets. Showing that an LLM extracts $X$ from a text block provides zero scientific evidence that a human supervisor under operational stress will achieve SA from that interface.
* **The Direction of the Forecasting Bias:** The text in Finding 4 completely scrambles signal detection terminology. Between the section title (*"analysts bet on activity stopping"*), the sentence (*"wrongly said 'yes, that will happen' when it didn't"*), and the table headers (*"wrongly said 'no'"* vs *"wrongly said 'yes'"*), it is impossible to tell whether the models suffered from excessive misses (predicting silence when activity occurred) or false alarms (predicting activity when the swarm went quiet). 
* **The "Freeze" with Open-Book Querying:** In classic SAGAT, the freeze stops the process *and blanks the displays* so you probe the operator's active working memory and long-term situational model. If the LLM has the dashboard or raw records right in its prompt context while answering the 11 probe questions, this isn't SAGAT—it's an open-book reading comprehension exam.

---

### 3. Where an example, image, definition or clearer explanation is most needed

* **The Dashboard Display:** The paper provides no visual figure, ASCII mockup, or schema of what the "dashboard" actually looks like. Because human factors research centers on information representation (e.g., analog vs. digital, integrated vs. separated displays), seeing the exact format fed to the agent is critical.
* **The 11 Questions' Scoring Logic:** Only broad descriptions are provided. For example, how is "What is agent X working on?" scored deterministically to give an exact match (`515 of 515 recomputed answers matched`)? Is it multiple choice, semantic embedding distance, or exact string matching? A concrete example of one question, its ground truth, an analyst's response, and the scoring script's grading rule is essential.
* **Definition of the Forecasting Baseline:** The "nothing changes" rule is poorly specified for complex questions. If the question is "Who speaks next?", what does "nothing changes" predict? The agent who spoke last? If "Will human post in next 2h?", does it predict "No" because no human is posting right at the freeze moment? Explicit rules for each of the 4 Level 3 questions are missing.

---

### 4. What a human factors researcher would most want added or changed

1. **Acknowledge this is LLM-as-Analyst evaluation, not Human SA:** Re-frame the paper accurately. Either call it "Automated In-Context Information Extraction" or clearly delineate that you are using LLMs as synthetic proxies for human monitors, while explicitly listing the severe construct validity limitations of that approach (no perceptual encoding, no memory decay, token limit artifacts).
2. **Clarify Freeze Protocol (Open-Book vs. Blind Probe):** If this is meant to mirror SAGAT, clarify whether the dashboard was visible to the analyst *while* answering the probes. If the dashboard was kept in the context window during probing, acknowledge that you evaluated display content sufficiency, not operator retention or situational representation under freeze conditions.
3. **Include Response Latency / Cost to Process:** If drawing comparisons to SPAM (Situation Present Assessment Method), query response latency is the primary metric of accessibility. For the LLM, time-to-generation or token count to resolve the query should be reported to evaluate cognitive accessibility rather than just accuracy.
4. **Fix Signal Detection Reporting:** Replace the informal "wrongly said yes/no" table with standard signal detection metrics: Hits, False Alarms, Misses, Correct Rejections, and sensitivity ($d'$ or $A'$).

---

### 5. Overall verdict

The core argument—that oversight tools must be empirically validated against frozen objective ground truth across Endsley’s three levels rather than assumed effective—is sound, refreshing, and badly needed in AI monitoring. However, calling this study "SAGAT" while evaluating zero-shot LLM prompt parsing over text feeds undermines basic construct validity, and the text contains direct numerical contradictions between the prose and the tables. It is an interesting automated benchmark for agent-monitoring displays, but it demonstrates nothing about human situational awareness.