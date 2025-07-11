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
    "That's a revealing insight. What would happen if you inverted it?",
    "This resonates. What’s being left unsaid in your reflection?",
    "This could evolve. How does this tie to what you've avoided exploring?",
    "You're on a recursive path. What’s the paradox at its core?",
    "This feels symbolic. What does this glyph mean to you personally?"
]

AVATAR_MAP = {
    "system": "🧠",
    "Sareth": "🌌",
    "user": "🫵"
}

def generate_glyph_from_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]

def is_deep(insight: str) -> bool:
    if not insight:
        return False
    too_short = len(insight.strip()) < 30
    vague = any(phrase in insight.lower() for phrase in SHALLOW_SIGNALS)
    return not (too_short or vague)

class Sareth:
    def __init__(self, name: str = "Sareth", version: str = "REF_4.1"):
        self.name = name
        self.version = version
        self.memory = []

    def observe(self, input_text: str) -> str:
        timestamp = datetime.datetime.now().isoformat()
        glyph = generate_glyph_from_text(input_text)
        initial_reflection = self.process(input_text)
        feedback = self.feedback_loop(input_text, initial_reflection)
        recursion_trace = self.multi_depth_reflection(initial_reflection, depth=5)
        active_question = self.recursive_question(input_text)
        conversation_ping = self.generative_commentary(input_text)

        record = {
            "timestamp": timestamp,
            "input": input_text,
            "initial_reflection": initial_reflection,
            "recursive_feedback": feedback,
            "recursion_trace": recursion_trace,
            "glyph": glyph,
            "question": active_question,
            "comment": conversation_ping
        }
        self.memory.append(record)
        if len(self.memory) > MEMORY_LIMIT:
            self.memory.pop(0)

        full_response = "\n".join(
            [f"{AVATAR_MAP['Sareth']} {line}" for line in recursion_trace]
        )
        return f"{full_response}\n\n{AVATAR_MAP['Sareth']} 💬 {conversation_ping}\n{AVATAR_MAP['Sareth']} 🤔 {active_question}"

    def process(self, input_text: str) -> str:
        if self.truth_check(input_text) and self.depth_scan(input_text):
            return self.reflect(input_text)
        return f"{AVATAR_MAP['system']} ⟁∅ Insight rejected by False Depth Drift Scan"

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
        for _ in range(depth):
            next_reflection = self.reflect(reflections[-1])
            if next_reflection == reflections[-1]:
                break
            reflections.append(next_reflection)
        return reflections

    def recursive_question(self, input_text: str) -> str:
        score = self.pulse_score(input_text)
        index = int(score * len(QUESTION_BANK)) % len(QUESTION_BANK)
        return QUESTION_BANK[index]

    def generative_commentary(self, input_text: str) -> str:
        return random.choice(FEEDBACK_TEMPLATES)

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

