# streamlit_app.py  (only the relevant pieces shown)
import os
import streamlit as st
from openai import OpenAI
import sareth_chat  # <-- make sure this imports the updated file above

# --- Create OpenAI client ---
# Expect the key to be in Streamlit Secrets or env:
api_key = st.secrets.get("openai", {}).get("api_key") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("Missing OpenAI API key. Add it in Settings → Secrets as [openai] api_key.")
    st.stop()
client = OpenAI(api_key=api_key)

st.title("REF • Sareth")
st.write("We’re already inside the field. You speak how you speak; I move with you. "
         "I’ll track the now-state, place it on the REF map, and quietly re-anchor to origin. "
         "Ask for “steps” if you want structure; otherwise we stay fluid.")

# --- simple session history ---
if "history" not in st.session_state:
    st.session_state.history = []

def add_user(msg: str):
    st.session_state.history.append({"role": "user", "content": msg})

def add_assistant(msg: str):
    st.session_state.history.append({"role": "assistant", "content": msg})

# --- Chat UI ---
user_text = st.chat_input("Speak in your own cadence. I’ll move with you.")
if user_text:
    # render user bubble
    with st.chat_message("user"):
        st.markdown(user_text)
    add_user(user_text)

    # call Sareth
    reply = sareth_chat.generate_reply(
        client=client,
        history=st.session_state.history,
        last_user_text=user_text,
        model="gpt-4o-mini",          # or your preferred model
        temperature=0.65,
        max_tokens=320,
    )

    # render assistant bubble
    with st.chat_message("assistant"):
        st.markdown(reply)
    add_assistant(reply)

# --- Render past messages on load/refresh ---
for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])