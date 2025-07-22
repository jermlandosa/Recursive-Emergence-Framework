"""Streamlit web UI for the Recursive Emergence Framework."""

import os
import random
import re
from collections import Counter
from datetime import datetime

import openai
import streamlit as st

from main import run_recursive_engine
from recursor import Recursor
from test_tools import run_sareth_test

st.set_page_config(page_title="Sareth | Recursive Reflection", layout="wide")
st.write("App Loaded")

# Mobile responsive styling
MOBILE_CSS = """
<style>
@media (max-width: 768px) {
    .block-container {padding:1rem !important;}
    .stButton>button {width:100%;margin-top:.5rem;}
    textarea,input {font-size:1.1rem !important;}
}
.block-container {max-width:700px;margin:auto;}
</style>
"""

st.markdown(
    '<meta name="viewport" content="width=device-width, initial-scale=1">',
    unsafe_allow_html=True,
)
st.markdown(MOBILE_CSS, unsafe_allow_html=True)

# Styling for latest Sareth response
LATEST_CSS = """
<style>
.sareth-response {
    background-color: #1e1e1e !important;
    color: #ffffff !important;
    padding: 10px;
    border-radius: 5px;
    margin-top: 10px;
}
</style>
"""
st.markdown(LATEST_CSS, unsafe_allow_html=True)

client = openai.Client(api_key=st.secrets["openai"]["api_key"])

# Initialize session state
for key in [
    "conversation",
    "glyph_trace",
    "conversation_history",
    "user_input",
    "search_query",
    "error_msg",
]:
    if key not in st.session_state:
        default = [] if "trace" in key or "conversation" in key else ""
        st.session_state[key] = default

# Persistent last Sareth output
LAST_RESPONSE_FILE = "last_sareth_output.txt"
if "last_sareth_output" not in st.session_state:
    if os.path.exists(LAST_RESPONSE_FILE):
        with open(LAST_RESPONSE_FILE, "r") as f:
            st.session_state.last_sareth_output = f.read()
    else:
        st.session_state.last_sareth_output = ""

# Toggle for showing history inline
if "show_history" not in st.session_state:
    st.session_state.show_history = False

# Track UI state
if 'show_help' not in st.session_state:
    st.session_state.show_help = False
