# ─── streamlit_app.py ──────────────────────────────────────────────────────────
from recursor import Recursor
from visualizer import Visualizer
from logger import StateLogger
from test_tools import run_sareth_test           # ← no circular import
from sareth import Sareth                        # ← safe to import here

# ----------------------------------------------------------------------------- #
# 1) Load Streamlit only if it exists                                           #
# ----------------------------------------------------------------------------- #
try:
    import streamlit as st                      # works on Streamlit Cloud / local
    STREAMLIT = True
except ModuleNotFoundError:                     # running via  `python streamlit_app.py`
    STREAMLIT = False

# ----------------------------------------------------------------------------- #
# 2) Pure-Python engine helper (can run anywhere)                               #
# ----------------------------------------------------------------------------- #
def run_recursive_engine(*, depth: int = 10, threshold: float = 0.7):
    seed_state = [1.0, 2.0, 3.0]
    engine = Recursor(max_depth=depth, tension_threshold=threshold)
    final_state = engine.run(seed_state)

    glyph_trace = engine.glyph_engine.trace()
    last_glyph  = glyph_trace[-1][1] if glyph_trace else None
    reason      = "depth_limit" if len(glyph_trace) >= depth else "complete"
    return final_state, last_glyph, reason


# ----------------------------------------------------------------------------- #
# 3) Streamlit UI (only if Streamlit is available)                              #
# ----------------------------------------------------------------------------- #
if STREAMLIT:
    st.set_page_config(page_title="Sareth + REF", layout="wide")
    st.title("🌀 Recursive Emergence Framework")

    # ── sidebar controls ──────────────────────────────────────────────────────
    with st.sidebar:
        st.header("🔁 Run Recursive Engine")
        depth    = st.slider("Max Recursion Depth", 1, 20, 10, key="depth_slider")
        tension  = st.slider("Tension Threshold", 0.0, 1.0, 0.7, key="tension_slider")

        if st.button("▶️ Run Engine", key="engine_btn"):
            state, glyph_id, halt = run_recursive_engine(depth=depth, threshold=tension)
            st.markdown(f"**Final State:** `{state}`")
            st.markdown(f"**Last Glyph:** `{glyph_id}`")
            st.markdown(f"**Halt Reason:** `{halt}`")

        st.markdown("---")
        st.subheader("🧪 Run Sareth Self-Test")
        if st.button("Run Sareth Test", key="sareth_test_btn"):
            st.success(run_sareth_test())

    # ── Sareth chat - center column ───────────────────────────────────────────
    st.divider()
    st.subheader("🧠 Converse with Sareth")

    if "sareth_agent" not in st.session_state:
        st.session_state.sareth_agent = Sareth()

    user_msg = st.chat_input("Enter a recursive reflection…")
    if user_msg:
        with st.chat_message("user"):
            st.markdown(user_msg)

        reply = st.session_state.sareth_agent.observe(user_msg)
        with st.chat_message("Sareth"):
            st.markdown(reply)

        st.expander("📚 Recent Memory").write(
            st.session_state.sareth_agent.memory[-5:]
        )


# ----------------------------------------------------------------------------- #
# 4) CLI entry-point (safe even without Streamlit installed)                    #
# ----------------------------------------------------------------------------- #
if __name__ == "__main__" and not STREAMLIT:
    state, glyph, halt = run_recursive_engine(depth=15, threshold=0.2)
    print("Final State:", state)
    print("Last Glyph:", glyph)
    print("Halt Reason:", halt)





