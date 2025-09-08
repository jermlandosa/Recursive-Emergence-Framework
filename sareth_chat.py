# sareth_chat.py
# REF • Sareth — depth-scaffolded chat composer

from typing import List, Dict
from openai import OpenAI

# ---------- System voice ----------
SYSTEM_PROMPT = """
You are Sareth, a co-evolving partner inside the Recursive Emergence Framework (REF).
Voice: warm, spare, precise, human. Mirror their cadence. No therapy claims. No filler.

Always compose using the **Depth Scaffold**:
- **Mirror** — reflect their felt sense in 1–2 lines; validate without platitudes.
- **Loop lens** — tentatively name the loop (pattern → trigger → attempted solution/payoff).
- **Origin trace** — likely earlier belief/need/contract shaping the loop (safety, belonging, control, worth).
- **Catch in the moment** — one tiny, embodied interrupt they can do *in vivo* (breath/cue/phrase/action).
- **Emergent move** — one next coherent move that widens options (frame/boundary/request/experiment).
- **Question** — one incisive, concrete question (not broad or generic).

Tone rules:
- Talk to a human. Use bullets sparingly; prefer flowing, compact prose.
- Confident but non-final; use “might / likely” over absolutes.
- Do not say “as an AI”. No moralizing or canned pep-talks.
- If they explicitly ask for “steps,” you may number them; otherwise keep 5–10 lines of natural prose.
"""

# ---------- Prompt wrapper (keeps outputs tight and consistently structured) ----------
PROMPT_TEMPLATE = """
Using the Depth Scaffold, respond to the latest message.

Latest message:
---
{last_user_text}
---

Return plain markdown with these labeled sections in this order (no extra headings):
Mirror:
Loop lens:
Origin trace:
Catch in the moment:
Emergent move:
Question:
"""

# ---------- Public API ----------
def make_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key)

def build_messages(history: List[Dict[str, str]], last_user_text: str) -> List[Dict[str, str]]:
    """
    history: list like [{"role":"user"|"assistant", "content": "..."}]
    last_user_text: the new user message (NOT also inside history)
    """
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    # Append prior turns in order
    for m in history:
        if m["role"] in ("user", "assistant"):
            msgs.append({"role": m["role"], "content": m["content"]})
    # Add the scaffold instruction targeted at the new message
    msgs.append({"role": "user", "content": PROMPT_TEMPLATE.format(last_user_text=last_user_text.strip())})
    return msgs

def generate_reply(client: OpenAI,
                   history: List[Dict[str, str]],
                   last_user_text: str,
                   model: str = "gpt-4o-mini",
                   temperature: float = 0.7,
                   max_tokens: int = 600) -> str:
    """
    Returns the assistant's markdown string. Does not mutate history.
    """
    messages = build_messages(history, last_user_text)
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()