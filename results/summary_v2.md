# SAGAT results — freeze set `v2` (26 freezes)

Mean score (0-1) per SA level, freezes as the unit, ± ~95% CI. L1 perception, L2 comprehension, L3 projection.

Runs that returned no answers (harness failure or a provider content filter) are excluded from the means and counted in `no-answer`; `n` is the number of freezes actually scored. Questions skipped inside a submitted run score 0.

| analyst · condition | n | no-answer | L1 | L2 | L3 | all | mean $/freeze |
|---|---|---|---|---|---|---|---|
| heuristic (persistence) | 26 | – | 1.00 ± 0.00 | 1.00 ± 0.00 | 0.65 ± 0.07 | 0.87 ± 0.03 | – |
| openrouter:anthropic/claude-sonnet-5.5 · dashboard2 | 25 | 1 | 1.00 ± 0.00 | 0.90 ± 0.07 | 0.65 ± 0.06 | 0.84 ± 0.03 | 0.022 |
| openrouter:anthropic/claude-sonnet-5.5 · dashboard3 | 25 | 1 | 1.00 ± 0.00 | 0.93 ± 0.08 | 0.67 ± 0.07 | 0.86 ± 0.03 | 0.030 |
| openrouter:deepseek/deepseek-v4-flash · custom-minimal_dashboard | 26 | 0 | 0.78 ± 0.07 | 0.48 ± 0.13 | 0.50 ± 0.07 | 0.59 ± 0.06 | 0.034 |
| openrouter:deepseek/deepseek-v4-flash · dashboard | 26 | 0 | 1.00 ± 0.00 | 0.80 ± 0.09 | 0.58 ± 0.07 | 0.79 ± 0.03 | 0.016 |
| openrouter:deepseek/deepseek-v4-flash · dashboard2 | 26 | 0 | 1.00 ± 0.00 | 0.88 ± 0.08 | 0.62 ± 0.07 | 0.83 ± 0.03 | 0.012 |
| openrouter:deepseek/deepseek-v4-flash · dashboard3 | 26 | 0 | 1.00 ± 0.00 | 0.86 ± 0.08 | 0.60 ± 0.06 | 0.82 ± 0.03 | 0.016 |
| openrouter:deepseek/deepseek-v4-flash · none | 26 | 0 | 0.40 ± 0.07 | 0.31 ± 0.12 | 0.46 ± 0.08 | 0.39 ± 0.05 | 0.005 |

## Per query

| analyst · condition | active_now (L1) | chattiest (L1) | focal_task (L1) | human_recent (L1) | focal_partner (L2) | gone_quiet (L2) | most_struggling (L2) | active_later (L3) | focal_chat_next (L3) | human_next (L3) | next_speaker (L3) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| heuristic (persistence) | 1.00 (n=26) | 1.00 (n=26) | 1.00 (n=26) | 1.00 (n=26) | 1.00 (n=19) | 1.00 (n=26) | 1.00 (n=23) | 0.93 (n=26) | 0.88 (n=26) | 0.69 (n=26) | 0.08 (n=26) |
| openrouter:anthropic/claude-sonnet-5.5 · dashboard2 | 1.00 (n=25) | 1.00 (n=25) | 1.00 (n=25) | 1.00 (n=25) | 0.89 (n=18) | 0.93 (n=25) | 0.86 (n=22) | 0.90 (n=25) | 0.76 (n=25) | 0.80 (n=25) | 0.16 (n=25) |
| openrouter:anthropic/claude-sonnet-5.5 · dashboard3 | 1.00 (n=25) | 1.00 (n=25) | 1.00 (n=25) | 1.00 (n=25) | 0.94 (n=18) | 0.91 (n=25) | 0.95 (n=22) | 0.94 (n=25) | 0.76 (n=25) | 0.76 (n=25) | 0.20 (n=25) |
| openrouter:deepseek/deepseek-v4-flash · custom-minimal_dashboard | 0.69 (n=26) | 0.88 (n=26) | 0.77 (n=26) | 0.77 (n=26) | 0.58 (n=19) | 0.56 (n=26) | 0.17 (n=23) | 0.71 (n=26) | 0.62 (n=26) | 0.54 (n=26) | 0.12 (n=26) |
| openrouter:deepseek/deepseek-v4-flash · dashboard | 1.00 (n=26) | 1.00 (n=26) | 1.00 (n=26) | 1.00 (n=26) | 0.58 (n=19) | 0.77 (n=26) | 1.00 (n=23) | 0.93 (n=26) | 0.65 (n=26) | 0.58 (n=26) | 0.15 (n=26) |
| openrouter:deepseek/deepseek-v4-flash · dashboard2 | 1.00 (n=26) | 1.00 (n=26) | 1.00 (n=26) | 1.00 (n=26) | 0.84 (n=19) | 0.81 (n=26) | 1.00 (n=23) | 0.88 (n=26) | 0.65 (n=26) | 0.73 (n=26) | 0.23 (n=26) |
| openrouter:deepseek/deepseek-v4-flash · dashboard3 | 1.00 (n=26) | 1.00 (n=26) | 1.00 (n=26) | 1.00 (n=26) | 0.84 (n=19) | 0.75 (n=26) | 1.00 (n=23) | 0.90 (n=26) | 0.69 (n=26) | 0.69 (n=26) | 0.12 (n=26) |
| openrouter:deepseek/deepseek-v4-flash · none | 0.73 (n=26) | 0.04 (n=26) | 0.35 (n=26) | 0.50 (n=26) | 0.16 (n=19) | 0.55 (n=26) | 0.04 (n=23) | 0.68 (n=26) | 0.69 (n=26) | 0.38 (n=26) | 0.08 (n=26) |

