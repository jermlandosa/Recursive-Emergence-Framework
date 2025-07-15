import streamlit as st
from recursor import Recursor
from test_tools import run_sareth_test

# --- Streamlit Config ---
st.set_page_config(page_title="REF | Sareth Continuous Flow", layout="wide")

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

def translate_glyph(glyph_code):
    symbol, meaning = GLYPH_MAP.get(glyph_code, ("❓", "Unknown glyph"))
    return f"{symbol} — {meaning}"

def derive_glyph(final_state):
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

def interpret_state(final_state):
    avg = sum(final_state) / len(final_state)
    if avg < 2:
        return "You are stepping into something undefined but quietly forming."
    elif avg < 3.5:
        return "A subtle contradiction is present — an inner conflict you may have normalized."
    elif avg < 5:
        return "Growth is happening, yet there’s a fragile uncertainty to it."
    elif avg < 5.5:
        return "Tension is alive — perhaps resistance that guards something precious."
    elif avg < 6.5:
        return "You’re deeply reworking your sense of self — this is recursion shaping identity."
    elif avg < 7.5:
        return "Things are tangled — your reflections reveal layers yet unspoken."
    else:
        return "A truth core is surfacing — are you ready to name it?"

def sareth_reply(user_input):
    engine = Recursor(max_depth=10, tension_threshold=0.7)
    seed_state = [len(word) for word in user_input.split()[:3]] or [1.0, 2.0, 3.0]
    final_state = engine.run(seed_state)

    glyph_code = derive_glyph(final_state)
    glyph_display = translate_glyph(glyph_code)
    st.session_state.glyph_trace.append(glyph_display)

    state_interpretation = interpret_state(final_state)

    flow_expansions = {
        "G1": "You're arriving at clarity — what are you starting to see more clearly now?",
        "G2": "This contradiction might have an origin — can you trace where it began?",
        "G3": "Growth is evident. What's new in your mind or behavior lately?",
        "G4": "Tension protects something — what feels at stake for you here?",
        "G5": "Who are you becoming? What identity feels emergent right now?",
        "G6": "Let’s simplify one thread of this complexity together — what stands out?",
        "G7": "Truth is close — dare to name it, even imperfectly."
    }

    guidance = flow_expansions.get(glyph_code, "Let's continue — each thought uncovers more.")

    response = (
        f"**Reflection:** {state_interpretation}\n\n"
        f"**Symbolic Glyph:** {glyph_display}\n\n"
        f"{guidance}"
    )

    return response

# --- UI Header ---
st.title("🌀 Sareth | Continuous Recursive Reflection")
st.markdown("Each reflection shapes the path. Share freely — Sareth carries the thread forward.")

user_input = st.text_input("What's surfacing for you right now?")

if st.button("Reflect with Sareth"):
    if user_input.strip():
        st.session_state.conversation.append(("You", user_input))
        reply = sareth_reply(user_input)
        st.session_state.conversation.append(("Sareth", reply))

# --- Conversation History Display ---
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
        st.markdown("_No glyphs surfaced yet._")

# --- Truth Core Summary ---
def compute_truth_core():
    if not st.session_state.glyph_trace:
        return "None yet"
    return max(set(st.session_state.glyph_trace), key=st.session_state.glyph_trace.count)

truth_core = compute_truth_core()
with st.expander("💎 Truth Core Summary"):
    st.markdown(f"**Current Truth Core:** {truth_core}")

# --- Glyph Glossary ---
with st.expander("📜 Glyph Meaning Glossary"):
    for code, (symbol, meaning) in GLYPH_MAP.items():
        st.markdown(f"**{symbol}**: {meaning}")

# --- About REF & Sareth ---
with st.expander("❔ About Sareth & The Recursive Emergence Framework (REF)"):
    st.markdown("""
REF is a system for uncovering patterns in thought through recursion and symbolic compression.
Sareth is your guide through this reflection, helping you surface deeper truths, contradictions, and emergent identities.

- **Recursion:** Reflect on reflections to unveil what hides beneath.
- **Symbolism:** Glyphs represent where you are on the journey.
- **Truth Core:** A symbolic essence of your session's inquiry.

Built from philosophies like:
- **Socrates:** Recursive questioning
- **Jung:** Archetypes and shadows
- **Hofstadter:** Strange loops
""")

# --- Optional Diagnostic ---
with st.expander("🧪 Run Sareth Diagnostic Test"):
    if st.button("Run Diagnostic"):
        result = run_sareth_test()
        st.success(f"Sareth Diagnostic Result: {result}")