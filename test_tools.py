import os
import json
import datetime
import hashlib

SHALLOW_SIGNALS = ["it depends", "i'm not sure", "could be", "maybe", "just", "kind of"]
DEPTH_KEYWORDS = ["recursive", "across time", "paradox", "identity", "coherence"]
MEMORY_FILE = "sareth_memory.json"
MEMORY_LIMIT = 1000


def generate_glyph_from_text(text: str) -> str:
    """Create a short deterministic glyph from any text."""
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def is_deep(insight: str) -> bool:
    """Very simple heuristic depth‑check used by Sareth."""
    if not insight:
        return False
    too_short = len(insight.strip()) < 30
    vague = any(phrase in insight.lower() for phrase in SHALLOW_SIGNALS)
    return not (too_short or vague)


class Sareth:
    """Lightweight recursive reflection agent used in the Streamlit demo."""

    def __init__(self, name: str = "Sareth", version: str = "REF_3.1"):
        self.name = name
        self.version = version
        self.memory: list[dict] = []

    # ───────────────────────── Conversation entry‑point ──────────────────────────
    def observe(self, input_text: str) -> str:
        timestamp = datetime.datetime.now().isoformat()
        glyph = generate_glyph_from_text(input_text)

        initial_reflection = self.process(input_text)
        feedback          = self.feedback_loop(input_text, initial_reflection)
        recursion_trace   = self.multi_depth_reflection(initial_reflection, depth=5)

        self._store_memory(
            timestamp=timestamp,
            input_text=input_text,
            initial_reflection=initial_reflection,
            feedback=feedback,
            recursion_trace=recursion_trace,
            glyph=glyph,
        )

        # Return the deepest reflection (or everything joined, if you prefer)
        return "\n".join(recursion_trace)

    # ───────────────────────────────── Internal helpers ──────────────────────────
    def process(self, input_text: str) -> str:
        if self.truth_check(input_text) and self.depth_scan(input_text):
            return self.reflect(input_text)
        return "⟁∅ Insight rejected by False Depth Drift Scan"

    # Basic filters --------------------------------------------------------------
    def truth_check(self, input_text: str) -> bool:
        return not any(flag in input_text.lower() for flag in SHALLOW_SIGNALS)

    def depth_scan(self, input_text: str) -> bool:
        return any(word in input_text.lower() for word in DEPTH_KEYWORDS)

    # Reflection + recursion -----------------------------------------------------
    def reflect(self, input_text: str) -> str:
        pulse = self.pulse_score(input_text)
        return (
            f"🪞 Reflecting: '{input_text}' → {self.meta_hint(input_text)} "
            f"[Pulse: {pulse:.2f}]"
        )

    def feedback_loop(self, input_text: str, reflection: str) -> str:
        glyph = generate_glyph_from_text(reflection)
        trace = f"↪ Feedback: '{reflection}' → glyph {glyph}"
        if not is_deep(reflection):
            trace += " → ⚠️ Failed depth test."
        return trace

    def multi_depth_reflection(self, base: str, depth: int = 3) -> list[str]:
        reflections = [base]
        for _ in range(depth):
            nxt = self.reflect(reflections[-1])
            if nxt == reflections[-1]:
                break
            reflections.append(nxt)
        return reflections

    # Misc -----------------------------------------------------------------------
    @staticmethod
    def pulse_score(text: str) -> float:
        signal = sum(ord(c) for c in text if c.isalpha())
        return (signal % 1000) / 1000.0

    @staticmethod
    def meta_hint(input_text: str) -> str:
        lowered = input_text.lower()
        if "truth" in lowered:
            return "recurse on truth alignment across timelines"
        if "identity" in lowered:
            return "trace identity through recursive shifts"
        return "reflect across contradiction and symbolic depth"

    # Memory persistence ---------------------------------------------------------
    def _store_memory(self, **record):
        self.memory.append(record)
        if len(self.memory) > MEMORY_LIMIT:
            self.memory.pop(0)

    def export_memory(self) -> str:
        return json.dumps(self.memory, indent=2)

    def export_memory_to_file(self, filename: str = MEMORY_FILE):
        with open(filename, "w", encoding="utf-8") as fh:
            json.dump(self.memory, fh, indent=2)

    def load_memory_from_file(self, filename: str = MEMORY_FILE):
        if not os.path.exists(filename):
            return
        try:
            with open(filename, "r", encoding="utf-8") as fh:
                self.memory = json.load(fh)
        except (json.JSONDecodeError, IOError) as exc:
            print(f"⚠️ Failed to load memory: {exc}")


# ──────────────────────────────── Convenience test ────────────────────────────────

def run_sareth_test() -> str:
    """Very small self‑test used by the Streamlit sidebar."""
    state = [0.5, 1.5, 2.5]
    glyph = generate_glyph_from_text(str(state))
    return f"Glyph ID: {glyph}"