if 'onboarded' not in st.session_state:
    st.session_state.onboarded = False

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
    """Strip markdown artifacts and timestamps from chat history text."""
    text = re.sub(r"_\(at .*\)_", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text.replace("---", "").strip()

def sareth_gpt_response(conversation_history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for speaker, text in conversation_history:
        role = "user" if speaker == "You" else "assistant"
        messages.append({"role": role, "content": sanitize_text(text)})
    response = client.chat.completions.create(model="gpt-4", messages=messages, temperature=0.7)
    return response.choices[0].message.content

def should_surface_glyph(conversation_history):
    """Check if the latest exchange warrants surfacing a glyph."""
    significance_check_prompt = {
        "role": "user",
        "content": (
            "Does the user's reflection reveal a meaningful insight, tension, contradiction, or pattern worth surfacing a symbolic marker for? "
            "Answer only 'yes' or 'no'."
        ),
    }

    recent_history = conversation_history[-6:]
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for speaker, text in recent_history:
        role = "user" if speaker == "You" else "assistant"
        messages.append({"role": role, "content": sanitize_text(text)})

    messages.append(significance_check_prompt)
    try:
        response = client.chat.completions.create(model="gpt-4", messages=messages, temperature=0)
        return response.choices[0].message.content.strip().lower() == "yes"
    except Exception as exc:
        st.error(f"API Error during glyph significance check:\n\n{exc}")
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
    st.rerun()

def process_reflection():
    try:
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
        st.session_state.last_sareth_output = sareth_response
        with open(LAST_RESPONSE_FILE, "w") as f:
            f.write(sareth_response)
    except Exception as exc:
        st.session_state.error_msg = f"Reflection error: {exc}"
    finally:
        st.session_state.user_input = ""
        st.rerun()

# --- UI ---
st.title("🌀 Sareth | Recursive Reflection")

intro_md = """
**Welcome to the Recursive Emergence Framework (REF).**

REF is a symbolic cognitive architecture that guides you through recursive self-reflection. Enter a thought below and press **Reflect with Sareth** to surface symbolic markers known as *glyphs*. Use the REF Engine section for deeper experimentation with recursion settings.
"""
st.markdown(intro_md)

if st.session_state.error_msg:
    st.error(st.session_state.error_msg)
    st.session_state.error_msg = ""

if not st.session_state.onboarded:
    with st.sidebar.expander("👋 Quick Start", expanded=True):
        st.markdown("1. Write a thought in the text box.\n2. Click **Reflect with Sareth**.\n3. Review the glyphs and insights that appear.")
        if st.button("Start Exploring", key="start_onboarding"):
            st.session_state.onboarded = True
            st.rerun()

with st.expander("⚙️ Run REF Engine"):
    depth = st.slider("Max Recursion Depth", 1, 10, 5, key="depth", help="Number of recursion cycles to run")
    tension = st.slider("Tension Threshold", 0.0, 1.0, 0.4, key="tension", help="How easily contradictions surface glyphs")
    if st.button("Run REF Engine", help="Execute the engine with these settings"):
        try:
            state, glyph, halt_reason = run_recursive_engine(depth=depth, threshold=tension)
        except Exception as e:
            st.error(f"Engine error: {e}")
        else:
            st.success("Run Complete.")
            st.markdown(f"**🧠 Final State:** `{state}`", help="State returned by the recursion engine")
            st.markdown(f"**🔣 Glyph ID:** `{glyph}`", help="Symbolic marker produced")
            st.markdown(f"**⛔ Halt Reason:** `{halt_reason}`", help="Why the engine stopped")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["Reflect", "Conversation History", "Insights"])

with tab1:
    st.markdown("#### Sareth's Latest Response")
    st.markdown(
        f"<div class='sareth-response'>{st.session_state.last_sareth_output or '_No response yet_'}</div>",
        unsafe_allow_html=True,
    )

    history_label = "Hide History" if st.session_state.show_history else "View History"
    if st.button(history_label, key="toggle_history"):
        st.session_state.show_history = not st.session_state.show_history
        st.rerun()

    if st.session_state.show_history:
        st.markdown("---")
        for speaker, text in reversed(st.session_state.conversation):
            with st.expander(f"{speaker}"):
                st.markdown(text)

    st.text_area(
        "Your reflection:",
        key="user_input",
        height=150,
        help="Write a thought or question here",
    )
    col1, col2, col3 = st.columns(3)
    col1.button("Reflect with Sareth", on_click=process_reflection)

    def load_random_prompt():
        prompt = random.choice(reflection_prompts)
        st.session_state.conversation.append(("Sareth", prompt))
        st.session_state.last_sareth_output = prompt
        with open(LAST_RESPONSE_FILE, "w") as f:
            f.write(prompt)
        st.session_state.user_input = ""
        st.rerun()

    col2.button("Prompt", on_click=load_random_prompt)
    col3.button("🔄 Reset", on_click=reset_conversation)

with tab2:
    st.caption("Past reflections and responses")
    st.markdown("---")
    display_history = [m for m in st.session_state.conversation if st.session_state.search_query.lower() in m[1].lower()] if st.session_state.search_query else st.session_state.conversation
    for speaker, text in reversed(display_history):
        with st.expander(f"{speaker}"):
            st.markdown(text)
    st.text_input("Search conversation:", key="search_query", help="Filter conversation history")

with tab3:
    st.caption("Summary of symbolic insights")
    st.markdown("---")
    st.subheader("🧿 Last Symbolic Marker")
    st.markdown(f"**{st.session_state.glyph_trace[-1]}**" if st.session_state.glyph_trace else "_None yet_")

    st.markdown("---")
    st.subheader("💎 Truth Core")
    st.markdown(f"**Current Truth Core:** {compute_truth_core()}")

    st.markdown("---")
    st.subheader("📊 Glyph Frequency Summary")
    for glyph, count in Counter(st.session_state.glyph_trace).items():
        st.markdown(f"**{glyph}**: {count} times")

    st.markdown("---")
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
        if st.button("Run Diagnostic", help="Health check for Sareth"):
            result = run_sareth_test()
            st.success(f"Sareth Diagnostic Result: {result}")

# Persistent sidebar help
if st.sidebar.button("❔ How to Use"):
    st.session_state.show_help = not st.session_state.show_help
if st.session_state.show_help:
    st.sidebar.markdown("""**Using Sareth**
1. Enter a reflection in the *Reflect* tab.
2. Click **Reflect with Sareth**.
3. View glyphs and summaries in the *Insights* tab.
Use the REF Engine for advanced options.""")

