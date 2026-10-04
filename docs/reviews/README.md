# Reviewer test: 15 AI reviews of the write-up, with planted errors

**What this is.** Before revising the write-up, we sent an earlier draft
(`WRITEUP_WITH_PLANTED_ERRORS.md`, with figures replaced by the same numbers as text
tables) to 15 AI reviewers: five reader types, each played by three model
families. The reader types were statistician, human-factors researcher,
AI-safety researcher, dashboard developer and non-technical reader; the
models were Claude Sonnet 5.5, GPT-6.1 Sol and Gemini 3.8 Flash, via
OpenRouter. The prompt and settings are in `scripts/run_reviews.py`. Total cost
was $0.55.

**The test.** The draft contained three deliberately planted errors.
Reviewers were not told about them. The key is in `PLANTED_KEY.txt`:
1. a wrong number in the summary;
2. an overstated claim ("perfect on every level");
3. a reversed finding.

**Result: 44 of 45 caught.** The one miss was Gemini as the human-factors
reader, on the wrong number. Detection was judged by reading each review,
not by keyword search alone.

| Reader | Claude Sonnet 5.5 | GPT-6.1 Sol | Gemini 3.8 Flash |
|---|---|---|---|
| Statistician | 3/3 | 3/3 | 3/3 |
| Human factors | 3/3 | 3/3 | 2/3 |
| AI safety | 3/3 | 3/3 | 3/3 |
| Dashboard developer | 3/3 | 3/3 | 3/3 |
| Non-technical | 3/3 | 3/3 | 3/3 |

**What it means.** All three planted errors contradicted another part of
the same document, so a careful reader *can* catch them. Errors that are
consistent throughout the document, or that live in the data rather than
the text, are invisible to this kind of review. The real flaw we found in
the data (the error flag; see NOTES.md Entry 14) is an example. The
reviewers also raised genuine issues, which the final write-up addresses;
see NOTES.md Entry 17.

The file names give the reader type and the model.
