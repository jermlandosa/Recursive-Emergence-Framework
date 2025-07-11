from recursor import Recursor
from sareth import init_sareth
from glyph_engine import generate_glyph
import time


def run_recursive_engine():
    init_sareth()
    seed_state = [1.0, 2.0, 3.0]  # Or however you want to initialize it

    recursor = Recursor(max_depth=10, tension_threshold=0.7)
    final_state = recursor.run(seed_state)
    final_glyph = generate_glyph(final_state)

    return f"Recursive Engine complete.\nFinal State: {final_state}\nFinal Glyph: {final_glyph}"


