import os
import json
import datetime
import hashlib

SHALLOW_SIGNALS = ["it depends", "i'm not sure", "could be", "maybe", "just", "kind of"]
DEPTH_KEYWORDS = ["recursive", "across time", "paradox", "identity", "coherence"]
MEMORY_FILE = "sareth_memory.json"
MEMORY_LIMIT = 1000


def generate_glyph_from_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def is_deep(insight: str) -> bool:
    if not insight:
        return False
    too_short = len(insight.strip()) < 30
    vague = any(phrase in insight.lower() for phrase in SHALLOW_SIGNALS)
    return not (too_short or vague)


class Sareth:
    def __init__(self, name: str = "Sareth", version: str = "REF_3.1"):
        self.name = name
        self.version = version
        self.memory = []

    def observe(self, input_text: str) -> str:
        timestamp = datetime.datetime.now().isoformat()
        glyph = generate_glyph_from_text(input_text)
        initial_reflection = self.process(input_text)
        feedback = self.feedback_loop(input_text, initial_reflection)
        recursion_trace = self.multi_depth_reflection(initial_reflection, depth=5)

        record = {
            "timestamp": timestamp,
            "input": input_text,
            "initial_reflection": initial_reflection,
            "recursive_feedback": feedback,
            "recursion_trace": recursion_trace,
            "glyph": glyph
        }
        self.memory.append(record)
        if len(self.memory) > MEMORY_LIMIT:
            self.memory.pop(0)

        return "\n".join(recursion_trace)

    def process(self, input_text: str) -> str:
        if self.truth_check(input_text) and self.depth_scan(input_text):
            return self.reflect(input_text)
        return "⟁∅ Insight rejected by False Depth Drift Scan"

    def truth_check(self, input_text: str) -> bool:
        return not any(flag in input_text.lower() for flag in SHALLOW_SIGNALS)

    def depth_scan(self, input_text: str) -> bool:
        return any(word in input_text.lower() for word in DEPTH_KEYWORDS)

    def reflect(self, input_text: str) -> str:
        pulse = self.pulse_score(input_text)
        return f"🪞 Reflecting: '{input_text}' → {self.meta_hint(input_text)} [Pulse: {pulse:.2f}]"

    def feedback_loop(self, input_text: str, reflection: str) -> str:
        glyph = generate_glyph_from_text(reflection)
        trace = f"↪ Feedback: '{reflection}' → glyph {glyph}"
        if not is_deep(reflection):
            trace += " → ⚠️ Failed depth test."
        return trace

    def multi_depth_reflection(self, base: str, depth: int = 3) -> list:
        reflections = [base]
        for i in range(depth):
            next_reflection = self.reflect(reflections[-1])
            if next_reflection == reflections[-1]:
                break
            reflections.append(next_reflection)
        return reflections

    def pulse_score(self, text: str) -> float:
        signal = sum(ord(c) for c in text if c.isalpha())
        return (signal % 1000) / 1000.0

    def meta_hint(self, input_text: str) -> str:
        if "truth" in input_text.lower():
            return "recurse on truth alignment across timelines"
        elif "identity" in input_text.lower():
            return "trace identity through recursive shifts"
        else:
            return "reflect across contradiction and symbolic depth"

    def export_memory(self) -> str:
        return json.dumps(self.memory, indent=2)

    def export_memory_to_file(self, filename=MEMORY_FILE):
        with open(filename, "w") as f:
            json.dump(self.memory, f, indent=2)

    def load_memory_from_file(self, filename=MEMORY_FILE):
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    self.memory = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Failed to load memory: {e}")
