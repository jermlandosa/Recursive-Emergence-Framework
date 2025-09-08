# streamlit_app.py  (only the relevant bits)
import streamlit as st
from sareth_chat import generate_reply  # ← use the refactor above

st.set_page_config(page_title="REF • Sareth", page_icon="🌀", layout="centered")

if "history" not in st.session_state:
    st.session_state["history"] = []

def add_message(role: str, content: str):
    st.session_state["history"].append((role, content))

# --- UI ---
st.title("REF • Sareth")
st.caption("We’re already inside the field. You speak how you speak; I move with you.\n"
           "I’ll track the now-state, place it on the REF map, and quietly re-anchor to origin.\n"
           "Ask for “steps” if you want structure; otherwise we stay fluid.")

# Chat bubbles
for role, content in st.session_state.history:
    with st.chat_message("user" if role == "user" else "assistant"):
        st.markdown(content)

# One clean input widget with on_submit callback
def on_submit():
    user_text = st.session_state["chat_box"].strip()
    if not user_text:
        return
    add_message("user", user_text)
    with st.chat_message("assistant"):
        reply = generate_reply(user_text, history=st.session_state.history)
        st.markdown(reply)
    add_message("assistant", reply)
    st.session_state["chat_box"] = ""  # safe because we clear before re-render

st.chat_input(
    "Speak in your own cadence. I’ll move with you.",
    key="chat_box",
    on_submit=on_submit
)