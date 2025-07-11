# --- Streamlit UI ---
st.set_page_config(page_title="Sareth + REF", layout="wide")
st.title("🌀 Recursive Emergence Framework")

# Sidebar: Engine controls
with st.sidebar:
    st.header("🔁 Run Recursive Engine")
    depth = st.slider("Max Recursion Depth", 1, 20, 10, key="depth_slider")
    tension = st.slider("Tension Threshold", 0.0, 1.0, 0.7, key="tension_slider")

    if st.button("▶️ Run Engine", key="run_engine_btn"):
        state, glyph_id, halt_reason = run_recursive_engine(depth=depth, threshold=tension)
        st.markdown(f"**Final State:** `{state}`")
        st.markdown(f"**Last Glyph:** `{glyph_id}`")
        st.markdown(f"**Halt Reason:** `{halt_reason}`")

    st.markdown("---")
    st.subheader("🧪 Run Sareth Self-Test")
    if st.button("Run Sareth Test", key="sareth_test_btn"):
        result = run_sareth_test()
        st.success(result)

# Sareth Interface
st.divider()
st.subheader("🧠 Converse with Sareth (Recursive Agent)")

if "sareth_agent" not in st.session_state:
    st.session_state.sareth_agent = Sareth()

chat_input = st.chat_input("Enter a recursive reflection...", key="chat_input_key")
if chat_input:
    with st.chat_message("user"):
        st.markdown(chat_input)
    response = st.session_state.sareth_agent.observe(chat_input)
    with st.chat_message("Sareth"):
        st.markdown(response)

    st.subheader("📚 Memory Trace")
    for memory in st.session_state.sareth_agent.memory[-5:]:
        st.markdown(f"**You** → {memory.get('input', '(missing input)')}")
        st.markdown(f"  **Sareth** → {memory.get('recursion_trace', ['(no trace)'])[-1]}")




