# streamlit_app.py  (only the chat-related pieces shown)

import streamlit as st
from sareth_chat import make_client, generate_reply

# ---- secrets / client ----
API_KEY = st.secrets["openai"]["api_key"]  # <-- keep using Streamlit Secrets
client = make_client(API_KEY)

# ---- session state ----
if "history" not in st.session_state:
    st.session_state.history = []   # list of {"role": "user"|"assistant", "content": str}

def submit_user_message(user_text: str):
    """Append user once, generate reply once (prevents duplication)."""
    if not user_text.strip():
        return
    # 1) Append user to history
    st.session_state.history.append({"role": "user", "content": user_text.strip()})
    # 2) Generate reply using all prior turns EXCLUDING the new one (we pass it separately)
    #    Because we already appended the user message, we pass history[:-1] and last_user_text
    reply = generate_reply(
        client=client,
        history=st.session_state.history[:-1],
        last_user_text=user_text,
        model="gpt-4o-mini",
        temperature=0.7,   # bump to 0.8 on heavy emotional topics if you want
        max_tokens=600
    )
    # 3) Append assistant
    st.session_state.history.append({"role": "assistant", "content": reply})

# ---- UI ----
st.title("REF • Sareth")
st.markdown(
    "We’re already inside the field. You speak how you speak; I move with you. "
    "I’ll track the now-state, place it on the REF map, and quietly re-anchor to origin. "
    "Ask for **“steps”** if you want structure; otherwise we stay fluid."
)

# render transcript
for m in st.session_state.history:
    if m["role"] == "user":
        st.chat_message("user").markdown(m["content"])
    else:
        st.chat_message("assistant").markdown(m["content"])

# input box
prompt = st.chat_input("Speak in your own cadence. I’ll move with you.")
if prompt:
    submit_user_message(prompt)   # <- single call prevents double-echo
    st.experimental_rerun()