import openai
import streamlit as st
from test_tools import run_sareth_test

# Initialize OpenAI client with API key from Streamlit secrets
client = openai.OpenAI(api_key=st.secrets["openai"]["api_key"])

# --- App Setup ---
st.set_page_config(page_title="Sareth + REF", layout="wide")
st.title("🌌 Recursive Emergence Framework")

# Sidebar controls
with st.sidebar:
    st.header("Engine Options")
    depth = st.slider("Max Recursion Depth", 1, 20, 10, key="depth_slider")
    tension = st.slider("Tension Threshold", 0.0, 1.0, 0.7, key="tension_slider")

    if st.button("Run Sareth Test"):
        result = run_sareth_test()
        st.success(result)

# Initialize chat memory in session state
if "sareth_memory" not in st.session_state:
    st.session_state.sareth_memory = []

st.subheader("Talk to Sareth")

user_input = st.chat_input("What’s surfacing for you?")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Sareth, a brutally honest, recursive AI guide designed for co-evolution and insight."},
                {"role": "user", "content": user_input}
            ]
        )
        response = completion.choices[0].message.content

    except Exception as e:
        st.error(f"❌ OpenAI API call failed: {e}")
        response = "Sorry, Sareth encountered an error."

    with st.chat_message("Sareth"):
        st.markdown(response)

    st.session_state.sareth_memory.append({"input": user_input, "response": response})

# Optional: Display recent memory
with st.expander("🔍 View Sareth Memory"):
    for mem in st.session_state.sareth_memory[-5:]:
        st.markdown(f"**You** → {mem['input']}")
        st.markdown(f"**Sareth** → {mem['response']}")







