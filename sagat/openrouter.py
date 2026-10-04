"""OpenRouter backend: the same analyst loop over OpenRouter's OpenAI-style
chat-completions API, so cheap or non-Claude models can be SAGAT-tested too.
Select it with a model name like `openrouter:deepseek/deepseek-v4-flash`.

Key: $OPENROUTER_API_KEY, else the macOS Keychain service named by
$OPENROUTER_KEYCHAIN_SERVICE (default `openrouter`).
Stdlib only (urllib), so it adds no dependency.
"""
import json
import os
import subprocess
import time
import urllib.error
import urllib.request

from .config import WORK

URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS_URL = "https://openrouter.ai/api/v1/models"


def api_key():
    k = os.environ.get("OPENROUTER_API_KEY")
    if not k:
        service = os.environ.get("OPENROUTER_KEYCHAIN_SERVICE", "openrouter")
        r = subprocess.run(["security", "find-generic-password", "-s", service, "-w"],
                           capture_output=True, text=True)
        k = r.stdout.strip() if r.returncode == 0 else ""
    if not k:
        raise SystemExit("No OpenRouter key: set $OPENROUTER_API_KEY, or point "
                         "$OPENROUTER_KEYCHAIN_SERVICE at the Keychain service holding it.")
    return k


def prices(model):
    """$ per token (prompt, completion) from OpenRouter's public model list,
    cached in work/. Used only when a response omits its own cost."""
    path = WORK / "openrouter_models.json"
    if not path.exists() or time.time() - path.stat().st_mtime > 86400:
        with urllib.request.urlopen(MODELS_URL, timeout=60) as r:
            path.write_bytes(r.read())
    for m in json.loads(path.read_text())["data"]:
        if m["id"] == model:
            p = m["pricing"]
            return float(p["prompt"]), float(p["completion"])
    return 0.0, 0.0


def _post(body, key, retries=4):
    data = json.dumps(body).encode()
    for attempt in range(retries + 1):
        req = urllib.request.Request(URL, data=data, headers={
            "Authorization": f"Bearer {key}", "Content-Type": "application/json",
            "X-Title": "swarm-sagat"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:500]
            if e.code in (408, 429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(2 ** attempt * 3)
                continue
            raise RuntimeError(f"OpenRouter HTTP {e.code}: {msg}") from None
        except (urllib.error.URLError, TimeoutError):
            if attempt < retries:
                time.sleep(2 ** attempt * 3)
                continue
            raise


def _fn(tool):
    """Anthropic-style tool dict -> OpenAI function tool. No `strict`: not all
    OpenRouter providers accept it, and off-schema answers already score 0."""
    return {"type": "function", "function": {"name": tool["name"],
                                             "description": tool["description"],
                                             "parameters": tool["input_schema"]}}


def _coerce(answers, item):
    """Light normalisation for models without strict schemas."""
    out = {}
    for q in item["queries"]:
        v = answers.get(q["id"])
        if q["kind"] == "bool" and isinstance(v, str):
            v = {"true": True, "yes": True, "false": False, "no": False}.get(v.strip().lower(), v)
        if q["kind"] == "set" and isinstance(v, str):
            v = [x.strip() for x in v.split(",") if x.strip()]
        if q["kind"] == "mc" and isinstance(v, str):
            v = v.strip()[:1].upper()
        out[q["id"]] = v
    return out


def run_one(model, cond, item, system, user_text, tools, run_sql, max_turns=24):
    key = api_key()
    or_model = model.split(":", 1)[1]
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user_text}]
    fns = [_fn(t) for t in tools]
    usage = {"input": 0, "output": 0, "cache_write": 0, "cache_read": 0}
    reported_cost, answers, sql_log, stop, nudged, served_by = 0.0, None, [], None, 0, None
    turn = 0
    for turn in range(max_turns):
        # last round: require the answer tool, so a long investigation still
        # ends in a scored submission rather than an empty run
        last = turn == max_turns - 1
        choice_param = ({"type": "function", "function": {"name": "submit_answers"}}
                        if last else "auto")
        resp = _post({"model": or_model, "messages": messages, "tools": fns,
                      "tool_choice": choice_param, "max_tokens": 32000,
                      "usage": {"include": True}}, key)
        if "error" in resp:
            raise RuntimeError(f"OpenRouter error: {resp['error']}")
        u = resp.get("usage") or {}
        usage["input"] += u.get("prompt_tokens", 0)
        usage["output"] += u.get("completion_tokens", 0)
        usage["cache_read"] += (u.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0
        reported_cost += u.get("cost") or 0.0
        served_by = resp.get("model", or_model)
        choice = resp["choices"][0]
        msg, stop = choice["message"], choice.get("finish_reason")
        calls = msg.get("tool_calls") or []
        messages.append({"role": "assistant", "content": msg.get("content") or "",
                         **({"tool_calls": calls} if calls else {})})
        if not calls:
            if nudged >= 2:
                break
            nudged += 1
            hint = (" Your last reply was cut off for length: think briefly this time."
                    if stop == "length" else "")
            messages.append({"role": "user", "content": "Please call submit_answers now "
                             "with all answers." + hint})
            continue
        for c in calls:
            name = c["function"]["name"]
            try:
                args = json.loads(c["function"].get("arguments") or "{}")
            except json.JSONDecodeError:
                messages.append({"role": "tool", "tool_call_id": c["id"],
                                 "content": "Error: arguments were not valid JSON."})
                continue
            if name == "submit_answers":
                answers = _coerce(args, item)
                content = "Answers recorded."
            elif name == "sql":
                content, _ = run_sql(item["frozen_db"], str(args.get("query", "")))
                sql_log.append(args.get("query", ""))
            else:
                content = f"Error: unknown tool {name}."
            messages.append({"role": "tool", "tool_call_id": c["id"], "content": content})
        if answers is not None:
            break
        if turn >= max_turns - 3:
            messages.append({"role": "user", "content": "Tool budget nearly used up: call "
                             "submit_answers in your next response."})
    if not reported_cost:
        p_in, p_out = prices(or_model)
        reported_cost = usage["input"] * p_in + usage["output"] * p_out
    return {"model": model, "served_by": served_by, "condition": cond, "effort": None,
            "freeze": item["id"], "answers": answers, "stop_reason": stop,
            "n_requests": turn + 1, "sql_queries": sql_log, "usage": usage,
            "cost_usd": round(reported_cost, 5)}
