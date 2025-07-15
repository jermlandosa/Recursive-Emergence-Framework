# glyph_engine.py
import hashlib
import json


class GlyphEngine:
    """
    Creates a short, human-readable hash (“glyph”) of each recursion state.
    This lets you track state-to-state evolution symbolically.
    """

    def __init__(self):
        self._trace = []  # [(depth, glyph), …]

    def generate(self, state, depth: int) -> str:
        state_str = json.dumps(state, sort_keys=True)
        glyph = hashlib.sha256(f"{depth}:{state_str}".encode()).hexdigest()[:12]
        self._trace.append((depth, glyph))
        return glyph

    def trace(self):
        return self._trace

    def print_trace(self):
        for depth, glyph in self._trace:
            print(f"Depth {depth:02d} → {glyph}")
