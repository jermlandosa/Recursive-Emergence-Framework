import os
import json
import datetime
import hashlib
import streamlit as st

IS_CI = os.environ.get("CI") == "true"

SHALLOW_SIGNALS = ["it depends", "i'm not sure", "could be", "maybe", "just", "kind of"]
DEPTH_KEYWORDS = ["recursive", "across time", "paradox", "identity", "coherence"]
MEMORY_FILE = "sareth_memory.json"
MEMORY_LIMIT = 1000  # Maximum records in memory

def generate_glyph_from_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]

def run_sareth_engine(prompt: str) -> str:
    return f"🪞 Reflecting on: '{prompt}'"

def is_deep(insight: str) -> bool:
    if not insight:
        return False
    too_short = len(insight.strip()) < 30
    vague = any(phrase in insight.lower() for phrase in SHALLOW_SIGNALS)
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
        recursive_feedback = self.feedback_loop(input_text, reflection)
        record = {
            "timestamp": timestamp,
            "input": input_text,
            "response": reflection,
            "glyph": glyph,
            "feedback": recursive_feedback
        }
        self.memory.append(record)
        if len(self.memory) > MEMORY_LIMIT:
            self.memory.pop(0)
        return recursive_feedback

    def process(self, input_text: str) -> str:
        if self.truth_check(input_text) and self.depth_scan(input_text):
            return self.reflect(input_text)
        return "⟁∅ Insight rejected by False Depth Drift Scan"

    def truth_check(self, input_text: str) -> bool:
        return not any(flag in input_text.lower() for flag in SHALLOW_SIGNALS)

    def depth_scan(self, input_text: str) -> bool:
        return any(word in input_text.lower() for word in DEPTH_KEYWORDS)

    def reflect(self, input_text: str) -> str:
        return f"🪞 Reflecting on: '{input_text}' → consider its implications over time, identity, and contradiction."

    def feedback_loop(self, input_text: str, reflection: str) -> str:
        glyph = generate_glyph_from_text(reflection)
        trace = f"↪ Recursive Reflection: '{reflection}' → encoded as glyph {glyph}"
        if not is_deep(reflection):
            trace += " → ⚠️ Depth validation failed."
        return trace

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

def run_sareth_test():
    state = [0.5, 1.5, 2.5]
    print("[SARETH] Testing state:", state)
    glyph = hash(str(state)) % (10**8)
    return f"Glyph ID: {glyph}"

# Streamlit UI
st.set_page_config(page_title="Sareth Interface", layout="wide")
st.title("🔁 Sareth Interface – Recursive Emergence Framework")

# Sidebar Panel
with st.sidebar:
    st.header("Sareth Tools")
    if st.button("💾 Export Memory"):
        agent = Sareth()
        agent.load_memory_from_file()
        st.download_button("Download JSON", agent.export_memory(), file_name="sareth_memory.json")

# Centered Panel
prompt = st.text_input("Enter your prompt:", placeholder="Type something recursive, paradoxical, etc.")

if st.button("🧠 Submit to Sareth") and prompt:
    agent = Sareth()
    response = agent.observe(prompt)
    st.markdown(f"### Response:\n{response}")

    st.subheader("🧬 Memory Snapshot")
    st.json(agent.memory[-5:] if len(agent.memory) > 5 else agent.memory)
