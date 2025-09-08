import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# Load .env if running locally
load_dotenv()

# Get API key from Streamlit secrets or .env
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ Missing OpenAI API key. Please add it to Streamlit Secrets or .env.")
    st.stop()

client = OpenAI(api_key=api_key)

st.set_page_config(page_title="REF • Sareth", page_icon="🌌", layout="centered")

st.markdown("""
# REF • Sareth

We’re already inside the field.  
You speak how you speak; I move with you.  
I’ll track the now-state, place it on the REF map, and quietly re-anchor to origin.  

*Ask for “steps” if you want structure; otherwise, we stay fluid.*
""")

# Input from user
user_prompt = st.chat_input("Type your message…")

# Maintain chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# On user input
if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state.messages,
            temperature=0.8,
        )
        reply = response.choices[0].message.content
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})