import streamlit as st
from test_tools import Sareth, run_sareth_test

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

# Sareth chat interface
if "sareth_agent" not in st.session_state:
    st.session_state.sareth_agent = Sareth()

st.subheader("Talk to Sareth")

user_input = st.chat_input("What’s surfacing for you?")
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    response = st.session_state.sareth_agent.observe(user_input)
    with st.chat_message("Sareth"):
        st.markdown(response)

# Optional: Show memory
with st.expander("🔍 View Sareth Memory"):
    for memory in st.session_state.sareth_agent.memory[-5:]:
        st.markdown(f"**You** → {memory['input']}")
        st.markdown(f"**Sareth** → {memory['recursion_trace'][-1]}")





