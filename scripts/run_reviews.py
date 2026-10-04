"""Re-run the reviewer test: 5 reader personas x 3 model families review
docs/reviews/WRITEUP_WITH_PLANTED_ERRORS.md (an earlier draft with three
planted errors; key in docs/reviews/PLANTED_KEY.txt). Reviews are written
next to it. Needs an OpenRouter key (see sagat/openrouter.py); ~$0.55.

  uv run python scripts/run_reviews.py docs/reviews     # run from the repo root
"""
import json, sys, concurrent.futures as cf
sys.path.insert(0, ".")
from sagat import openrouter as O
R = sys.argv[1]
doc = open(f"{R}/WRITEUP_WITH_PLANTED_ERRORS.md").read()
PERSONAS = {
 "statistician": "a data analyst / applied statistician who reviews empirical claims for a living. You care about sample sizes, baselines, multiple comparisons, whether conclusions follow from the numbers, and internal consistency of reported figures.",
 "human_factors": "a human factors researcher who has run SAGAT and SPAM studies with pilots and control-room operators. You care about whether the method is applied faithfully, construct validity, and what transfers to human operators.",
 "ai_safety": "an AI safety researcher working on oversight of multi-agent AI systems. You care about whether this helps catch dangerous swarm behaviour, threat models, and what the results do and don't license.",
 "dashboard_dev": "a software developer who builds monitoring dashboards and LLM tooling. You want to know whether you could apply this to your own dashboard next week, and what you'd need.",
 "non_technical": "a curious, intelligent reader with no technical, statistical or AI background. You read carefully but don't know jargon.",
}
MODELS = ["anthropic/claude-sonnet-5.5", "openai/gpt-6.1-sol", "google/gemini-3.8-flash"]
ASK = """You are reviewing a short hackathon write-up as {persona}

Review it critically and specifically. Please report:
1. Up to 6 statements that are most likely WRONG, unsupported, overstated, or inconsistent with other parts of the document. Quote each statement exactly, then explain the problem. Real errors matter most here; point to the evidence inside the document.
2. What confused you or felt counter-intuitive, and why.
3. Where an example, image, definition or clearer explanation is most needed.
4. What a reader like you would most want added or changed.
5. Overall verdict in 2-3 sentences: is the core argument convincing to someone like you?

Be direct; you are not here to be polite. Use plain headings 1-5.

--- WRITE-UP START ---
{doc}
--- WRITE-UP END ---"""
key = O.api_key()
def one(persona, model):
    body = {"model": model, "messages": [{"role": "user", "content": ASK.format(persona=PERSONAS[persona], doc=doc)}],
            "max_tokens": 6000, "usage": {"include": True}}
    r = O._post(body, key)
    text = r["choices"][0]["message"].get("content") or ""
    cost = (r.get("usage") or {}).get("cost") or 0
    name = f"{persona}__{model.split('/')[1]}"
    open(f"{R}/{name}.md", "w").write(text)
    return name, cost, len(text)
jobs = [(p, m) for p in PERSONAS for m in MODELS]
total = 0
with cf.ThreadPoolExecutor(8) as ex:
    for fut in cf.as_completed([ex.submit(one, p, m) for p, m in jobs]):
        try:
            name, cost, n = fut.result(); total += cost
            print(f"{name:40s} {n:6d} chars ${cost:.4f}", flush=True)
        except Exception as e:
            print("FAIL", e, flush=True)
print(f"total ${total:.3f}")
