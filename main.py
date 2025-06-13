from visualizer import Visualizer
from logger import StateLogger
from recursor import Recursor

if __name__ == "__main__":
    seed_input = [1.0, 2.0, 3.0]
    engine = Recursor(max_depth=15, tension_threshold=0.2)
    final_state = engine.run(seed_input)

    # Visualize recursion
    vis = Visualizer(engine.logger)
    vis.plot_state_evolution()

    # Print glyph history
    engine.glyph_engine.print_trace()
