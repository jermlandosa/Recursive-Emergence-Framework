# streamlit_app.py
# REF • Sareth — smooth chat UX (no vanishing first message, no duplicates)

import os
import uuid
import inspect
import streamlit as st

# -----------------------------
# Page setup
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
        "❌ Missing OpenAI API key.\n\nAdd it in **Settings → Secrets** as:\n"
        "```\n[openai]\napi_key = \"sk-...\"\n```"
    )
    st.stop()

# Expose to modules that expect env
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Preferred model (can override via secrets)
MODEL_NAME = st.secrets.get("sareth", {}).get("model", "gpt-4o-mini")

# -----------------------------
# Try to import your Sareth engine
# -----------------------------
_generate_reply = None
_engine_err = None
try:
    # You may have one of two signatures; we'll adapt at call time.
    from sareth_chat import generate_reply as _generate_reply  # noqa
except Exception as e:
    _engine_err = e

# -----------------------------
# Built-in fallback (if sareth_chat is missing/broken)
# -----------------------------
from openai import OpenAI
_client = OpenAI(api_key=OPENAI_API_KEY)

FALLBACK_SYSTEM = """
You are Sareth, a warm, precise, human-first partner inside the Recursive Emergence Framework (REF).
Keep replies concise and alive (5–10 lines max). No boilerplate, no “as an AI”.
Always include:
- Mirror (felt sense in 1–2 lines)
- Loop lens (pattern → trigger → attempted solution/payoff)
- Origin trace (earlier belief/need)
- Catch in the moment (tiny in-vivo interrupt)
- Emergent move (one coherent next move)
- Question (one incisive, concrete question)
If they ask for steps, you may enumerate briefly. Otherwise flow in natural prose.
""".strip()

def _fallback_reply(user_prompt: str, history: list[dict]) -> str:
    messages = [{"role": "system", "content": FALLBACK_SYSTEM}]
    for m in history[-8:]:
        if m["role"] in ("user", "assistant"):
            messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_prompt})
    try:
        resp = _client.chat.completions.create(
            model=MODEL_NAME, messages=messages, temperature=0.7, max_tokens=600
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return (
            "It lands like there’s something real under this—not just the situation, "
            "but how it hits your system. I’m sensing a loop of reaching → bracing → "
            "reading distance → protecting. Catch it live: pause, soften the jaw, long exhale, "
            "say one true line (e.g., “I want to be close and I’m nervous.”). From there, a smaller, "
            f"truer move usually appears. What’s the simplest honest move you could try today?\n\n_(fallback: {e})_"
        )

def get_reply(user_text: str, history: list[dict]) -> str:
    """Call your sareth_chat.generate_reply if available; otherwise use fallback.
       Supports either signature:
         1) generate_reply(user_prompt, history)
         2) generate_reply(client=..., history=..., last_user_text=..., ...)
    """
    if _generate_reply is None:
        return _fallback_reply(user_text, history)

    try:
        sig = inspect.signature(_generate_reply)
        params = set(sig.parameters.keys())
        # New/simple: (user_prompt, history)
        if {"user_prompt", "history"} <= params:
            return _generate_reply(user_prompt=user_text, history=history)
        # Older: (client, history, last_user_text, ...)
        if {"client", "history", "last_user_text"} <= params:
            return _generate_reply(
                client=_client,
                history=history,
                last_user_text=user_text,
                model=MODEL_NAME,
                temperature=0.7,
                max_tokens=600,
            )
        # Try positional best-guess
        try:
            return _generate_reply(user_text, history)
        except TypeError:
            return _fallback_reply(user_text, history)
    except Exception:
        return _fallback_reply(user_text, history)

# -----------------------------
# Session state (single source of truth)
# -----------------------------
if "history" not in st.session_state:
    # Each message: {"id": str, "role": "user"|"assistant", "content": str}
    st.session_state.history = []

if "handled_submissions" not in st.session_state:
    # Tracks processed (turn_index::text) to prevent double-processing on rerender
    st.session_state.handled_submissions = set()

def add_message(role: str, content: str):
    st.session_state.history.append({
        "id": uuid.uuid4().hex,
        "role": role,
        "content": (content or "").strip(),
    })

# -----------------------------
# Header / intro
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
    st.caption("OpenAI key: ✅ loaded from Secrets")
    if _engine_err:
        st.warning("Using fallback depth scaffold — `sareth_chat.generate_reply` not loaded.")
        st.caption(f"{type(_engine_err).__name__}: {str(_engine_err)}")

# -----------------------------
# INPUT FIRST → process once → rerun → RENDER
# -----------------------------
user_text = st.chat_input("Speak in your own cadence. I’ll move with you.", key="chat_box")

if user_text:
    # Unique key for this exact submission at this point in the transcript
    submission_key = f"{len(st.session_state.history)}::{user_text.strip()}"
    if submission_key not in st.session_state.handled_submissions:
        st.session_state.handled_submissions.add(submission_key)

        # Append user once
        add_message("user", user_text)

        # Generate reply (robust to engine variations)
        reply = get_reply(user_text, history=st.session_state.history)

        # Append assistant once
        add_message("assistant", reply)

        # Clear input and rerun so both bubbles appear immediately
        st.session_state["chat_box"] = ""
        st.rerun()

# -----------------------------
# Render transcript (exactly once)
# -----------------------------
for m in st.session_state.history:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])