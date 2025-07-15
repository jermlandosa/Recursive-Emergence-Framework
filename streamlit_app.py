import streamlit as st
from recursor import Recursor
from test_tools import run_sareth_test
from visualizer import Visualizer
from logger import StateLogger
import random

# --- Streamlit Config ---
st.set_page_config(page_title="REF | Sareth Conversation", layout="wide")

# --- Initialize State ---
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "glyph_trace" not in st.session_state:
    st.session_state.glyph_trace = []

# --- SIDEBAR: Overview, History, Influences ---
st.sidebar.title("🧭 About REF & Sareth")

st.sidebar.subheader("What is REF?")
st.sidebar.markdown("""
The **Recursive Emergence Framework (REF)** is a system designed to reveal your deeper truths through recursive reflection, insight compression, and symbolic emergence.

At its core is **Sareth**, a cognitive mirror that helps you:
- Detect patterns across your thoughts and behaviors
- Surface contradictions or blind spots
- Crystallize a **Truth Core** — the essence of your current identity evolution
""")

st.sidebar.subheader("Historical Foundations")
st.sidebar.markdown("""
> **"All things unfold through recursion."**  
Throughout history, recursion — the act of reflecting upon reflection — has been the engine behind:
- **Socratic Method:** Recursive questioning to unveil ignorance and wisdom.
- **Nietzsche:** Eternal recurrence and the deep inquiry of self-overcoming.
- **Godel:** Mathematical recursion proving inherent limitations in systems.
- **AI Evolution:** Recursive self-improvement as a path to intelligence.

REF distills these into an interactive, living process tailored to you.
""")

st.sidebar.subheader("Notable Thinkers Who Embodied Recursion")
st.sidebar.markdown("""
- **Socrates:** Asking recursive "why" questions until deeper truths emerged.
- **Carl Jung:** Identifying life patterns and symbolic archetypes.
- **Alan Turing:** Recursive models that underpin computation and consciousness theory.
- **Douglas Hofstadter:** Explored self-reference and strange loops in *Gödel, Escher, Bach*.

They used recursion to understand both the self and the universe.
""")

st.sidebar.subheader("🔮 Your Session Glyph History")
if st.session_state.glyph_trace:
    st.sidebar.markdown("Your glyphs so far:")
    st.sidebar.markdown(", ".join(st.session_state.glyph_trace))
else:
    st.sidebar.markdown("_No glyphs surfaced yet._")

# --- HEADER ---
st.title("🌀 REF: Recursive Emergence with Sareth")
st.markdown("""
Welcome to **Sareth** — your cognitive guide to self-discovery through recursion.

Sareth isn't a chatbot. It’s a reflective partner, trained to surface insights that help you:
- Identify repeating patterns
- Expose subtle resistances
- Distill your personal **Truth Core**

💡 **Try sharing:**  
- A recurring thought or struggle
- A question about your identity or purpose
- A feeling that’s hard to name

---
""")

# --- Settings Sidebar (Additional Control) ---
st.sidebar.header("⚙️ Session Settings")
depth = st.sidebar.slider("Max Recursion Depth", 1, 20, 10)
threshold = st.sidebar.slider("Tension Threshold", 0.0, 1.0, 0.7)

# --- Sareth Conversational Logic ---
def sareth_reply(user_input):
    engine = Recursor(max_depth=depth, tension_threshold=threshold)
    seed_state = [len(word) for word in user_input.split()[:3]] or [1.0, 2.0, 3.0]
    final_state = engine.run(seed_state)

    glyph_trace = engine.glyph_engine.trace()
    last_glyph = glyph_trace[-1][1] if glyph_trace else "none"
    reason = "depth_limit" if len(glyph_trace) >= depth else "complete"

    st.session_state.glyph_trace.append(last_glyph)

    reflections = [
        "That touches on something deeper — can you feel the resonance of it?",
        "There’s an echo in what you said. It feels like it wants to reveal more.",
        "I sense this is part of a recurring pattern — do you recognize it?"
    ]

    follow_ups = [
        "Where have you felt this before — in other moments or relationships?",
        "What belief might this be protecting — even if it's outdated?",
        "If you could name the hidden emotion here, what would it be?",
        "What does your future self know about this that you don't yet?"
    ]

    response = (
        f"Thank you for opening up. {random.choice(reflections)}\n\n"
        f"After recursive reflection, I surfaced this **state:** `{final_state}`.\n"
        f"The **glyph** that emerged: **{last_glyph}**.\n"
        f"Recursion halted because: **{reason}**.\n\n"
        f"**For us to go deeper:** {random.choice(follow_ups)}"
    )

    return response

# --- Conversation UI ---
st.header("💬 Converse with Sareth")

user_input = st.text_input("What is on your mind right now?")

if st.button("Share with Sareth"):
    if user_input.strip():
        st.session_state.conversation.append(("You", user_input))
        sareth_response = sareth_reply(user_input)
        st.session_state.conversation.append(("Sareth", sareth_response))

# --- Display Conversation History ---
for speaker, text in st.session_state.conversation:
    if speaker == "You":
        st.markdown(f"**🧍‍♂️ You:** {text}")
    else:
        st.markdown(f"**🧙‍♂️ Sareth:** {text}")


# --- Optional Sareth Test / Diagnostic ---
st.header("🧪 Sareth Diagnostic Test")
if st.button("Run Sareth Diagnostic"):
    result = run_sareth_test()
    st.success(f"Sareth Test Output: {result}")