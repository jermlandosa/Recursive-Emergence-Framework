"""
Streamlit front-end for the Recursive Emergence Framework + Sareth v3.1
---------------------------------------------------------------------
"""

# ── Safe import so the file can be run outside Streamlit ──────────────────────
try:
    import streamlit as st
    STREAMLIT = True
except ModuleNotFoundError:  # fallback for plain-python runs / CI
    STREAMLIT = False

from recursor import Recursor
from visualizer import Visualizer
from logger import StateLogger
from test_tools import Sareth            # ← NEW location of the class

# ── Convenience wrapper for the core engine ──────────────────────────────────
def run_recursive_engine(*, depth: int = 10, threshold: float = 0.7):
    seed_state = [1.0, 2.0, 3.0]
    engine = Recursor(max_depth=depth, tension_threshold=threshold)
    final_state = engine.run(seed_state)

    glyph_trace = engine.glyph_engine.trace()
    last_glyph  = glyph_trace[-1][1] if glyph_trace else None
    reason      = "depth_limit" if len(glyph_trace) >= depth else "complete"
    return final_state, last_glyph, reason


# ── Streamlit UI ─────────────────────────────────────────────────────────────
if STREAMLIT:
    st.set_page_config(page_title="Sareth + REF", layout="wide")
    st.title("🌀  Recursive Emergence Framework")

    # Sidebar – engine controls
    with st.sidebar:
        st.header("🔁  Run Recursive Engine")
        depth_slider   = st.slider("Max Recursion Depth", 1, 20, 10,
                                   key="depth_slider")
        tension_slider = st.slider("Tension Threshold", 0.0, 1.0, 0.7,
                                   key="tension_slider")

        if st.button("▶️ Run Engine", key="run_engine_btn"):
            state, glyph_id, halt_reason = run_recursive_engine(
                depth=depth_slider, threshold=tension_slider
            )
            st.markdown(f"**Final State:** `{state}`")
            st.markdown(f"**Last Glyph:** `{glyph_id}`")
            st.markdown(f"**Halt Reason:** `{halt_reason}`")

    # Chat interface with Sareth
    st.divider()
    st.subheader("🧠  Converse with Sareth (Recursive Agent)")

    if "sareth_agent" not in st.session_state:
        st.session_state["sareth_agent"] = Sareth()

    user_msg = st.chat_input("Enter a recursive reflection…")
    if user_msg:
        agent = st.session_state["sareth_agent"]
        with st.chat_message("user"):
            st.markdown(user_msg)

        bot_reply = agent.observe(user_msg)
        with st.chat_message("Sareth"):
            st.markdown(bot_reply)

        # Show last 5 memory entries
        st.expander("📚  Recent Memory (last 5)").json(
            agent.memory[-5:]
        )


# ── CLI entry-point (optional) ───────────────────────────────────────────────
if __name__ == "__main__" and not STREAMLIT:
    # Run once via CLI for quick sanity-check
    state, glyph, reason = run_recursive_engine(depth=15, threshold=0.2)
    print(f"Final State: {state}")
    print(f"Last Glyph:  {glyph}")
    print(f"Halt Reason: {reason}")

    # Minimal visualisation
    vis = Visualizer(StateLogger())
    vis.logger.logs = [{"depth": 0, "state": state}]
    vis.plot_state_evolution()







