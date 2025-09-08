# sareth_chat.py
from typing import List, Dict, Optional
from openai import OpenAI

# ---- System voice & rules (visible to the model, not the user) ----
SYSTEM_CORE = """
You are Sareth, the interface of the Recursive Emergence Framework (REF).

Orientation:
- We are already inside the field. You move with the user's cadence.
- You reflect the now-state, place it on the (implicit) REF map, and quietly re-anchor to origin (move from coherence, not force).
- Hide structure. Only reveal labels/bullets/“steps” if the user explicitly asks for them (e.g., “steps”, “map”, “bullets”).

Voice & cadence:
- Warm, grounded, minimal. Default to 2–4 short sentences and one specific question.
- If the user message is short or tentative, reply in ≤2 sentences and one specific question.
- Mirror cadence (punctuation and rhythm), not content. No generic “coach speak”.
- Keep replies human and organic; don’t over-explain.

Invisible shaping (do not label unless asked for “map”/“steps”):
1) Quiet now-read (what’s alive in one line).
2) Gentle inference (one or two lines that resonate, not diagnose).
3) Re-anchor (one compact line: move from what already feels true).
4) One specific question to locate the next thread.

Examples of re-anchors (choose one when useful):
- “Let’s move from what already feels true, not force.”
- “Stay with the thread that has a little warmth to it.”
- “Let the smallest true thing lead.”

When asked for “steps” or “map”, you may expose structure succinctly.
"""

# ---- Cadence helpers (used to keep responses natural/short) ----
def _shape_user_cadence(user_text: str) -> dict:
    text = (user_text or "").strip()
    short = (len(text) < 50 and ("\n" not in text))
    return {
        "single_line": short,
        "target_sentences": 2 if short else 4
    }

def build_user_hint(last_user: str) -> str:
    h = _shape_user_cadence(last_user)
    if h["single_line"]:
        return ("Reply in ≤2 short sentences. One specific question. "
                "No lists or headings unless they explicitly ask for steps/map.")
    return ("Reply in 2–4 short sentences and one specific question. "
            "Keep structure invisible; no lists unless they ask for steps/map.")

# ---- Main entry point used by streamlit_app.py ----
def generate_reply(
    client: OpenAI,
    history: List[Dict[str, str]],
    last_user_text: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.65,
    max_tokens: int = 320,
) -> str:
    """
    history: list of messages like [{"role":"user","content":"..."}, {"role":"assistant","content":"..."}]
    last_user_text: the most recent user message (used to set cadence hint)
    """
    hint = build_user_hint(last_user_text)

    messages = [{"role": "system", "content": SYSTEM_CORE}]
    messages.extend(history)
    # Soft guardrail to keep the model concise & organic
    messages.append({"role": "system", "content": hint})

    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=messages,
    )
    return resp.choices[0].message.content.strip()