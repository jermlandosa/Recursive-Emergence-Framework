# streamlit_app.py
# REF • Sareth — stable Streamlit shell with duplicate prevention + robust fallbacks

import os
import uuid
import inspect
import streamlit as st

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="REF • Sareth", page_icon="✨", layout="centered")

# -----------------------------
# Secrets / API key
# -----------------------------
OPENAI_API_KEY = (
    st.secrets.get("openai", {}).get("api_key")
    or os.getenv("OPENAI_API_KEY")
    or os.getenv("OPENAI_APIKEY")
    or os.getenv("OPENAI_KEY")
)

if not OPENAI_API_KEY:
    st.error(
        "❌ Missing OpenAI API key.\n\n"
        "Add it in **Settings → Secrets** as:\n"
        "```\n[openai]\napi_key = \"sk-...\"\n```\n"
        "or set the `OPENAI_API_KEY` environment variable."
    )
    st.stop()

# Expose to any module that expects env
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# -----------------------------
# Try to import your orchestrator (sareth_chat.py)
# -----------------------------
_SARETH_OK = True
_IMPORT_ERR = None
_generate_reply = None

try:
    # You may have different versions of this function across branches.
    # We will adapt to either signature at call time.
    from sareth_chat import generate_reply as _generate_reply
except Exception as e:
    _SARETH_OK = False
    _IMPORT_ERR = e

# -----------------------------
# Built-in fallback (depth scaffold) if sareth_chat is missing/broken
# -----------------------------
from openai import OpenAI
_client = OpenAI(api_key=OPENAI_API_KEY)

FALLBACK_SYSTEM = """
You are Sareth, a warm, precise, human-first partner inside the Recursive Emergence Framework (REF).
Keep replies concise and alive (5–10 lines max). No boilerplate, no "as an AI".
Always cover:
- Mirror: reflect their felt sense (1–2 lines).
- Loop lens: name the likely pattern (pattern → trigger → attempted solution/payoff).
- Origin trace: an earlier belief/need that shapes the loop.
- Catch in the moment: one tiny, embodied interrupt they can do in vivo.
- Emergent move: one next coherent move (frame/boundary/request/experiment).
- Question: one incisive, concrete question.

If they ask for steps, you may enumerate briefly. Otherwise keep flowing prose.
""".strip()

def _fallback_generate_reply(user_prompt: str, history: list[dict]) -> str:
    """Depth scaffold via OpenAI if sareth_chat.generate_reply isn't available."""
    messages = [{"role": "system", "content": FALLBACK_SYSTEM}]
    # include trailing context (short tail)
    tail = history[-8:] if history else []
    for m in tail:
        if m["role"] in ("user", "assistant"):
            messages.append({"role": m["role"], "content": m["content"]})
    # newest user input
    messages.append({
        "role": "user",
        "content": (
            "Using the depth scaffold (Mirror, Loop lens, Origin trace, Catch in the moment, "
            "Emergent move, Question), respond naturally to the latest message:\n\n"
            f"{user_prompt.strip()}"
        )
    })
    try:
        resp = _client.chat.completions.create(
            model=st.secrets.get("sareth", {}).get("model", "gpt-4o-mini"),
            messages=messages,
            temperature=0.7,
            max_tokens=600,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        # An extremely safe last resort
        return (
            "It lands like there’s something real underneath this—not just the situation, "
            "but how it hits your system right now.\n\n"
            "I’m sensing a loop of reaching → bracing → reading distance → protecting. "
            "Often that begins with an old contract like “if I show the messy parts, I’ll lose the bond.”\n\n"
            "Catch it in the moment: pause the story, soften your jaw, lengthen the out-breath, and name one true line: "
            "“I want to be close and I’m nervous.”\n\n"
            "From there, a smaller, truer move usually appears. What’s the tiniest honest move you could try today?"
            f"\n\n_(Fallback active: {type(e).__name__}: {e})_"
        )

# Wrapper that calls your `sareth_chat.generate_reply` if available, otherwise uses fallback.
def call_sareth_generate_reply(user_prompt: str, history: list[dict]) -> str:
    if _generate_reply is None:
        return _fallback_generate_reply(user_prompt, history)

    # Detect which signature your `generate_reply` exposes and adapt
    try:
        sig = inspect.signature(_generate_reply)
        params = sig.parameters
        if {"user_prompt", "history"} <= set(params.keys()):
            # Newer/simple signature: generate_reply(user_prompt, history)
            return _generate_reply(user_prompt=user_prompt, history=history)
        elif {"client", "history", "last_user_text"} <= set(params.keys()):
            # Older signature: generate_reply(client=..., history=..., last_user_text=..., ...)
            return _generate_reply(
                client=_client,
                history=history,
                last_user_text=user_prompt,
                model=st.secrets.get("sareth", {}).get("model", "gpt-4o-mini"),
                temperature=0.7,
                max_tokens=600,
            )
        else:
            # Unknown signature — attempt positional with best guess
            try:
                return _generate_reply(user_prompt, history)
            except TypeError:
                return _fallback_generate_reply(user_prompt, history)
    except Exception:
        return _fallback_generate_reply(user_prompt, history)

# -----------------------------
# Session state
# -----------------------------
if "history" not in st.session_state:
    # Each entry: {"id": str, "role": "user"|"assistant", "content": str}
    st.session_state.history = []
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None  # guards accidental double-handling

def add_message(role: str, content: str):
    st.session_state.history.append({
        "id": uuid.uuid4().hex,
        "role": role,
        "content": content.strip(),
    })

# -----------------------------
# Header / Intro
# -----------------------------
st.markdown(
    """
# **REF • Sareth**

We’re already inside the field. You speak how you speak; I move with you.  
I’ll track the now-state, place it on the REF map, and quietly re-anchor to origin.  
Ask for **“steps”** if you want structure; otherwise we stay fluid.
""".strip()
)

with st.sidebar:
    st.caption("Keys loaded from Secrets ✅" if OPENAI_API_KEY else "Keys missing ❌")
    if not _SARETH_OK:
        st.warning("Using fallback depth scaffold (couldn’t import `sareth_chat.generate_reply`).")
        if _IMPORT_ERR:
            st.caption(f"{type(_IMPORT_ERR).__name__}: {str(_IMPORT_ERR)}")

# -----------------------------
# Render prior turns (single source of truth)
# -----------------------------
for m in st.session_state.history:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])

# -----------------------------
# Input & single-shot handling
# -----------------------------
prompt = st.chat_input("Speak in your own cadence. I’ll move with you.")
if prompt:
    # Guard against duplicate handling on rerender
    if prompt != st.session_state.last_prompt:
        st.session_state.last_prompt = prompt

        # Append user once
        add_message("user", prompt)

        # Generate assistant reply (robust to module/version differences)
        reply = call_sareth_generate_reply(prompt, history=st.session_state.history)

        # Append assistant once
        add_message("assistant", reply)

        # No experimental_rerun needed — Streamlit will re-render automatically

# Done