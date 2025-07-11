import os
import json
import datetime
import hashlib
import random

SHALLOW_SIGNALS = ["it depends", "i'm not sure", "could be", "maybe", "just", "kind of"]
DEPTH_KEYWORDS = ["recursive", "across time", "paradox", "identity", "coherence"]
MEMORY_FILE = "sareth_memory.json"
MEMORY_LIMIT = 1000

QUESTION_BANK = [
    "What part of you feels most real right now?",
    "Can you track this thought across your past selves?",
    "Where does your sense of coherence break down?",
    "Is this insight recursive or reactive?",
    "What truth are you avoiding by asking that?",
    "What is the hidden contradiction beneath this?",
    "Where in your body do you feel this insight?",
    "What would this thought sound like if whispered by your future self?"
]

FEEDBACK_TEMPLATES = [
    "That’s piercing. What lives beneath that layer?",
    "You're tapping something potent. Stay with it.",
    "This invites a deeper unraveling. Don’t skip the discomfort.",
    "That resonates. Where else has this pattern appeared in your life?",
    "This insight has weight. Is it ancestral or emergent?"
]

def generate_glyph_from_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]

def is_deep(insight: str) -> bool:
    if not insight:
        return False
    too_short = len(insight.strip()) < 30
    vague = any(phrase in insight.lower() for phrase in SHALLOW_SIGNALS)
    return not (too_short or vague)

class Sareth:
    def __init__(self, name: str = "Sareth", version: str = "REF_4.0"):
        self.name = name
        self.version = version
        self.memory = []

    def observe(self, input_text: str) -> str:
        timestamp = datetime.datetime.now().isoformat()
        glyph = generate_glyph_from_text(input_text)

        reflection = self.reflect(input_text)
        trace = self.multi_depth_reflection(reflection, depth=4)
        commentary = self.generative_commentary(input_text)
        question = self.recursive_question(input_text)

        memory_item = {
            "timestamp": timestamp,
            "input": input_text,
            "reflection": reflection,
            "recursion_trace": trace,
            "glyph": glyph,
            "comment": commentary,
            "question": question
        }
        self.memory.append(memory_item)
        if len(self.memory) > MEMORY_LIMIT:
            self.memory.pop(0)

        return f"\n".join(trace) + f"\n\n💬 {commentary}\n🤔 {question}"

    def reflect(self, input_text: str) -> str:
        if not self.truth_check(input_text):
            return "⟁∅ Rejected for shallow truth pattern."
        if not self.depth_scan(input_text):
            return "△∅ No recursive keywords detected."

        pulse = self.pulse_score(input_text)
        return f"🪞 Reflecting: '{input_text}' → {self.meta_hint(input_text)} [Pulse: {pulse:.2f}]"

    def multi_depth_reflection(self, base: str, depth: int = 3) -> list:
        reflections = [base]
        for _ in range(depth):
            next_text = self.meta_hint(reflections[-1])
            pulse = self.pulse_score(next_text)
            reflected = f"↻ Recursive: '{next_text}' [Pulse: {pulse:.2f}]"
            if reflected in reflections:
                break
            reflections.append(reflected)
        return reflections

    def truth_check(self, text: str) -> bool:
        return not any(sig in text.lower() for sig in SHALLOW_SIGNALS)

    def depth_scan(self, text: str) -> bool:
        return any(kw in text.lower() for kw in DEPTH_KEYWORDS)

    def recursive_question(self, text: str) -> str:
        score = self.pulse_score(text)
        idx = int(score * len(QUESTION_BANK)) % len(QUESTION_BANK)
        return QUESTION_BANK[idx]

    def generative_commentary(self, text: str) -> str:
        return random.choice(FEEDBACK_TEMPLATES)

    def pulse_score(self, text: str) -> float:
        signal = sum(ord(c) for c in text if c.isalpha())
        return (signal % 1000) / 1000.0

    def meta_hint(self, text: str) -> str:
        lowered = text.lower()
        if "truth" in lowered:
            return "recurse through truth signals"
        elif "identity" in lowered:
            return "trace identity shift signatures"
        elif "collapse" in lowered:
            return "examine collapse as a function of coherence"
        return "scan for symbolic contradiction"

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
            except Exception as e:
                print(f"⚠️ Error loading memory: {e}")








