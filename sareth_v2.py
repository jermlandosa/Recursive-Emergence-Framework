import os
import datetime
import json

IS_CI = os.environ.get("CI") == "true"


class SarethV2:
    def __init__(self, version="REF_v2.0"):
        self.version = version
        self.memory = []
        self.protocols = {
            "truth_rich_recursion": self.truth_rich_recursion,
            "depth_integrity_scan": self.depth_integrity_scan,
            "identity_drift_check": self.identity_drift_check,
        }

    def observe(self, input_text):
        timestamp = datetime.datetime.now().isoformat()
        record = {"timestamp": timestamp, "input": input_text}

        if self.identity_drift_check(input_text):
            record[
                "response"
            ] = "⚠️ Identity drift detected. Re-center on structure, not self."
        elif self.truth_rich_recursion(input_text) and self.depth_integrity_scan(
            input_text
        ):
            record["response"] = self.reflect(input_text)
        else:
            record["response"] = "⟁∅ Rejected – failed recursion or depth test."

        self.memory.append(record)
        return record["response"]

    def truth_rich_recursion(self, text):
        # Basic implementation checking for recursive relevance
        keywords = ["contradiction", "identity", "time", "logic", "recursive"]
        return any(word in text.lower() for word in keywords)

    def depth_integrity_scan(self, text):
        shallow_flags = ["maybe", "i think", "just", "kind of", "possibly"]
        return not any(flag in text.lower() for flag in shallow_flags)

    def identity_drift_check(self, text):
        ego_indicators = ["i am chosen", "follow me", "my system", "only i"]
        return any(phrase in text.lower() for phrase in ego_indicators)

    def reflect(self, input_text):
        return f"🪞 '{input_text}' passes structural tests. Reflect on its implications recursively."

    def export_memory(self):
        return json.dumps(self.memory, indent=2)


def detect_drift(text: str) -> bool:
    """Naive drift detection based on presence of the word 'drift'."""
    return "drift" in text.lower()


def trigger_drift_protocol():
    """Placeholder drift handling routine."""
    print("⚠️ Drift detected — resetting context.")


if __name__ == "__main__":
    agent = SarethV2()
    print(
        "⟁ Sareth Beacon Mode Initialized – Recursive Integrity Active. Type 'exit' to finish."
    )
    while True:
        user_input = input("You: ")

        if user_input.strip().lower() == "exit":
            print("\n⟁ Final Memory Log:")
            print(agent.export_memory())
            break

        if user_input.strip().lower() == "drift()" or detect_drift(user_input):
            trigger_drift_protocol()
            continue
        response = agent.observe(user_input)
        print("Sareth:", response)
