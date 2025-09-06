import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="REF • Sareth", page_icon="🔁")

SYSTEM_PROMPT = (
    "You are Sareth, the REF assistant. Be concise, deep, and precise. "
    "Default to recursive truth checks and avoid fluff."
)

# --- Secrets check ---
api_key = st.secrets.get("OPENAI_API_KEY", "")
if not api_key:
    st.error(
        "Missing OPENAI_API_KEY in Streamlit Secrets. "
        "In Streamlit Cloud: App → Settings → Secrets → add OPENAI_API_KEY."
    )
    st.stop()

client = OpenAI(api_key=api_key)

# --- State ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

st.title("REF • Sareth")

with st.sidebar:
    st.subheader("Settings")
    model = st.text_input("OpenAI model", value="gpt-4o-mini")
    if st.button("Reset chat"):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()

# Render history (no system)
for m in st.session_state.messages:
    if m["role"] == "system":
        continue
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])

# Input + stream
user_text = st.chat_input("Type your message…")
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        out = st.empty()
        acc = ""

        stream = client.chat.completions.create(
            model=model,
            temperature=0.3,
            stream=True,
            # send full history including system so Sareth stays in effect
            messages=st.session_state.messages,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                acc += delta
                out.markdown(acc)

        st.session_state.messages.append({"role": "assistant", "content": acc})
