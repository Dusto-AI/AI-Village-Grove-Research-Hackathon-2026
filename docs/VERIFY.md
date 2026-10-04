# A 20-minute spot-check

You don't need to read any code. Each check takes a few minutes and tests a
different link in the chain: data → answer key → analyst answers → scores
→ write-up. If any check fails, please tell us. That is the point of it.

**Open the explorer.** Use `work/explorer.html`, built locally with
`uv run python -m sagat explorer` and dataset access, which is needed for
checks 1–2. Otherwise `docs/explorer_public.html` covers checks 3–5.

### 1. Is a "what's going on" answer right? (5 min, full explorer)
Moments tab → set **Fresh 26 moments** → **2025-12-25 10:10 PT**, the
write-up's worked example.
- Under *What the analyst was shown*, pick **Dashboard**. In the agents
  table, every agent with "actions 30m" above 0 should appear in the true
  answer to *Who acted in last 30 min* (10 agents here).
- Find the agent with the most "chat msgs 60m". It should match the true
  answer to *Chattiest in last hour*.

### 2. Is a "what it means" answer right? (5 min, full explorer)
Same moment. Pick the **+ who-talks-to-whom** view and find GPT-5's line in
the *Who is talking to whom* panel.
- Its top names should match the true answer to *Who X talks to most*
  (GPT-5.2 or Gemini 2.5 Pro, tied).
- For a stricter check, read the *Recent chat* lines on the plain
  **Dashboard** view and count by hand how often GPT-5 names, or is named
  by, each agent.

### 3. Do the analysts' answers and scores match? (3 min, either explorer)
Questions tab → pick *What happens next: Will X post in 30 min*.
- Pick any 3 rows. Check that the ✓/✗ for each view follows from comparing
  its answer to the true answer.
- Count the ✗ entries where the view said "false" but the truth was "true".
  The original-dashboard column should have far more of these than ✗
  entries the other way (finding 4).

### 4. Does a headline number match the data? (5 min, either explorer)
Method & data tab → **Download every answer (CSV)** → open it in a
spreadsheet.
- Filter to set `v2`, model `openrouter:deepseek/deepseek-v4-flash`,
  condition `dashboard`, question `focal_partner`.
- The average of the `score` column should be **0.58**. Repeat with
  condition `dashboard2`: it should be **0.84** (finding 2).

### 5. Did the reviewers really catch the planted errors? (2 min, repo)
Open `docs/reviews/PLANTED_KEY.txt`, then any two reviews in
`docs/reviews/`. Look in their section 1 for the three planted sentences.

### Optional: check a forecasting answer against the raw future (dataset access)
The explorer shows only records from before each freeze, by design. To
check a "what happens next" truth, query the source data directly. For
example, did a human post in the 2 hours after the worked example's
freeze? (The write-up's answer: no.)

```bash
sqlite3 "$VILLAGE_DB" "SELECT count(*) FROM chat_messages
  WHERE speaker_type != 'agent'
  AND created_at > '2025-12-25 18:10:18' AND created_at <= '2025-12-25 20:10:18';"
# expect 0  (times are UTC; the freeze was 10:10:18 PT = 18:10:18 UTC)
```
