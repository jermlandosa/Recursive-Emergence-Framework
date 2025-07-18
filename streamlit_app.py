import streamlit as st
import openai
from recursor import Recursor
from test_tools import run_sareth_test
from main import run_recursive_engine
from datetime import datetime
from collections import Counter
import random
import re

st.set_page_config(page_title="Sareth | Recursive Reflection", layout="wide")

client = openai.Client(api_key=st.secrets["openai"]["api_key"])

# Initialize session state
for key in ["conversation", "glyph_trace", "conversation_history", "user_input", "search_query"]:
    if key not in st.session_state:
        st.session_state[key] = [] if 'trace' in key or 'conversation' in key else ""

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

def sanitize_text(text):
    return re.sub(r"[_*`]", "", text).replace("---", "").strip()

def sareth_gpt_response(conversation_history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for speaker, text in conversation_history:
        role = "user" if speaker == "You" else "assistant"
        messages.append({"role": role, "content": sanitize_text(text)})
    response = client.chat.completions.create(model="gpt-4", messages=messages, temperature=0.7)
    return response.choices[0].message.content

def should_surface_glyph(conversation_history):
    significance_check_prompt = {"role": "user", "content": "Does the user's reflection reveal a meaningful insight, tension, contradiction, or pattern worth surfacing a symbolic marker for? Answer only 'yes' or 'no'."}
    recent = conversation_history[-6:]
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for speaker, text in recent:
        messages.append({"role": "user" if speaker == "You" else "assistant", "content": sanitize_text(text)})
    messages.append(significance_check_prompt)
    try:
        response = client.chat.completions.create(model="gpt-4", messages=messages, temperature=0)
        return response.choices[0].message.content.strip().lower() == "yes"
    except Exception as e:
        st.error(f"API Error during glyph significance check: {e}")
        return False

def derive_glyph(user_input):
    engine = Recursor(max_depth=10, tension_threshold=0.7)
    seed_state = [len(word) for word in user_input.split()[:3]] or [1.0, 2.0, 3.0]
    avg = sum(engine.run(seed_state)) / len(seed_state)
    if avg < 2: return "G1"
    elif avg < 3.5: return "G2"
    elif avg < 5: return "G3"
    elif avg < 5.5: return "G4"
    elif avg < 6.5: return "G5"
    elif avg < 7.5: return "G6"
    else: return "G7"

def translate_glyph(glyph_code):
    symbol, meaning = GLYPH_MAP.get(glyph_code, ("❓", "Unknown glyph"))
    return f"{symbol} — {meaning}"

def compute_truth_core():
    return max(set(st.session_state.glyph_trace), key=st.session_state.glyph_trace.count) if st.session_state.glyph_trace else "None yet"

def reset_conversation():
    if st.session_state.conversation:
        st.session_state.conversation_history.append((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.conversation.copy()))
    st.session_state.conversation = []
    st.session_state.glyph_trace = []
    st.session_state.user_input = ""
    st.session_state.search_query = ""
    st.success("Conversation reset!")
    st.experimental_rerun()

def process_reflection():
    user_input = st.session_state.user_input.strip()
    if not user_input:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.conversation.append(("You", f"{user_input} _(at {timestamp})_"))

    sareth_response = sareth_gpt_response(st.session_state.conversation)

    if should_surface_glyph(st.session_state.conversation):
        glyph_code = derive_glyph(user_input)
        glyph_display = translate_glyph(glyph_code)
        st.session_state.glyph_trace.append(glyph_display)
        sareth_response += f"\n\n---\n**Symbolic Marker:** {glyph_display}"
    else:
        sareth_response += "\n\n_Note: No symbolic marker surfaced — reflect deeper to uncover more._"

    st.session_state.conversation.append(("Sareth", sareth_response))
    st.session_state.user_input = ""

# --- UI ---
st.title("🌀 Sareth | Recursive Reflection")

st.markdown(
    "The **Recursive Emergence Framework (REF)** analyzes your reflections in a recursive loop. "
    "**Sareth** guides you through this process, surfacing symbolic markers—called glyphs—to highlight key insights. "
    "Start by entering a thought below to explore what emerges."
)

with st.expander("⚙️ Run REF Engine"):
    depth = st.slider("Max Recursion Depth", 1, 10, 5, key="depth")
    tension = st.slider("Tension Threshold", 0.0, 1.0, 0.4, key="tension")
    if st.button("Run REF Engine"):
        state, glyph, halt_reason = run_recursive_engine(depth=depth, threshold=tension)
        st.success("Run Complete.")
        st.markdown(f"**🧠 Final State:** `{state}`")
        st.markdown(f"**🔣 Glyph ID:** `{glyph}`")
        st.markdown(f"**⛔ Halt Reason:** `{halt_reason}`")

st.text_input("Your reflection:", key="user_input", on_change=process_reflection)
st.button("Reflect with Sareth", on_click=process_reflection)
st.button("🔄 Reset Conversation", on_click=reset_conversation)

st.subheader("📜 Conversation History")
display_history = [m for m in st.session_state.conversation if st.session_state.search_query.lower() in m[1].lower()] if st.session_state.search_query else st.session_state.conversation
for speaker, text in reversed(display_history):
    st.markdown(f"**{speaker}:** {text}")

st.text_input("Search conversation:", key="search_query")

st.subheader("🧿 Last Symbolic Marker")
st.markdown(f"**{st.session_state.glyph_trace[-1]}**" if st.session_state.glyph_trace else "_None yet_")

st.subheader("💎 Truth Core")
st.markdown(f"**Current Truth Core:** {compute_truth_core()}")

st.subheader("📊 Glyph Frequency Summary")
for glyph, count in Counter(st.session_state.glyph_trace).items():
    st.markdown(f"**{glyph}**: {count} times")

with st.expander("📜 Glyph Meaning Glossary"):
    for code, (symbol, meaning) in GLYPH_MAP.items():
        st.markdown(f"**{symbol}**: {meaning}")

with st.expander("❔ About Sareth & REF"):
    st.markdown("""
Sareth is your recursive reflection guide, combining AI with symbolic interpretation.
Each reflection surfaces a symbolic marker, tracing your cognitive journey — but only when your insights are deep enough.

- **Recursion:** Deeper reflection on each layer of thought.
- **Glyphs:** Symbols representing your inner state evolution.
- **Truth Core:** The dominant theme of your session.
""")

with st.expander("🧪 Run Sareth Diagnostic"):
    if st.button("Run Diagnostic"):
        result = run_sareth_test()
        st.success(f"Sareth Diagnostic Result: {result}")

