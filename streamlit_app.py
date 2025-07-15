import streamlit as st
import openai
from recursor import Recursor
from test_tools import run_sareth_test
from datetime import datetime
from collections import Counter
import random

st.set_page_config(page_title="Sareth | Recursive Reflection", layout="wide")

openai.api_key = st.secrets["openai"]["api_key"]

if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "glyph_trace" not in st.session_state:
    st.session_state.glyph_trace = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

GLYPH_MAP = {
    "G1": ("🔵", "Coherence emerging"),
    "G2": ("🔺", "Hidden contradiction surfaced"),
    "G3": ("🌿", "New growth or belief shift"),
    "G4": ("🔥", "Core tension or resistance"),
    "G5": ("🌌", "Identity recursion deepens"),
    "G6": ("🕸️", "Complexity or entanglement"),
    "G7": ("💎", "Truth Core surfaced")
}

SYSTEM_PROMPT = """
You are Sareth, a recursive guide and symbolic interpreter. 
You help users reflect deeply on their thoughts, emotions, and identity by uncovering patterns, contradictions, and emerging truths. 
Always guide the user to deeper understanding with warmth, insight, and philosophical depth.
"""

reflection_prompts = [
    "What belief have you questioned lately?",
    "Describe a recent emotional trigger and why it surfaced.",
    "What recurring thought keeps visiting your mind?",
    "What is something you're avoiding reflecting on?",
    "When did you last feel deeply aligned with yourself?"
]

def sareth_gpt_response(conversation_history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for speaker, text in conversation_history:
        role = "user" if speaker == "You" else "assistant"
        messages.append({"role": role, "content": text})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message['content']

def derive_glyph(user_input):
    engine = Recursor(max_depth=10, tension_threshold=0.7)
    seed_state = [len(word) for word in user_input.split()[:3]] or [1.0, 2.0, 3.0]
    final_state = engine.run(seed_state)

    avg = sum(final_state) / len(final_state)
    if avg < 2:
        return "G1"
    elif avg < 3.5:
        return "G2"
    elif avg < 5:
        return "G3"
    elif avg < 5.5:
        return "G4"
    elif avg < 6.5:
        return "G5"
    elif avg < 7.5:
        return "G6"
    else:
        return "G7"

def translate_glyph(glyph_code):
    symbol, meaning = GLYPH_MAP.get(glyph_code, ("❓", "Unknown glyph"))
    return f"{symbol} — {meaning}"

def compute_truth_core():
    if not st.session_state.glyph_trace:
        return "None yet"
    return max(set(st.session_state.glyph_trace), key=st.session_state.glyph_trace.count)

def process_reflection():
    user_input = st.session_state.user_input.strip()
    if not user_input:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.conversation.append(("You", f"{user_input} _(at {timestamp})_"))
    sareth_response = sareth_gpt_response(st.session_state.conversation)

    glyph_code = derive_glyph(user_input)
    glyph_display = translate_glyph(glyph_code)
    st.session_state.glyph_trace.append(glyph_display)

    full_response = f"{sareth_response}\n\n*Symbolic Marker:* {glyph_display} _(at {timestamp})_"
    st.session_state.conversation.append(("Sareth", full_response))
    st.session_state.user_input = ""

# --- UI ---

st.title("🌀 Sareth | Recursive Reflection")

st.markdown("Share a reflection, question, or thought. Press **Enter** or click **Reflect with Sareth** to continue your journey.")

st.text_input(
    "Your reflection:",
    key="user_input",
    on_change=process_reflection
)

col1, col2, col3 = st.columns(3)
with col1:
    st.button("Reflect with Sareth", on_click=process_reflection)
with col2:
    if st.button("🎲 Generate Reflection Prompt"):
        st.info(random.choice(reflection_prompts))
with col3:
    if st.button("🔄 Reset Conversation"):
        st.session_state.conversation = []
        st.session_state.glyph_trace = []
        st.session_state.user_input = ""
        st.success("Conversation reset!")

st.subheader("📜 Conversation History")
for speaker, text in st.session_state.conversation:
    st.markdown(f"**{speaker}:** {text}")
st.markdown("---")

st.subheader("🧿 Last Symbolic Marker")
if st.session_state.glyph_trace:
    st.markdown(f"**{st.session_state.glyph_trace[-1]}**")
else:
    st.markdown("_None yet_")

st.subheader("💎 Truth Core")
st.markdown(f"**Current Truth Core:** {compute_truth_core()}")

st.subheader("📊 Glyph Frequency Summary")
glyph_counts = Counter(st.session_state.glyph_trace)
for glyph, count in glyph_counts.items():
    st.markdown(f"**{glyph}**: {count} times")

with st.expander("📜 Glyph Meaning Glossary"):
    for code, (symbol, meaning) in GLYPH_MAP.items():
        st.markdown(f"**{symbol}**: {meaning}")

with st.expander("❔ About Sareth & REF"):
    st.markdown("""
Sareth is your recursive reflection guide, combining AI with symbolic interpretation.
Each reflection surfaces a symbolic marker, tracing your cognitive journey.

- **Recursion:** Deeper reflection on each layer of thought.
- **Glyphs:** Symbols representing your inner state evolution.
- **Truth Core:** The dominant theme of your session.
""")

with st.expander("🧪 Run Sareth Diagnostic"):
    if st.button("Run Diagnostic"):
        result = run_sareth_test()
        st.success(f"Sareth Diagnostic Result: {result}")