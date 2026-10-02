import streamlit as st
from dataclasses import asdict
from rve.live import ensure_chat_state, messages_for_llm
from rve.openai_client import openai_client
from rve.reflection import generate_response
from rve.glyphs import map_text_to_glyph_events

st.set_page_config(page_title="Recursive Emergence Framework", page_icon="🧭", layout="wide")
ensure_chat_state()
st.session_state.setdefault("last_run", None)

st.title("Recursive Emergence Framework 🧭")
st.caption("Sareth · Clear answers, with an optional check before responding")
colA, colB, colC = st.columns([3, 3, 1])
with colA:
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"])
with colB:
    reflection = st.toggle("Review before answering", value=True,
        help="Checks the draft for concrete mistakes and revises when needed. Self-review can still be wrong and uses additional model calls.")
with colC:
    if st.button("Reset"):
        st.session_state.chat.clear()
        st.session_state.glyph_trace.clear()
        st.session_state.last_response = ""
        st.session_state.last_run = None
        st.rerun()

with st.expander("Sareth instructions"):
    st.session_state.system_prompt = st.text_area("System prompt",
        value=st.session_state.system_prompt, height=140)

left, right = st.columns([3, 2])
with left:
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    user_input = st.chat_input("Speak to Sareth…")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        # Commit the turn only when generation succeeds; failed retries do not
        # leave duplicated user messages in the model's context.
        context = messages_for_llm() + [{"role": "user", "content": user_input}]
        with st.chat_message("assistant"):
            try:
                with st.spinner("Preparing and reviewing an answer…" if reflection else "Preparing an answer…"):
                    result = generate_response(openai_client(), context,
                        model=model, reflection=reflection)
            except Exception:
                st.error("Sareth could not generate an answer. Check the model connection and send your message again.")
            else:
                st.markdown(result.answer)
                if "failed" in result.status:
                    st.warning("The review could not finish. Showing the original draft.")
                st.session_state.chat.extend([
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": result.answer},
                ])
                st.session_state.last_response = result.answer
                st.session_state.last_run = asdict(result)
                # Map the complete final answer, so keywords split across
                # provider chunks are not lost. Glyphs are annotations only.
                st.session_state.glyph_trace.extend(map_text_to_glyph_events(result.answer))

with right:
    st.subheader("Response details")
    run = st.session_state.last_run
    if run:
        labels = {"baseline": "Direct answer", "reviewed_unchanged": "Reviewed; draft retained",
                  "revised": "Reviewed and revised"}
        st.write(labels.get(run["status"], "Review incomplete; draft retained"))
        st.caption("Self-review does not independently verify facts.")
        with st.expander("Review notes and usage"):
            for issue in run["issues"]:
                st.write(f"{issue['kind']}: {issue['detail']}")
                st.write(issue["suggestion"])
            if not run["issues"]:
                st.write("No review issues recorded.")
            st.write(f"Model calls attempted: {run['calls']} · {run['elapsed_seconds']:.1f}s")
            st.write(f"Reported tokens: {run['prompt_tokens']} input / {run['completion_tokens']} output")
            if not run["usage_complete"]:
                st.caption("Token usage is incomplete.")
    st.subheader("Symbolic annotations")
    st.caption("Keyword annotations, not confidence or truth scores.")
    for ev in reversed(st.session_state.glyph_trace[-24:]):
        st.write(f"{ev['glyph']} · {ev['signal']}")
