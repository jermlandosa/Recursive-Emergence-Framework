import os
import streamlit as st
from openai import OpenAI
import sareth_chat

api_key = st.secrets.get("openai", {}).get("api_key") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("Missing OpenAI API key. Add it in Settings → Secrets.")
    st.stop()
client = OpenAI(api_key=api_key)

st.title("REF • Sareth")
st.write(
    "We’re already inside the field. You speak how you speak; I move with you. "
    "I’ll track the now-state, place it on the REF map, and quietly re-anchor to origin. "
    "Ask for “steps” if you want structure; otherwise we stay fluid."
)

# --- session state setup ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Chat input ---
user_text = st.chat_input("Speak in your own cadence. I’ll move with you.")

if user_text:
    # 1. Show user's message
    with st.chat_message("user"):
        st.markdown(user_text)

    # 2. Append user message to history
    st.session_state.history.append({"role": "user", "content": user_text})

    # 3. Generate reply ONLY ONCE
    reply = sareth_chat.generate_reply(
        client=client,
        history=st.session_state.history,
        last_user_text=user_text,
        model="gpt-4o-mini",
        temperature=0.65,
        max_tokens=320,
    )

    # 4. Append assistant reply once
    st.session_state.history.append({"role": "assistant", "content": reply})

    # 5. Show assistant reply immediately
    with st.chat_message("assistant"):
        st.markdown(reply)

# --- Render previous history ---
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])