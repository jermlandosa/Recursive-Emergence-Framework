from recursor import Recursor
from sareth import run_sareth_test
from glyph_engine import generate_glyph  # if needed
from logger import StateLogger
from visualizer import Visualizer

def run_recursive_engine(depth: int = 10, threshold: float = 0.7):
    """Convenience wrapper used by the Streamlit UI."""
    seed_state = [1.0, 2.0, 3.0]
    engine = Recursor(max_depth=depth, tension_threshold=threshold)
    final_state = engine.run(seed_state)

    glyph_trace = engine.glyph_engine.trace()
    last_glyph = glyph_trace[-1][1] if glyph_trace else None

    if len(glyph_trace) >= depth:
        reason = "depth_limit"
    else:
        reason = "complete"

    return final_state, last_glyph, reason


# Optional Streamlit UI block (runs only if Streamlit is available)
try:
    import streamlit as st

    st.title("Sareth Interface Test")
    if st.button("Run Sareth"):
        output = run_sareth_test()
        st.success(output)

except Exception as e:
    print(f"[Streamlit UI skipped]: {e}")


if __name__ == "__main__":
    state, glyph, reason = run_recursive_engine(depth=15, threshold=0.2)

    # Visualize recursion
    vis = Visualizer(StateLogger())
    vis.logger.logs = [{'depth': i, 'state': s} for i, s in enumerate([state])]
    vis.plot_state_evolution()

    print(f"Final State: {state}")
    print(f"Last Glyph: {glyph}")
    print(f"Halt Reason: {reason}")

    result = run_sareth_test()
    print("Sareth Test Output:", result)



