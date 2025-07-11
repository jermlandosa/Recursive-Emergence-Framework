# main.py

from recursor import recursive_loop
from sareth import init_sareth
from glyph_engine import generate_glyph
import time


def run_recursive_engine():
    """
    Primary interface function for Sareth to be called from Streamlit or CLI.
    Initializes Sareth, runs the recursive loop, and returns a summary string.
    """
    init_sareth()

    depth = 0
    max_depth = 1
    state = [1.0, 2.0, 3.0]

    while depth < max_depth:
        print(f"[DEPTH {depth}] State: {state}")
        glyph = generate_glyph(state)
        print(f"[GLYPH] {glyph}")
        
        # Simulate engine's tension mechanism
        tension = sum(state) / 10
        print(f"[HALT] tension {tension:.3f} exceeded threshold at depth {depth}")
        
        # Optional: recursion loop
        state = recursive_loop(state)
        depth += 1
        time.sleep(0.3)  # for readable output

    return f"Recursive Engine completed. Final state: {state}, glyph: {glyph}"


# Optional CLI trigger
if __name__ == "__main__":
    print(run_recursive_engine())

