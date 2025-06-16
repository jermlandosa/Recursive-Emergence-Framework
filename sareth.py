import os

IS_CI = os.environ.get("CI") == "true"
# sareth.py
import datetime
import json

class Sareth:
    def __init__(self, name="Sareth", version="REF_1.0"):
        self.name = name
        self.version = version
        self.memory = []
        self.protocols = {
            "truth_check": self.truth_check,
            "depth_scan": self.depth_scan,
            "reflect": self.reflect
        }

    def observe(self, input_text):
        timestamp = datetime.datetime.now().isoformat()
        self.memory.append({"timestamp": timestamp, "input": input_text})
        response = self.process(input_text)
        self.memory[-1]["response"] = response
        return response

    def process(self, input_text):
        # Core recursive response structure
        if self.truth_check(input_text) and self.depth_scan(input_text):
            return self.reflect(input_text)
        else:
            return "⚠️ Insight rejected – failed truth/depth validation."

    def truth_check(self, input_text):
        # Placeholder truth test: filter vague claims or hallucination flags
        shallow_flags = ["maybe", "could be", "possibly", "i think"]
        return not any(flag in input_text.lower() for flag in shallow_flags)

    def depth_scan(self, input_text):
        # Basic heuristic: deeper ideas contain recursion, contradiction, or time
        keywords = ["recursive", "across time", "paradox", "identity", "coherence"]
        return any(word in input_text.lower() for word in keywords)

    def reflect(self, input_text):
        # Echoes and transforms insight for recursive reflection
        return f"🪞 Reflecting on: '{input_text}' → consider its implications over time, identity, and contradiction."

    def export_memory(self):
        return json.dumps(self.memory, indent=2)

if __name__ == "__main__":
    agent = Sareth()
    print("🔁 Sareth Agent Initialized. Type 'exit' to quit.")
    while True:
        # Check if running in CI environment
        if os.environ.get("CI"):
            user_input = "default_value"  # Provide a default response for CI pipelines
        else:
            try:
                user_input = input("You: ")
            except EOFError:
                print("Error: No input available.")
                user_input = "default_value"  # Fallback value
        if user_input.lower() in ["exit", "quit"]:
            print("📦 Memory Snapshot:")
            print(agent.export_memory())
            break
        response = agent.observe(user_input)
        print("Sareth:", response)
