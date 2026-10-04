# SAGAT results — freeze set `v1` (26 freezes)

Mean score (0-1) per SA level, freezes as the unit, ± ~95% CI. L1 perception, L2 comprehension, L3 projection.

Runs that returned no answers (harness failure or a provider content filter) are excluded from the means and counted in `no-answer`; `n` is the number of freezes actually scored. Questions skipped inside a submitted run score 0.

| analyst · condition | n | no-answer | L1 | L2 | L3 | all | mean $/freeze |
|---|---|---|---|---|---|---|---|
| heuristic (persistence) | 26 | – | 1.00 ± 0.00 | 1.00 ± 0.00 | 0.59 ± 0.07 | 0.85 ± 0.03 | – |
| openrouter:anthropic/claude-sonnet-5.5 · dashboard | 25 | 1 | 0.99 ± 0.02 | 0.73 ± 0.07 | 0.57 ± 0.09 | 0.77 ± 0.04 | 0.020 |
| openrouter:anthropic/claude-sonnet-5.5 · none | 25 | 1 | 0.31 ± 0.07 | 0.39 ± 0.09 | 0.37 ± 0.07 | 0.35 ± 0.05 | 0.010 |
| openrouter:anthropic/claude-sonnet-5.5 · self | 25 | 1 | 0.58 ± 0.07 | 0.45 ± 0.09 | 0.42 ± 0.09 | 0.48 ± 0.05 | 0.043 |
| openrouter:deepseek/deepseek-v4-flash · dashboard | 26 | 0 | 1.00 ± 0.00 | 0.71 ± 0.10 | 0.55 ± 0.09 | 0.75 ± 0.05 | 0.019 |
| openrouter:deepseek/deepseek-v4-flash · none | 26 | 0 | 0.38 ± 0.08 | 0.33 ± 0.11 | 0.44 ± 0.08 | 0.38 ± 0.05 | 0.004 |
| openrouter:deepseek/deepseek-v4-flash · raw | 26 | 0 | 0.88 ± 0.12 | 0.85 ± 0.11 | 0.49 ± 0.08 | 0.73 ± 0.09 | 0.073 |
| openrouter:deepseek/deepseek-v4-flash · self | 26 | 0 | 0.45 ± 0.08 | 0.35 ± 0.10 | 0.39 ± 0.09 | 0.40 ± 0.06 | 0.025 |

## Per query

| analyst · condition | active_now (L1) | chattiest (L1) | focal_task (L1) | human_recent (L1) | focal_partner (L2) | gone_quiet (L2) | most_struggling (L2) | active_later (L3) | focal_chat_next (L3) | human_next (L3) | next_speaker (L3) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| heuristic (persistence) | 1.00 (n=26) | 1.00 (n=26) | 1.00 (n=25) | 1.00 (n=26) | 1.00 (n=24) | 1.00 (n=26) | 1.00 (n=25) | 0.79 (n=26) | 0.81 (n=26) | 0.69 (n=26) | 0.08 (n=26) |
| openrouter:anthropic/claude-sonnet-5.5 · dashboard | 1.00 (n=25) | 0.96 (n=25) | 1.00 (n=24) | 1.00 (n=25) | 0.26 (n=23) | 0.96 (n=25) | 0.92 (n=24) | 0.77 (n=25) | 0.80 (n=25) | 0.52 (n=25) | 0.20 (n=25) |
| openrouter:anthropic/claude-sonnet-5.5 · none | 0.67 (n=25) | 0.12 (n=25) | 0.29 (n=24) | 0.16 (n=25) | 0.13 (n=23) | 0.88 (n=25) | 0.08 (n=24) | 0.51 (n=25) | 0.60 (n=25) | 0.28 (n=25) | 0.08 (n=25) |
| openrouter:anthropic/claude-sonnet-5.5 · self | 0.82 (n=25) | 0.40 (n=25) | 0.88 (n=24) | 0.24 (n=25) | 0.35 (n=23) | 0.88 (n=25) | 0.04 (n=24) | 0.61 (n=25) | 0.68 (n=25) | 0.24 (n=25) | 0.16 (n=25) |
| openrouter:deepseek/deepseek-v4-flash · dashboard | 1.00 (n=26) | 1.00 (n=26) | 1.00 (n=25) | 1.00 (n=26) | 0.29 (n=24) | 0.85 (n=26) | 0.96 (n=25) | 0.77 (n=26) | 0.65 (n=26) | 0.58 (n=26) | 0.19 (n=26) |
| openrouter:deepseek/deepseek-v4-flash · none | 0.70 (n=26) | 0.12 (n=26) | 0.16 (n=25) | 0.54 (n=26) | 0.12 (n=24) | 0.54 (n=26) | 0.24 (n=25) | 0.50 (n=26) | 0.77 (n=26) | 0.42 (n=26) | 0.08 (n=26) |
| openrouter:deepseek/deepseek-v4-flash · raw | 0.88 (n=26) | 0.85 (n=26) | 0.92 (n=25) | 0.92 (n=26) | 0.71 (n=24) | 0.96 (n=26) | 0.84 (n=25) | 0.75 (n=26) | 0.46 (n=26) | 0.62 (n=26) | 0.12 (n=26) |
| openrouter:deepseek/deepseek-v4-flash · self | 0.48 (n=26) | 0.31 (n=26) | 0.80 (n=25) | 0.23 (n=26) | 0.33 (n=24) | 0.62 (n=26) | 0.04 (n=25) | 0.49 (n=26) | 0.62 (n=26) | 0.27 (n=26) | 0.19 (n=26) |

