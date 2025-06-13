# glyph_engine.py
import hashlib
import json

class GlyphEngine:
    def __init__(self):
        self.glyph_trace = []

    def generate_glyph(self, state, depth):
        # Use a hash of the state + depth as symbolic representation
        state_str = json.dumps(state)
        glyph = hashlib.sha256(f"{depth}-{state_str}".encode()).hexdigest()[:12]  # short glyph
        self.glyph_trace.append((depth, glyph))
        return glyph

    def get_trace(self):
        return self.glyph_trace

    def print_trace(self):
        for depth, glyph in self.glyph_trace:
            print(f"Depth {depth}: Glyph {glyph}")
