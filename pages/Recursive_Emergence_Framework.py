import streamlit as st
from rve.live import ensure_chat_state, stream_chat, messages_for_llm, push_user, push_assistant
from rve.glyphs import map_text_to_glyph_events

st.set_page_config(page_title="Recursive Emergence Framework", page_icon="🧭", layout="wide")
ensure_chat_state()

# ---- Header ----
colA, colB, colC = st.columns([5, 2, 1])
with colA:
    st.title("Recursive Emergence Framework (Live) 🧭")
    st.caption("Streaming responses + real-time glyph mapping (Sareth mode)")
with colB:
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"], index=0)
with colC:
    if st.button("↺ Reset"):
        st.session_state.chat.clear()
        st.session_state.glyph_trace.clear()
        st.session_state.last_response = ""
        st.experimental_rerun()

with st.expander("System (Sareth)"):
    sys_new = st.text_area("System Prompt", value=st.session_state.system_prompt, height=140)
    if sys_new != st.session_state.system_prompt:
        st.session_state.system_prompt = sys_new
        st.success("System updated for the next turns.")

# ---- Layout ----
left, right = st.columns([3, 2], vertical_alignment="top")

with left:
    # History
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    user_input = st.chat_input("Speak to Sareth…")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        push_user(user_input)

        # Streamed assistant
        with st.chat_message("assistant"):
            slot = st.empty()
            full_text = ""
            for delta in stream_chat(messages_for_llm(), model=model, temperature=0.2):
                full_text += delta
                # live typing cursor
                slot.markdown(full_text + "▌")

                # Live glyph mapping per chunk
                evs = map_text_to_glyph_events(delta)
                if evs:
                    st.session_state.glyph_trace.extend(evs)

            # finalize
            slot.markdown(full_text)
            push_assistant(full_text)
            st.session_state.last_response = full_text

with right:
    st.subheader("Glyph Trace (live)")
    if not st.session_state.glyph_trace:
        st.info("As responses stream, detected glyph signals will appear here.")
    else:
        for ev in reversed(st.session_state.glyph_trace[-24:]):
            st.markdown(
                f"**{ev['glyph']}** — _{ev['signal']}_ · <span style='opacity:.6'>{ev['t']}</span>",
                unsafe_allow_html=True,
            )

    with st.expander("Last response (raw)"):
        st.code(st.session_state.last_response or "", language="markdown")
