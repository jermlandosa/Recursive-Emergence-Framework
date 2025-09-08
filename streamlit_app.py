import os
import streamlit as st
from openai import OpenAI
import sareth_chat

# --- OpenAI client ---
api_key = st.secrets.get("openai", {}).get("api_key") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("Missing OpenAI API key. Add it in Settings → Secrets or set OPENAI_API_KEY.")
    st.stop()
client = OpenAI(api_key=api_key)

# --- UI header ---
st.title("REF • Sareth")
st.write(
    "We’re already inside the field. You speak how you speak; I move with you. "
    "I’ll track the now-state, place it on the REF map, and quietly re-anchor to origin. "
    "Ask for “steps” if you want structure; otherwise we stay fluid."
)

# --- session state ---
if "history" not in st.session_state:
    st.session_state.history = []  # list of {"role": "user"/"assistant", "content": str}

# --- 1) RENDER HISTORY (only place we display messages) ---
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 2) HANDLE NEW INPUT (no immediate display here) ---
user_text = st.chat_input("Speak in your own cadence. I’ll move with you.")
if user_text:
    # Append user's message once
    if not (st.session_state.history and st.session_state.history[-1]["role"] == "user"
            and st.session_state.history[-1]["content"] == user_text):
        st.session_state.history.append({"role": "user", "content": user_text})

    # Generate reply once (ensure sareth_chat.generate_reply DOES NOT append to history)
    reply = sareth_chat.generate_reply(
        client=client,
        history=st.session_state.history,
        last_user_text=user_text,
        model="gpt-4o-mini",
        temperature=0.65,
        max_tokens=320,
    )

    # Append assistant reply once
    st.session_state.history.append({"role": "assistant", "content": reply})

    # Re-render so the messages appear via the history loop (avoids duplicates)
    st.rerun()