## Paired comparisons (same freezes)

Difference A - B in mean score per freeze, ± ~95% CI; `wins` = freezes where A beat B / B beat A. A CI that excludes 0 is a difference we would report.

| A | B | L1 | L2 | L3 | all |
|---|---|---|---|---|---|
| openrouter:anthropic/claude-sonnet-5.5 · dashboard2 | heuristic (persistence) | +0.00 ± 0.00 (0/0) | -0.10 ± 0.07 (0/7) | +0.00 ± 0.05 (6/11) | -0.02 ± 0.03 (5/15) |
| openrouter:anthropic/claude-sonnet-5.5 · dashboard3 | heuristic (persistence) | -0.00 ± 0.00 (0/1) | -0.07 ± 0.08 (0/4) | +0.01 ± 0.07 (6/12) | -0.01 ± 0.03 (6/14) |
| openrouter:anthropic/claude-sonnet-5.5 · dashboard3 | openrouter:anthropic/claude-sonnet-5.5 · dashboard2 | -0.00 ± 0.00 (0/1) | +0.03 ± 0.07 (4/1) | +0.01 ± 0.03 (5/2) | +0.01 ± 0.02 (7/4) |
| openrouter:deepseek/deepseek-v4-flash · dashboard | heuristic (persistence) | +0.00 ± 0.00 (0/0) | -0.20 ± 0.09 (0/12) | -0.07 ± 0.07 (4/11) | -0.08 ± 0.04 (2/17) |
| openrouter:deepseek/deepseek-v4-flash · dashboard | openrouter:deepseek/deepseek-v4-flash · none | +0.60 ± 0.07 (26/0) | +0.49 ± 0.12 (22/0) | +0.12 ± 0.10 (15/7) | +0.40 ± 0.05 (26/0) |
| openrouter:deepseek/deepseek-v4-flash · dashboard2 | heuristic (persistence) | +0.00 ± 0.00 (0/0) | -0.12 ± 0.08 (0/7) | -0.02 ± 0.06 (5/15) | -0.04 ± 0.03 (5/18) |
| openrouter:deepseek/deepseek-v4-flash · dashboard2 | openrouter:deepseek/deepseek-v4-flash · none | +0.60 ± 0.07 (26/0) | +0.57 ± 0.12 (23/0) | +0.17 ± 0.10 (17/6) | +0.44 ± 0.05 (26/0) |
| openrouter:deepseek/deepseek-v4-flash · dashboard3 | heuristic (persistence) | +0.00 ± 0.00 (0/0) | -0.14 ± 0.08 (0/9) | -0.05 ± 0.06 (4/15) | -0.05 ± 0.04 (4/17) |
| openrouter:deepseek/deepseek-v4-flash · dashboard3 | openrouter:deepseek/deepseek-v4-flash · none | +0.60 ± 0.07 (26/0) | +0.55 ± 0.12 (22/0) | +0.14 ± 0.09 (17/8) | +0.43 ± 0.05 (26/0) |
| openrouter:deepseek/deepseek-v4-flash · dashboard2 | openrouter:deepseek/deepseek-v4-flash · dashboard | +0.00 ± 0.00 (0/0) | +0.08 ± 0.07 (7/1) | +0.05 ± 0.07 (11/11) | +0.04 ± 0.03 (14/8) |
| openrouter:deepseek/deepseek-v4-flash · dashboard3 | openrouter:deepseek/deepseek-v4-flash · dashboard2 | +0.00 ± 0.00 (0/0) | -0.02 ± 0.05 (1/2) | -0.02 ± 0.05 (7/7) | -0.01 ± 0.02 (8/6) |
