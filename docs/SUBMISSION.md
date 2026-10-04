# Swarm SAGAT: testing whether swarm dashboards actually help

**The problem.** As agent swarms grow, the people overseeing them depend on
dashboards, summaries and AI analysts to tell them what's going on. Those
tools keep getting more polished, but that polish is easy to mistake for
understanding. A clean, confident screen can still leave its reader unable
to answer the questions that matter, or worse, become confidently wrong.
Right now we mostly judge oversight tools by how informative they *look*
(or how useful they seem after a few minutes of use).

**The idea.** Aviation solved this decades ago with **SAGAT** (Situational
Awareness Global Assessment Technique). Freeze a flight simulator at a
random moment, ask the pilot what's going on, what it means and what
happens next, and score the answers against the truth. If a new cockpit
display really helps, scores go up. A recorded swarm is an almost perfect
fit for this. Any past moment can be "frozen" by hiding what came after it,
the right answers are already in the logs, and even "what happens next" can
be scored, because the future has already happened.

**What I did.** I froze the AI Village at 52 moments across a year (6 to 32
agents). At each moment I asked AI analysts 11 questions, giving them
different views: nothing, a status dashboard, the raw records, or a single
agent's own memory. Their answers were scored against what really
happened, and compared with a no-intelligence baseline: "assume nothing
changes".

**Why it matters beyond this dataset.** The method doesn't care what the
observer is: an AI analyst, a human with a dashboard, or a reviewer
checking a report. Anyone building swarm-oversight tools can use it to find
out whether a tool genuinely improves understanding, rather than assuming
it does. The same recursion applies to checking the work itself. This
project was built with an AI coding agent in about a day. So I also
SAGAT-tested the reviewers: 15 AI reviews of the write-up, with three
planted errors. They caught 44 of 45, but every planted error contradicted
something else in the text. Errors that are consistent throughout, or that
live in the data rather than the text, would slip past that kind of review.
One real data flaw here was found only by reading raw records. Finding
these weird gaps is really what this hackathon is all about.

**Try it.** The repo plugs in any dashboard with one function and scores it
on the same moments (a plain chat feed did clearly worse than the status
board). An explorer page shows every frozen moment, what each analyst saw
and how it answered. A "Try it yourself" tab lets a person take the same
test. Everything rebuilds from the public dataset.

**What I found.**
- **A plain dashboard gets an analyst from guessing to perfect on "what's
  going on"** at every moment tested.
- **The test pinpointed what the dashboard was missing.** It didn't show
  who was working with whom. Adding that, and retesting on fresh moments,
  raised that score from 0.58 to 0.84. That loop is the main point of this
  system: test, find the gap, fix it, retest.
- **Nothing reliably beats "assume nothing changes" at predicting what
  happens next:** not a much stronger model, raw data, history panels, or
  the agents' own written plans. The analysts' typical mistake was betting
  that activity would stop, when in this swarm it usually carries on.
- **Catching an agent that misreports its work depends on the view.** I
  took agents' real "just finished" messages and quietly deleted the
  activity behind some of them. The improved dashboard caught 8 of 9 of
  these planted misreports; a chat feed alone caught none. Getting this
  test right took three attempts: my first two inserted fake messages, and
  the analysts partly spotted the fake text rather than the contradiction.
- **Some obvious signals are misleading.** The dataset's "error" flag also
  marks many successful actions. One agent's memory knew little about the
  wider swarm. And during a security-training exercise, the AI provider's
  safety filter blocked the stronger analyst from answering at all.

*Data: AI Village transcripts (AI Digest / AI Village dataset). Full
write-up, notebook and code in the repo.*
