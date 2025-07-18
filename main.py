"""Command line entrypoint and optional Streamlit UI for the REF engine."""

from logger import StateLogger
from visualizer import Visualizer
from test_tools import run_sareth_test
from ref_engine import run_recursive_engine
from recursor import Recursor


def run_recursive_engine_local(*, depth: int = 10, threshold: float = 0.7):
    """Run the Recursor with a simple numeric seed state and return the engine."""
    engine = Recursor(max_depth=depth, tension_threshold=threshold)

    seed_state = [1.0, 1.5, 2.0]
    final_state = engine.run(seed_state)

    trace = engine.glyph_engine.trace()
    glyph = trace[-1][1] if trace else ""

    return final_state, glyph, "complete", engine


# Optional Streamlit UI
try:
    import streamlit as st

    st.set_page_config(page_title="Sareth Interface", layout="centered")
    st.title("🌀 Recursive Emergence Framework")

    st.subheader("Run Recursive Engine")
    depth = st.slider("Max Recursion Depth", 1, 20, 10)
    tension = st.slider("Tension Threshold", 0.0, 1.0, 0.7)

    if st.button("▶️ Run Recursive Engine"):
        state, glyph, reason, _ = run_recursive_engine_local(depth=depth, threshold=tension)
        st.write(f"**Final State:** {state}")
        st.write(f"**Last Glyph:** {glyph}")
        st.write(f"**Halt Reason:** `{reason}`")

    st.subheader("Run Sareth Test")
    if st.button("🧪 Run Sareth"):
        result = run_sareth_test()
        st.success(result)

except Exception as e:
    print(f"[Streamlit Disabled] {e}")

# CLI Entry Point
if __name__ == "__main__":
    state, glyph, reason, engine = run_recursive_engine_local(depth=15, threshold=0.2)

    vis = Visualizer(StateLogger())
    vis.logger.logs = [{'depth': i, 'state': s} for i, s in enumerate([state])]
    vis.plot_state_evolution()

    print(f"Final State: {state}")
    print(f"Last Glyph: {glyph}")
    print(f"Halt Reason: {reason}")

    result = run_sareth_test()
    print("Sareth Test Output:", result)
