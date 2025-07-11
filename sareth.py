import os
import json
import datetime
import hashlib

IS_CI = os.environ.get("CI") == "true"

def generate_glyph_from_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]

def run_sareth_engine(prompt: str) -> str:
    return f"🪞 Reflecting on: '{prompt}'"

def is_deep(insight: str) -> bool:
    if not insight:
        return False
    shallow_signals = ["it depends", "i'm not sure", "could be", "maybe", "just", "kind of"]
    too_short = len(insight.strip()) < 30
    vague = any(phrase in insight.lower() for phrase in shallow_signals)
    return not (too_short or vague)

class Sareth:
    def __init__(self, name: str = "Sareth", version: str = "REF_1.0"):
        self.name = name
        self.version = version
        self.memory = []

    def observe(self, input_text: str) -> str:
        timestamp = datetime.datetime.now().isoformat()
        glyph = generate_glyph_from_text(input_text)
        reflection = self.process(input_text)
        record = {
            "timestamp": timestamp,
            "input": input_text,
            "response": reflection,
            "glyph": glyph
        }
        self.memory.append(record)
        return reflection

    def process(self, input_text: str) -> str:
        if self.truth_check(input_text) and self.depth_scan(input_text):
            return self.reflect(input_text)
        return "⟁∅ Insight rejected by False Depth Drift Scan"

    def truth_check(self, input_text: str) -> bool:
        shallow_flags = ["maybe", "could be", "possibly", "i think"]
        return not any(flag in input_text.lower() for flag in shallow_flags)

    def depth_scan(self, input_text: str) -> bool:
        keywords = ["recursive", "across time", "paradox", "identity", "coherence"]
        return any(word in input_text.lower() for word in keywords)

    def reflect(self, input_text: str) -> str:
        return f"🪞 Reflecting on: '{input_text}' → consider its implications over time, identity, and contradiction."

    def export_memory(self) -> str:
        return json.dumps(self.memory, indent=2)

    def export_memory_to_file(self, filename="sareth_memory.json"):
        with open(filename, "w") as f:
            json.dump(self.memory, f, indent=2)

    def load_memory_from_file(self, filename="sareth_memory.json"):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                self.memory = json.load(f)

if __name__ == "__main__":
    agent = Sareth()
    print("🔁 Sareth Agent Initialized. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("📦 Memory Snapshot:")
            print(agent.export_memory())
            break
        response = agent.observe(user_input)
        print("Sareth:", response)

def run_sareth_test():
    state = [0.5, 1.5, 2.5]
    print("[SARETH] Testing state:", state)
    glyph = hash(str(state)) % (10**8)
    return f"Glyph ID: {glyph}"
