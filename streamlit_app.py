# --- streamlit_app.py (TOP of file) ---
import os
import uuid
import streamlit as st
from sareth_chat import generate_reply  # make sure this exists as shown below

st.set_page_config(page_title="REF • Sareth", page_icon="✨")

# ---------- Session boot ----------
if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts: {id, role, content}

if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None  # guards duplicates

def add_message(role: str, content: str):
    """Append a message exactly once per render; carries a unique id."""
    st.session_state.history.append({
        "id": uuid.uuid4().hex,
        "role": role,
        "content": content.strip(),
    })

# ---------- Header / Intro ----------
st.markdown(
    """
    # REF • Sareth

    We’re already inside the field. You speak how you speak; I move with you.  
    I’ll track the now-state, place it on the REF map, and quietly re-anchor to origin.  
    Ask for **“steps”** if you want structure; otherwise we stay fluid.
    """.strip()
)

# ---------- Render prior turns ----------
for m in st.session_state.history:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])

# ---------- Input & guarded processing ----------
prompt = st.chat_input("Speak in your own cadence. I’ll move with you.", key="chat_input")

if prompt:
    # 1) Guard: only handle a *new* prompt
    if prompt != st.session_state.last_prompt:
        st.session_state.last_prompt = prompt

        # 2) Append user's message once
        add_message("user", prompt)

        # 3) Generate Sareth's reply (your engine)
        reply = generate_reply(prompt, history=st.session_state.history)

        # 4) Append assistant message once
        add_message("assistant", reply)

        # 5) Rerender will happen automatically — no experimental_rerun
    else:
        # Same prompt detected in a re-render; do nothing.
        pass