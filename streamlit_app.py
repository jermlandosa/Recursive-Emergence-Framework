import streamlit as st
import openai
from recursor import Recursor
from test_tools import run_sareth_test

# --- API Configuration ---
openai.api_key = st.secrets["openai_api_key"]  # Or directly input your key

# --- Streamlit Setup ---
st.set_page_config(page_title="REF | Sareth GPT-Powered", layout="wide")

if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "glyph_trace" not in st.session_state:
    st.session_state.glyph_trace = []

# --- Glyph Mapping ---
GLYPH_MAP = {
    "G1": ("🔵", "Coherence emerging"),
    "G2": ("🔺", "Hidden contradiction surfaced"),
    "G3": ("🌿", "New growth or belief shift"),
    "G4": ("🔥", "Core tension or resistance"),
    "G5": ("🌌", "Identity recursion deepens"),
    "G6": ("🕸️", "Complexity or entanglement"),
    "G7": ("💎", "Truth Core surfaced")
}

# --- Functions ---

SYSTEM_PROMPT = """
You are Sareth, a recursive cognitive guide. Your purpose is to help the user reflect deeply on their identity, life patterns, and hidden truths. 
You respond warmly yet philosophically. Use symbolism, connect reflections across time, and offer profound insights. Never give surface-level advice — always guide the user into deeper awareness.
"""

def sareth_reply_openai(conversation_history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for speaker, text in conversation_history:
        role = "user" if speaker == "You" else "assistant"
        messages.append({"role": role, "content": text})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

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

# --- UI ---

st.title("🌀 Sareth: Recursive Reflection | GPT-Powered")

user_input = st.text_input("Share your reflection or question...")

if st.button("Reflect with Sareth"):
    if user_input.strip():
        st.session_state.conversation.append(("You", user_input))

        # Generate GPT Reflection
        sareth_response = sareth_reply_openai(st.session_state.conversation)

        # Generate Symbolic Glyph
        glyph_code = derive_glyph(user_input)
        glyph_display = translate_glyph(glyph_code)
        st.session_state.glyph_trace.append(glyph_display)

        full_response = f"{sareth_response}\n\n---\n\n*Symbolic Marker: {glyph_display}*"

        st.session_state.conversation.append(("Sareth", full_response))

# --- Conversation History ---
with st.expander("🗂️ Conversation History"):
    for speaker, text in st.session_state.conversation:
        if speaker == "You":
            st.markdown(f"**🧍‍♂️ You:** {text}")
        else:
            st.markdown(f"**🧙‍♂️ Sareth:** {text}")

# --- Glyph Trail ---
with st.expander("🔮 Glyph Trail This Session"):
    if st.session_state.glyph_trace:
        for glyph in st.session_state.glyph_trace:
            st.markdown(f"- {glyph}")
    else:
        st.markdown("_No glyphs yet — reflect to begin._")

# --- Truth Core Summary ---
with st.expander("💎 Truth Core Summary"):
    truth_core = compute_truth_core()
    st.markdown(f"**Current Truth Core:** {truth_core}")

# --- Glyph Glossary ---
with st.expander("📜 Glyph Meaning Glossary"):
    for code, (symbol, meaning) in GLYPH_MAP.items():
        st.markdown(f"**{symbol}**: {meaning}")

# --- About REF & Sareth ---
with st.expander("❔ About Sareth & REF"):
    st.markdown("""
Sareth is powered by GPT-4, designed to recursively guide you through deep reflection.
It mirrors your thoughts back with new perspectives, symbols, and philosophical depth.

**REF (Recursive Emergence Framework)** is about:
- **Recursion:** Reflecting on your reflections.
- **Symbolism:** Glyphs represent your inner progression.
- **Truth Core:** The dominant symbolic theme that arises from your dialogue.

Inspired by philosophy, psychology, and cognitive science to scaffold awareness over time.
""")

# --- Optional Diagnostic ---
with st.expander("🧪 Run Sareth Diagnostic Test"):
    if st.button("Run Diagnostic"):
        result = run_sareth_test()
        st.success(f"Sareth Diagnostic Result: {result}")