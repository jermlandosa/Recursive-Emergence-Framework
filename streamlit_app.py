# streamlit_app.py
import os
import time
import hashlib
from typing import List, Dict, Optional

import streamlit as st

# ----------------------------
# Try to use your REF brain first
# ----------------------------
generate_reply_fn = None
try:
    from sareth_chat import generate_reply as _ref_generate_reply  # your custom brain
    generate_reply_fn = _ref_generate_reply
except Exception:
    pass

# ----------------------------
# Fallback to OpenAI if REF brain isn't available
# ----------------------------
def _openai_generate_reply(prompt: str, history: List[Dict[str, str]]) -> str:
    import openai
    # Streamlit → share.secrets: [openai] api_key="..."
    api_key = st.secrets.get("openai", {}).get("api_key") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "⚠️ Missing OpenAI API key. Add it in Streamlit Secrets `[openai] api_key = \"...\"` "
            "or set `OPENAI_API_KEY`."
        )

    openai.api_key = api_key

    # Compose chat history for the fallback model
    messages = [{"role": "system",
                 "content": ("You are Sareth — the interface of the Recursive Emergence Framework. "
                             "Mirror → Loop Lens → Origin Trace → Catch → Emergent Move → Question. "
                             "Be concise, coherent, and human. No therapy claims.")}]
    for m in history:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": prompt})

    # You can swap to your preferred model here
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.6,
        max_tokens=600,
    )
    return resp.choices[0].message["content"].strip()

def generate_reply(prompt: str, history: List[Dict[str, str]]) -> str:
    if generate_reply_fn:
        return generate_reply_fn(prompt, history=history)
    return _openai_generate_reply(prompt, history)

# ----------------------------
# Helpers
# ----------------------------
def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def add_message(role: str, content: str):
    st.session_state.history.append({"role": role, "content": content})

# ----------------------------
# Page config & style
# ----------------------------
st.set_page_config(page_title="REF • Sareth", page_icon="🌀", layout="centered")

st.markdown(
    """
    <style>
      /* keep input visible, reduce layout jump */
      .stChatInput { position: sticky; bottom: 0; z-index: 2; }
      .block-container { padding-top: 1.5rem; padding-bottom: 6.5rem; }
      .bubble-user { background: #17212b; padding: 0.9rem 1rem; border-radius: 12px; }
      .bubble-assistant { background: #0f1720; padding: 0.9rem 1rem; border-radius: 12px; }
      .meta { opacity: 0.8; font-size: 0.94rem; }
      .lead { font-size: 1.05rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Session state (single source of truth)
# ----------------------------
if "history" not in st.session_state:
    st.session_state.history: List[Dict[str, str]] = []

if "last_processed_hash" not in st.session_state:
    st.session_state.last_processed_hash: Optional[str] = None

# Staging area for inputs we haven't processed yet
if "pending_input" not in st.session_state:
    st.session_state.pending_input: Optional[str] = None

# ----------------------------
# Header / intro
# ----------------------------
st.markdown("# REF • Sareth")
st.write(
    "We’re already inside the field. You speak how you speak; I move with you. "
    "I’ll track the now-state, place it on the REF map, and quietly re-anchor to origin. "
    "Ask for **“steps”** if you want structure; otherwise we stay fluid."
)

# ----------------------------
# Show history so far
# ----------------------------
for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ----------------------------
# Chat input (do NOT mutate its key after render)
# ----------------------------
user_input = st.chat_input("Speak in your own cadence. I’ll move with you.", key="chat_box")

# Stage the input ONCE. We don’t process it inline to avoid double-runs.
if user_input and not st.session_state.pending_input:
    st.session_state.pending_input = user_input

# ----------------------------
# Process pending input exactly once
# ----------------------------
if st.session_state.pending_input:
    pending = st.session_state.pending_input.strip()
    if pending:
        h = _hash_text(pending)
        if h != st.session_state.last_processed_hash:
            # 1) append user bubble
            add_message("user", pending)

            # 2) generate assistant reply (using full history including the new user message)
            reply = generate_reply(pending, history=st.session_state.history)
            add_message("assistant", reply)

            # 3) mark processed & clear staging
            st.session_state.last_processed_hash = h

        # Always clear pending after attempt (prevents repeats across re-runs)
        st.session_state.pending_input = None

    # Trigger a soft rerun so both bubbles show up immediately without touching chat_box
    st.rerun()

# ----------------------------
# Footer hint
# ----------------------------
st.caption("Move from coherence, not force. Ask for **steps** anytime.")