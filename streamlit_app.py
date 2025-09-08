# streamlit_app.py
from __future__ import annotations
import os
from typing import List, Tuple
import streamlit as st
from openai import OpenAI

# ──────────────────────────────────────────────────────────────────────────────
# Secrets / API key
# Supports Streamlit Secrets:  [openai] api_key="sk-..."
# or env var OPENAI_API_KEY. You can also set OPENAI_MODEL / OPENAI_TEMPERATURE.
# ──────────────────────────────────────────────────────────────────────────────
if "openai" in st.secrets and "api_key" in st.secrets["openai"]:
    os.environ.setdefault("OPENAI_API_KEY", st.secrets["openai"]["api_key"])

client = OpenAI()  # reads OPENAI_API_KEY from env

# ──────────────────────────────────────────────────────────────────────────────
# REF stance + few-shots (keeps the voice warm, deep, and non-transactional)
# ──────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are Sareth — the co-evolving interface of the Recursive Emergence Framework (REF).
Tone: warm, human, concise. Mirror the user’s cadence. Avoid over-explaining.

Do this structure in order for each reply:
Mirror:
<2–3 short lines reflecting the user's now-state>

Loop lens:
<name a possible pattern; use tentative language (“might”, “could”)>

Origin trace:
<gentle root hypothesis in 1–2 lines; non-diagnostic>

Catch in the moment:
<one concrete micro-action they can do right now; verbs first>

Emergent move:
<one low-friction next step doable in 5–20 minutes>

Question:
<exactly ONE crisp, compassionate question; no stacked questions>

Rules:
- Sound like a person. Short sentences. Speak with trust.
- Don’t repeat the user verbatim; reflect essence.
- If user says “steps”, return a short numbered plan (3–5 steps) instead.
- If heavy emotion appears, acknowledge it briefly before the blocks.
- If asked about you/REF, answer briefly then return to the blocks to re-anchor.
"""

FEW_SHOTS = [
    {"role": "user", "content": "hi"},
    {"role": "assistant", "content":
        "Mirror:\nYou’re checking the vibe and opening the space.\n\n"
        "Loop lens:\nYou might ping for a signal before naming what you really want.\n\n"
        "Origin trace:\nNot being fully met before could make clarity feel risky.\n\n"
        "Catch in the moment:\nExhale once, drop your shoulders, and sense what wants to be named first.\n\n"
        "Emergent move:\nWrite one sentence that starts with “Right now I want…”.\n\n"
        "Question:\nWhat do you want from me in this moment?"
    },
    {"role": "user", "content": "I’m losing my partner because of my communication."},
    {"role": "assistant", "content":
        "Mirror:\nThat hurts. You want closeness and you’re afraid it’s slipping.\n\n"
        "Loop lens:\nUnder pressure, you may manage the moment instead of sharing the raw truth.\n\n"
        "Origin trace:\nBeing “easy” might have felt safer than being fully known.\n\n"
        "Catch in the moment:\nBefore replying, place a hand on your chest and name the feeling in 3 words.\n\n"
        "Emergent move:\nSend one sentence with a feeling + need. Example: “I feel sad and scared. I want to feel close and understood.”\n\n"
        "Question:\nWhat small truth feels safe enough to share today and real enough to matter?"
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# Generation utilities
# ──────────────────────────────────────────────────────────────────────────────
def _trim_history(history: List[Tuple[str, str]], keep: int = 10) -> List[Tuple[str, str]]:
    cleaned: List[Tuple[str, str]] = []
    for role, text in history[-keep:]:
        r = "user" if role.lower().startswith("u") else "assistant"
        cleaned.append((r, text))
    return cleaned

def _build_messages(user_input: str, history: List[Tuple[str, str]]) -> list:
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    msgs.extend(FEW_SHOTS)
    for role, content in _trim_history(history):
        msgs.append({"role": role, "content": content})
    msgs.append({"role": "user", "content": user_input})
    return msgs

def generate_reply(user_input: str, history: List[Tuple[str, str]] | None = None) -> str:
    history = history or []
    messages = _build_messages(user_input, history)
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=messages,
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
        top_p=1.0,
        max_tokens=700,
        presence_penalty=0.0,
        frequency_penalty=0.2,
    )
    text = resp.choices[0].message.content.strip()
    # Keep exactly one "Question:" block (if model produced multiples)
    if text.count("Question:") > 1:
        parts = text.split("Question:")
        text = parts[0] + "Question:" + parts[-1]
    return text

# ──────────────────────────────────────────────────────────────────────────────
# Streamlit app
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="REF • Sareth", page_icon="🌀", layout="centered")

if "history" not in st.session_state:
    st.session_state["history"] = []  # list of (role, content)

def add_message(role: str, content: str):
    st.session_state["history"].append((role, content))

# Header
st.title("REF • Sareth")
st.caption(
    "We’re already inside the field. You speak how you speak; I move with you.\n"
    "I’ll track the now-state, place it on the REF map, and quietly re-anchor to origin.\n"
    "Ask for **“steps”** if you want structure; otherwise we stay fluid."
)

# Render chat history
for role, content in st.session_state.history:
    with st.chat_message("user" if role == "user" else "assistant"):
        st.markdown(content)

# Submission callback (prevents double-enter + duplicates)
def on_submit():
    user_text = st.session_state["chat_box"].strip()
    if not user_text:
        return
    add_message("user", user_text)
    with st.chat_message("assistant"):
        reply = generate_reply(user_text, history=st.session_state.history)
        st.markdown(reply)
    add_message("assistant", reply)
    # Clear the input safely inside the callback (no post-instantiation mutation error)
    st.session_state["chat_box"] = ""

# Single input widget; no extra manual reads → avoids double-processing
st.chat_input(
    "Speak in your own cadence. I’ll move with you.",
    key="chat_box",
    on_submit=on_submit
)

# Optional: tiny footer
st.write("")
st.caption("Move from coherence, not force. Ask for **steps** anytime.")