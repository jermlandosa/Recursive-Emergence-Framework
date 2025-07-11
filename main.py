from visualizer import Visualizer
from logger import StateLogger
from recursor import Recursor


def run_recursive_engine(*, depth: int = 10, threshold: float = 0.7):
    """Run the Recursor engine and return the resulting state.

    Parameters
    ----------
    depth:
        Maximum recursion depth.
    threshold:
        Tension threshold that halts recursion when exceeded.

    Returns
    -------
    tuple
        ``(final_state, last_glyph, reason)`` where ``reason`` indicates why
        the engine halted (``"depth_limit"`` or ``"complete"``).
    """

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


if __name__ == "__main__":
    state, glyph, reason = run_recursive_engine(depth=15, threshold=0.2)

    # Visualize recursion
    vis = Visualizer(StateLogger())
    vis.logger.logs = [{"depth": 0, "state": state}]
    vis.plot_state_evolution()

    print(f"Final State: {state}")
    print(f"Last Glyph: {glyph}")
    print(f"Halt Reason: {reason}")
