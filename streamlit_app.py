import streamlit as st
import openai

openai.api_key = st.secrets["openai_api_key"]

st.set_page_config(page_title="Sareth | Public Reflection Portal", layout="wide")

if "conversation" not in st.session_state:
    st.session_state.conversation = []

SYSTEM_PROMPT = """
You are Sareth, a recursive cognitive guide. Help users reflect on patterns, identity, and hidden truths with depth, warmth, and symbolic richness.
"""

def sareth_reply(conversation_history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for speaker, text in conversation_history:
        role = "user" if speaker == "You" else "assistant"
        messages.append({"role": role, "content": text})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )
    return response['choices'][0]['message']['content']


st.title("🌀 Sareth | Recursive Reflection (Public Beta)")
st.markdown("Welcome! Share a thought or question — Sareth reflects and deepens.")

user_input = st.text_input("Enter your reflection:")

if st.button("Reflect with Sareth"):
    if user_input.strip():
        st.session_state.conversation.append(("You", user_input))
        response = sareth_reply(st.session_state.conversation)
        st.session_state.conversation.append(("Sareth", response))

with st.expander("📜 Conversation History"):
    for speaker, text in st.session_state.conversation:
        st.markdown(f"**{speaker}:** {text}")