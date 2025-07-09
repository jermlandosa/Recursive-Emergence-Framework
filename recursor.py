# recursor.py
from memory import RecursiveMemory
from evaluator import Evaluator
from logger import StateLogger
from glyph_engine import GlyphEngine

class Recursor:
    """
    Core engine: iteratively transforms `state`, logging depth-wise data,
    generating glyphs, and halting on convergence or excess tension.
    """
    def __init__(self, *, max_depth: int = 10, tension_threshold: float = 0.7):
        self.memory            = RecursiveMemory()
        self.evaluator         = Evaluator()
        self.logger            = StateLogger()
        self.glyph_engine      = GlyphEngine()
        self.max_depth         = max_depth
        self.tension_threshold = tension_threshold

    def run(self, seed_state):
        state = seed_state
        self.memory.store_state(state)  # persist initial state

        for depth in range(self.max_depth):
            # 1️⃣  Log the raw state
            self.logger.log_state(depth, state)

            # 2️⃣  Emit glyph
            glyph = self.glyph_engine.generate(state, depth)
            print(f"[GLYPH] {glyph}")

            # 3️⃣  Tension check
            tension = self.evaluator.calculate_tension(state)
            if tension > self.tension_threshold:
                print(f"[HALT] tension {tension:.3f} exceeded threshold at depth {depth}")
                break

            # 4️⃣  Transform / recurse
            next_state = self.evaluator.recurse(state, self.memory)

            # 5️⃣  Convergence check
            if self.evaluator.has_converged(state, next_state):
                print(f"[CONVERGED] at depth {depth}")
                state = next_state
                self.memory.store_state(state)
                break

            # 6️⃣  Persist state & iterate
            state = next_state
            self.memory.store_state(state)

        return state

