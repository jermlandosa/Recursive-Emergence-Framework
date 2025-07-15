from recursor import Recursor
from sareth_test_mode import run_sareth_test  # type: ignore
from visualizer import Visualizer
from logger import StateLogger

def run_recursive_engine(*, depth: int = 10, threshold: float = 0.7):
    """Run the Recursor with a simple numeric seed state."""
    engine = Recursor(max_depth=depth, tension_threshold=threshold)

    seed_state = [1.0, 1.5, 2.0]
    final_state = engine.run(seed_state)

    trace = engine.glyph_engine.trace()
    glyph = trace[-1][1] if trace else ""

    return final_state, glyph, "complete", engine


if __name__ == "__main__":
    state, glyph, reason, engine = run_recursive_engine(depth=15, threshold=0.2)

    # Visualize recursion
    vis = Visualizer(StateLogger())
    vis.logger.logs = [{"depth": 0, "state": state}]
    vis.plot_state_evolution()

    # Print glyph history
    engine.glyph_engine.print_trace()
