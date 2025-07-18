# streamlit_app.py
import streamlit as st
from main import run_recursive_engine
import openai
from recursor import Recursor
from test_tools import run_sareth_test
from datetime import datetime
from collections import Counter
import random
import re

st.set_page_config(page_title="Sareth | Recursive Reflection", layout="wide")

with st.expander("⚙️ Run REF Engine"):
    depth = st.slider("Max Recursion Depth", 1, 10, 5, key="depth")
    tension = st.slider("Tension Threshold", 0.0, 1.0, 0.4, key="tension")
    if st.button("Run Sareth Engine"):
        state, glyph, halt_reason = run_recursive_engine(depth=depth, threshold=tension)
        st.success("Run Complete.")
        st.markdown(f"**🧠 Final State:** `{state}`")
        st.markdown(f"**🔣 Glyph ID:** `{glyph}`")
        st.markdown(f"**⛔ Halt Reason:** `{halt_reason}`")


client = openai.Client(api_key=st.secrets["openai"]["api_key"])

if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "glyph_trace" not in st.session_state:
    st.session_state.glyph_trace = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

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
    # Remove markdown, timestamps, separators
    text = re.sub(r"_\(at .*\)_", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = text.replace("---", "").strip()
    return text

def sareth_gpt_response(conversation_history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for speaker, text in conversation_history:
        role = "user" if speaker == "You" else "assistant"
        messages.append({"role": role, "content": sanitize_text(text)})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

def should_surface_glyph(conversation_history):
    significance_check_prompt = {
        "role": "user",
        "content": (
            "Based on our last exchange, does the user's reflection reveal a meaningful insight, tension, contradiction, "
            "or pattern worth surfacing a symbolic marker for? Answer only 'yes' or 'no'."
        )
    }

    recent_history = conversation_history[-6:]  # Limit to last 6 messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for speaker, text in recent_history:
        role = "user" if speaker == "You" else "assistant"
        sanitized = sanitize_text(text)
        messages.append({"role": role, "content": sanitized})

    messages.append(significance_check_prompt)

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content.strip().lower() == "yes"
    except Exception as e:
        st.error(f"API Error during glyph significance check:\n\n{e}")
        return False

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

def reset_conversation():
    if st.session_state.conversation:
        st.session_state.conversation_history.append(
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.conversation.copy())
        )
    st.session_state.conversation = []
    st.session_state.glyph_trace = []
    st.success("Conversation reset!")
    st.experimental_rerun()

def process_reflection(message: str):
    user_input = message.strip()
    if not user_input:
        return
    st.session_state.conversation.append(("You", user_input))
    sareth_response = sareth_gpt_response(st.session_state.conversation)

    if should_surface_glyph(st.session_state.conversation):
        glyph_code = derive_glyph(user_input)
        glyph_display = translate_glyph(glyph_code)
        st.session_state.glyph_trace.append(glyph_display)
        full_response = f"{sareth_response}\n\n---\n**Symbolic Marker:** {glyph_display}"
    else:
        full_response = f"{sareth_response}\n\n_Note: No symbolic marker surfaced — reflect deeper to uncover more._"

    st.session_state.conversation.append(("Sareth", full_response))

# --- UI ---

st.title("🌀 Sareth | Recursive Reflection")

chat_col, history_col = st.columns([3, 1])

with chat_col:
    for speaker, text in st.session_state.conversation:
        with st.chat_message("user" if speaker == "You" else "assistant"):
            st.markdown(text)

    prompt = st.chat_input("Share a reflection...")
    if prompt:
        process_reflection(prompt)

    cols = st.columns(2)
    with cols[0]:
        if st.button("🎲 Generate Reflection Prompt"):
            st.info(random.choice(reflection_prompts))
    with cols[1]:
        st.button("🔄 Reset Conversation", on_click=reset_conversation)

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

with history_col:
    st.subheader("📂 Past Sessions")
    for ts, conv in reversed(st.session_state.conversation_history):
        with st.expander(ts):
            for speaker, text in conv:
                st.markdown(f"**{speaker}:** {text}")

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