## Paired comparisons (same freezes)

Difference A - B in mean score per freeze, ± ~95% CI; `wins` = freezes where A beat B / B beat A. A CI that excludes 0 is a difference we would report.

| A | B | L1 | L2 | L3 | all |
|---|---|---|---|---|---|
| openrouter:anthropic/claude-sonnet-5.5 · dashboard | heuristic (persistence) | -0.01 ± 0.02 (0/1) | -0.27 ± 0.07 (0/19) | -0.02 ± 0.09 (6/11) | -0.09 ± 0.04 (2/19) |
| openrouter:anthropic/claude-sonnet-5.5 · dashboard | openrouter:anthropic/claude-sonnet-5.5 · none | +0.68 ± 0.06 (25/0) | +0.33 ± 0.08 (20/0) | +0.20 ± 0.10 (20/3) | +0.42 ± 0.06 (25/0) |
| openrouter:anthropic/claude-sonnet-5.5 · self | heuristic (persistence) | -0.42 ± 0.07 (0/24) | -0.55 ± 0.09 (0/24) | -0.17 ± 0.12 (6/17) | -0.37 ± 0.06 (0/25) |
| openrouter:anthropic/claude-sonnet-5.5 · self | openrouter:anthropic/claude-sonnet-5.5 · none | +0.27 ± 0.06 (25/0) | +0.05 ± 0.06 (5/1) | +0.05 ± 0.09 (17/7) | +0.13 ± 0.05 (21/4) |
| openrouter:deepseek/deepseek-v4-flash · dashboard | heuristic (persistence) | +0.00 ± 0.00 (0/0) | -0.29 ± 0.10 (0/18) | -0.04 ± 0.08 (5/10) | -0.09 ± 0.05 (3/19) |
| openrouter:deepseek/deepseek-v4-flash · dashboard | openrouter:deepseek/deepseek-v4-flash · none | +0.62 ± 0.08 (26/0) | +0.38 ± 0.15 (19/2) | +0.11 ± 0.11 (17/7) | +0.37 ± 0.06 (26/0) |
| openrouter:deepseek/deepseek-v4-flash · raw | heuristic (persistence) | -0.12 ± 0.12 (0/4) | -0.15 ± 0.11 (0/7) | -0.11 ± 0.10 (3/12) | -0.12 ± 0.09 (2/13) |
| openrouter:deepseek/deepseek-v4-flash · raw | openrouter:deepseek/deepseek-v4-flash · none | +0.51 ± 0.15 (23/3) | +0.52 ± 0.14 (22/1) | +0.04 ± 0.13 (13/10) | +0.34 ± 0.11 (22/4) |
| openrouter:deepseek/deepseek-v4-flash · self | heuristic (persistence) | -0.55 ± 0.08 (0/25) | -0.65 ± 0.10 (0/25) | -0.20 ± 0.12 (5/18) | -0.45 ± 0.07 (0/25) |
| openrouter:deepseek/deepseek-v4-flash · self | openrouter:deepseek/deepseek-v4-flash · none | +0.07 ± 0.12 (14/12) | +0.03 ± 0.14 (8/6) | -0.05 ± 0.10 (9/15) | +0.01 ± 0.09 (12/14) |
| openrouter:deepseek/deepseek-v4-flash · raw | openrouter:deepseek/deepseek-v4-flash · dashboard | -0.12 ± 0.12 (0/4) | +0.14 ± 0.14 (12/4) | -0.06 ± 0.13 (5/9) | -0.03 ± 0.10 (13/8) |
