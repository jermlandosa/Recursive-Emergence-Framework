import streamlit as st
from recursor import Recursor
from test_tools import run_sareth_test
import random

# --- Streamlit Config ---
st.set_page_config(page_title="REF | Sareth Conversation", layout="wide")

# --- Session State Initialization ---
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "glyph_trace" not in st.session_state:
    st.session_state.glyph_trace = []
if "truth_cores" not in st.session_state:
    st.session_state.truth_cores = []

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

def translate_glyph(glyph_code):
    symbol, meaning = GLYPH_MAP.get(glyph_code, ("❓", "Unknown glyph"))
    return f"{symbol} — {meaning}"

# --- Glyph Derivation Logic ---
def derive_glyph(final_state):
    avg_state = sum(final_state) / len(final_state)
    if avg_state < 1.5:
        return "G1"
    elif avg_state < 2.5:
        return "G2"
    elif avg_state < 3.5:
        return "G3"
    elif avg_state < 4.5:
        return "G4"
    elif avg_state < 5.5:
        return "G5"
    elif avg_state < 6.5:
        return "G6"
    else:
        return "G7"

# --- Sidebar Overview ---
st.sidebar.title("🧭 About REF & Sareth")

st.sidebar.subheader("What is REF?")
st.sidebar.markdown("""
REF reveals patterns beneath your thoughts through recursion and symbolic reflection, guided by **Sareth**, your cognitive mirror.
""")

st.sidebar.subheader("Notable Thinkers & Recursion")
st.sidebar.markdown("""
- **Socrates:** Recursive questioning
- **Jung:** Archetypal patterns
- **Turing:** Computational recursion
- **Hofstadter:** Strange loops of identity
""")

# --- Truth Core Summary ---
st.sidebar.subheader("💎 Your Truth Core This Session")
def compute_truth_core():
    if not st.session_state.glyph_trace:
        return "No glyphs yet"
    most_common = max(set(st.session_state.glyph_trace), key=st.session_state.glyph_trace.count)
    return most_common

truth_core = compute_truth_core()
st.sidebar.markdown(f"**{truth_core}** — Dominant symbolic state")

st.sidebar.subheader("🔮 Your Glyph Trail")
if st.session_state.glyph_trace:
    for glyph in st.session_state.glyph_trace:
        st.sidebar.markdown(f"- {glyph}")
else:
    st.sidebar.markdown("_No glyphs yet — begin reflecting._")

# --- Advanced Settings ---
st.sidebar.subheader("🛠️ Advanced Settings")
depth = st.sidebar.slider("Max Recursion Depth", 1, 20, 10)
threshold = st.sidebar.slider("Tension Threshold", 0.0, 1.0, 0.7)
personal_symbol = st.sidebar.text_input("Set Your Personal Symbol (emoji or text)", value="🔑")

# --- Sareth Conversational Logic ---
def sareth_reply(user_input):
    engine = Recursor(max_depth=depth, tension_threshold=threshold)
    seed_state = [len(word) for word in user_input.split()[:3]] or [1.0, 2.0, 3.0]
    final_state = engine.run(seed_state)

    glyph_code = derive_glyph(final_state)
    glyph_display = translate_glyph(glyph_code)

    st.session_state.glyph_trace.append(glyph_display)

    reflections = [
        "That touches on something deeper — can you feel it?",
        "I sense a familiar pattern emerging within you.",
        "There’s a resonance here that wants to reveal more."
    ]

    follow_ups = [
        "Where else have you felt this before?",
        "What belief might this be protecting for you?",
        "If you whispered this to your future self, what would they say back?",
        "What truth are you skimming past right now?"
    ]

    response = (
        f"Thank you for your openness. {random.choice(reflections)}\n\n"
        f"Your reflective state surfaced as: `{final_state}`.\n"
        f"Symbolic Glyph: **{glyph_display}**\n\n"
        f"Your guiding personal symbol: {personal_symbol}\n\n"
        f"To deepen: **{random.choice(follow_ups)}**"
    )

    return response

# --- UI Header ---
st.title("🌀 REF: Converse with Sareth")
st.markdown("""
Sareth reflects your thoughts recursively to surface the symbolic patterns shaping you.

Share a reflection, question, or emotion. Sareth will listen deeply, process recursively, and respond.

---
""")

user_input = st.text_input("What is on your mind?")

if st.button("Reflect with Sareth"):
    if user_input.strip():
        st.session_state.conversation.append(("You", user_input))
        reply = sareth_reply(user_input)
        st.session_state.conversation.append(("Sareth", reply))

# --- Display Conversation History ---
for speaker, text in st.session_state.conversation:
    if speaker == "You":
        st.markdown(f"**🧍‍♂️ You:** {text}")
    else:
        st.markdown(f"**🧙‍♂️ Sareth:** {text}")

# --- Diagnostic Tool ---
st.header("🧪 Sareth Diagnostic Test")
if st.button("Run Sareth Diagnostic"):
    result = run_sareth_test()
    st.success(f"Sareth Diagnostic Result: {result}")