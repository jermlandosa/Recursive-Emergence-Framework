"""Command line entrypoint and optional Streamlit UI for the REF engine."""

from logger import StateLogger
from test_tools import run_sareth_test
from visualizer import Visualizer
from ref_engine import run_recursive_engine


# Optional Streamlit UI
try:
    import streamlit as st

    st.set_page_config(page_title="Sareth Interface", layout="centered")
    st.title("🌀 Recursive Emergence Framework")

    st.subheader("Run Recursive Engine")
    depth = st.slider("Max Recursion Depth", 1, 20, 10)
    tension = st.slider("Tension Threshold", 0.0, 1.0, 0.7)

    if st.button("▶️ Run Recursive Engine"):
        state, glyph, reason = run_recursive_engine(depth=depth, threshold=tension)
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
    state, glyph, reason = run_recursive_engine(depth=15, threshold=0.2)

    # Optional: visualize
    vis = Visualizer(StateLogger())
    vis.logger.logs = [{'depth': i, 'state': s} for i, s in enumerate([state])]
    vis.plot_state_evolution()

    print(f"Final State: {state}")
    print(f"Last Glyph: {glyph}")
    print(f"Halt Reason: {reason}")

    result = run_sareth_test()
    print("Sareth Test Output:", result)




