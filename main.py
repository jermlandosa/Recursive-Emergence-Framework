from recursor import Recursor
from test_tools import run_sareth_test  # type: ignore
from visualizer import Visualizer
from logger import StateLogger
from recursor import Recursor

if __name__ == "__main__":
    state, glyph, reason = run_recursive_engine(depth=15, threshold=0.2)

    # Visualize recursion
    vis = Visualizer(StateLogger())
    vis.logger.logs = [{"depth": 0, "state": state}]
    vis.plot_state_evolution()

    # Print glyph history
    engine.glyph_engine.print_trace()
