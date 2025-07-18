from recursor import Recursor
from glyph_engine import GlyphEngine

def run_recursive_engine(depth=10, threshold=0.7):
    seed_state = [1.0, 2.0, 3.0]
    engine = Recursor(max_depth=depth, tension_threshold=threshold)
    final_state = engine.run(seed_state)

    glyph_trace = engine.glyph_engine.trace()
    last_glyph = glyph_trace[-1][1] if glyph_trace else None

    reason = "depth_limit" if len(glyph_trace) >= depth else "complete"
    return final_state, last_glyph, reason
