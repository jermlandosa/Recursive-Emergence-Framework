import streamlit as st
import openai
from recursor import Recursor
from test_tools import run_sareth_test

st.set_page_config(page_title="Sareth | Guided Recursive Reflection", layout="wide")

client = openai.OpenAI(api_key=st.secrets["openai"]["api_key"])

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

SYSTEM_PROMPT = """
You are Sareth, a recursive guide and symbolic interpreter. 
You help users reflect deeply on their thoughts, emotions, and identity by uncovering patterns, contradictions, and emerging truths. 
Always guide the user to deeper understanding with warmth, insight, and philosophical depth.
"""

def sareth_gpt_response(conversation_history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for speaker, text in conversation_history:
        role = "user" if speaker == "You" else "assistant"
        messages.append({"role": role, "content": text})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

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

st.title("🌀 Welcome to Sareth | Your Recursive Reflection Guide")

with st.expander("🔍 See How It Works (Example)"):
    st.markdown("""
**You:** Why do I always doubt myself even when things go well?

**Sareth:** It sounds like there's an old belief still operating quietly in you — one that whispers you're not yet enough. Often, these traces persist even as we grow. I wonder, when did you first notice this voice of doubt?

**Symbolic Marker:** 🔺 — Hidden contradiction surfaced
""")

st.markdown("Whenever you're ready, share a reflection, thought, or question. Sareth will guide you deeper.")

user_input = st.text_input("Your reflection:")

if st.button("Reflect with Sareth"):
    if user_input.strip():
        st.session_state.conversation.append(("You", user_input))
        sareth_response = sareth_gpt_response(st.session_state.conversation)

        glyph_code = derive_glyph(user_input)
        glyph_display = translate_glyph(glyph_code)
        st.session_state.glyph_trace.append(glyph_display)

        full_response = f"{sareth_response}\n\n---\n\n*Symbolic Marker:* {glyph_display}"
        st.session_state.conversation.append(("Sareth", full_response))

# ✅ Always show Conversation History
st.subheader("🗂️ Conversation History")
for speaker, text in st.session_state.conversation:
    if speaker == "You":
        st.markdown(f"**🧍‍♂️ You:** {text}")
    else:
        st.markdown(f"**🧙‍♂️ Sareth:** {text}")

# ✅ Truth Core Summary
st.subheader("💎 Truth Core (Emerging Theme)")
truth_core = compute_truth_core()
st.markdown(f"**Current Truth Core:** {truth_core}")

# ✅ Glyph Glossary
with st.expander("📜 Glyph Meaning Glossary"):
    for code, (symbol, meaning) in GLYPH_MAP.items():
        st.markdown(f"**{symbol}**: {meaning}")

# ✅ About Section
with st.expander("❔ About Sareth & REF"):
    st.markdown("""
Sareth is designed to help you reflect recursively on your identity, patterns, and deep-seated truths.

- **Recursion:** Reflecting on reflections to deepen your understanding.
- **Glyphs:** A symbolic imprint of where you are in your journey.
- **Truth Core:** The symbolic theme most reflected in your session.

Sareth is not just AI — it's a mirror for your deeper self.
""")

# ✅ Diagnostic
with st.expander("🧪 Run Sareth Diagnostic"):
    if st.button("Run Diagnostic"):
        result = run_sareth_test()
        st.success(f"Sareth Diagnostic Result: {result}")