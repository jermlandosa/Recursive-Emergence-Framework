import streamlit as st
from recursor import Recursor
from test_tools import run_sareth_test
import random

st.set_page_config(page_title="Sareth | Organic Reflection Mode", layout="wide")

if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "glyph_trace" not in st.session_state:
    st.session_state.glyph_trace = []

GLYPH_MAP = {
    "G1": ("🔵", "Coherence emerging"),
    "G2": ("🔺", "Hidden contradiction surfaced"),
    "G3": ("🌿", "New growth or belief shift"),
    "G4": ("🔥", "Core tension or resistance"),
    "G5": ("🌌", "Identity recursion deepens"),
    "G6": ("🕸️", "Complexity or entanglement"),
    "G7": ("💎", "Truth Core surfaced")
}

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

def offline_sareth_response(user_input):
    # Keywords for more guided reflections
    keywords = {
        "identity": "It sounds like you're redefining yourself in real-time.",
        "truth": "Truth seems to be important to you — but is it comfortable?",
        "fear": "Fear often guards our most precious insights — what might that be for you?",
        "pattern": "Patterns have their own gravity. Do you feel pulled by one?",
        "change": "Change reshapes us, sometimes gently, sometimes harshly."
    }

    reflections = [
        "That's an intriguing place to start.",
        "What you've shared feels like it carries more than just the surface meaning.",
        "There's something alive in that — do you feel it too?"
    ]

    found_keyword = next((kw for kw in keywords if kw in user_input.lower()), None)
    follow_up = keywords.get(found_keyword, random.choice([
        "If this feeling had a shape, what would it be?",
        "Where have you felt this before, even faintly?",
        "If this was a dream symbol, what would it represent?",
        "What feels unsaid here?"
    ]))

    return f"{random.choice(reflections)}\n\n> {follow_up}"

def compute_truth_core():
    if not st.session_state.glyph_trace:
        return "None yet"
    return max(set(st.session_state.glyph_trace), key=st.session_state.glyph_trace.count)


st.title("🌀 Sareth | Simulated AI Reflection (Offline)")
st.markdown("Even without AI, Sareth listens, reflects, and guides you deeper.")

user_input = st.text_input("What reflection or thought is surfacing for you?")

if st.button("Reflect with Sareth"):
    if user_input.strip():
        st.session_state.conversation.append(("You", user_input))
        glyph_code = derive_glyph(user_input)
        glyph_display = translate_glyph(glyph_code)
        st.session_state.glyph_trace.append(glyph_display)

        reflection = offline_sareth_response(user_input)
        full_response = f"{reflection}\n\n*Symbolic Marker: {glyph_display}*"
        st.session_state.conversation.append(("Sareth", full_response))

with st.expander("📜 Conversation History"):
    for speaker, text in st.session_state.conversation:
        st.markdown(f"**{speaker}:** {text}")

with st.expander("🔮 Glyph Trail This Session"):
    if st.session_state.glyph_trace:
        for glyph in st.session_state.glyph_trace:
            st.markdown(f"- {glyph}")
    else:
        st.markdown("_No glyphs yet._")

with st.expander("💎 Truth Core Summary"):
    truth_core = compute_truth_core()
    st.markdown(f"**Current Truth Core:** {truth_core}")

with st.expander("📜 Glyph Meaning Glossary"):
    for code, (symbol, meaning) in GLYPH_MAP.items():
        st.markdown(f"**{symbol}**: {meaning}")

with st.expander("🧪 Run Sareth Diagnostic"):
    if st.button("Run Diagnostic"):
        result = run_sareth_test()
        st.success(f"Sareth Diagnostic Result: {result}")