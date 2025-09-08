import os
import streamlit as st
from openai import OpenAI

# -----------------------------
# API KEY HANDLER (NEW)
# -----------------------------
def get_openai_api_key() -> str | None:
    """
    Load OpenAI API key from multiple possible sources:
    1) Streamlit Secrets flat: OPENAI_API_KEY
    2) Streamlit Secrets sectioned: [openai].api_key
    3) Environment variables
    """
    return (
        st.secrets.get("OPENAI_API_KEY")
        or (st.secrets.get("openai", {}) or {}).get("api_key")
        or os.getenv("OPENAI_API_KEY")
    )

def require_openai_key() -> str:
    """
    Require the OpenAI API key and stop app if missing.
    """
    api_key = get_openai_api_key()
    if not api_key:
        st.error(
            "🚨 Missing OpenAI API key.\n\n"
            "Add it under **Settings → Secrets** as:\n\n"
            "```\nOPENAI_API_KEY = \"sk-...\"\n```\n"
            "**or**:\n\n"
            "```\n[openai]\napi_key = \"sk-...\"\n```"
        )
        st.stop()
    os.environ["OPENAI_API_KEY"] = api_key
    return api_key

# -----------------------------
# SETUP CLIENT
# -----------------------------
api_key = require_openai_key()
client = OpenAI(api_key=api_key)

# -----------------------------
# APP UI
# -----------------------------
st.set_page_config(page_title="REF • Sareth", layout="centered")
st.title("REF • Sareth")

st.markdown(
    """
    We’re already inside the field.  
    You speak how you speak; I move with you.  
    I’ll track the now-state, place it on the REF map, and quietly re-anchor to origin.  
    Ask for **“steps”** if you want structure; otherwise we stay fluid.
    """
)

# -----------------------------
# CHAT INPUT
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                temperature=0.7,
            )
            output = response.choices[0].message.content
            st.markdown(output)
            st.session_state.messages.append(
                {"role": "assistant", "content": output}
            )
        except Exception as e:
            st.error(f"⚠️ OpenAI API error: {e}")