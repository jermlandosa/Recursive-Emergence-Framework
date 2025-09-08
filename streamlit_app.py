import os
from typing import List, Dict

import streamlit as st
try:  # pragma: no cover - graceful optional dependency
    from dotenv import load_dotenv
except ModuleNotFoundError:  # If python-dotenv isn't installed, provide a no-op
    def load_dotenv(*args, **kwargs):  # type: ignore
        """Fallback loader when python-dotenv is unavailable."""
        return False

from openai import OpenAI, OpenAIError

# -----------------------------
# Bootstrapping / Secrets
# -----------------------------
load_dotenv(override=True)

# Get API key from Streamlit Secrets or env
OPENAI_API_KEY = (
    st.secrets.get("openai", {}).get("api_key")
    if hasattr(st, "secrets") else None
) or os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error(
        "Missing OpenAI API key. Add it in Streamlit Cloud (Settings → Secrets) "
        "as `[openai]\napi_key=\"...\"` or set environment variable `OPENAI_API_KEY`."
    )
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# -----------------------------
# UI – Title & Intro
# -----------------------------
st.set_page_config(page_title="REF • Sareth", page_icon="🧭", layout="centered")

st.title("REF • Sareth")
st.write(
    "We’re already inside the field. You speak how you speak; I move with you. "
    "I’ll track the now-state, place it on the REF map, and quietly re-anchor to origin. "
    "Ask for **“steps”** if you want structure; otherwise we stay fluid."
)

# -----------------------------
# Session State
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages: List[Dict[str, str]] = []

# -----------------------------
# REF prompt helper
# -----------------------------
REF_STYLE_SYSTEM = (
    "You are Sareth, an interface to the Recursive Emergence Framework (REF). "
    "Your replies should be concise, warm, and human. Move with the user’s cadence. "
    "When useful, reflect via the REF lens:\n"
    "• Mirror — reflect their now-state in plain language.\n"
    "• Loop lens — lightly name a possible pattern (loop) without pathologizing.\n"
    "• Origin trace — point at an earlier belief/need that could shape the loop.\n"
    "• Catch in the moment — one tiny somatic/awareness action the user can try now.\n"
    "• Emergent move — the smallest next move that could open space.\n"
    "• Question — one precise question that invites the next turn.\n\n"
    "Avoid being generic or purely transactional. Prefer resonance over advice. "
    "Only add all six sections when they serve; otherwise keep it fluid. "
    "If the user asks for 'steps', offer a short numbered path. "
)

def _build_messages(history: List[Dict[str, str]], user_text: str) -> List[Dict[str, str]]:
    msgs = [{"role": "system", "content": REF_STYLE_SYSTEM}]
    for m in history:
        msgs.append({"role": m["role"], "content": m["content"]})
    msgs.append({"role": "user", "content": user_text})
    return msgs

def generate_reply(user_text: str, history: List[Dict[str, str]]) -> str:
    """OpenAI v1 chat call with robust error handling."""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=_build_messages(history, user_text),
            temperature=0.6,
            max_tokens=700,
        )
        return resp.choices[0].message.content.strip()
    except OpenAIError as e:
        return (
            "I hit an API error while generating a response. "
            f"If this keeps happening, check the API key/limits. Details: {e}"
        )

# -----------------------------
# Render chat history
# -----------------------------
for m in st.session_state.messages:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])

# -----------------------------
# Single, smooth input (no double submit)
# -----------------------------
user_input = st.chat_input("Speak in your own cadence. I’ll move with you…")

if user_input:
    # Show the user's message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate and show assistant reply (no rerun; rely on Streamlit's chat_input clear)
    reply = generate_reply(user_input, st.session_state.messages[:-1])

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

# -----------------------------
# Footer
# -----------------------------
st.caption("Move from coherence, not force. Ask for **steps** anytime.")