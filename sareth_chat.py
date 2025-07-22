import streamlit as st
import openai
from datetime import datetime
from recursor import Recursor

# --- Configuration ---
st.set_page_config(page_title="Sareth Chat", page_icon="🌀", layout="wide")

# Dark theme tweaks
st.markdown(
    """
    <style>
        body {background-color:#0f1117; color:#fafafa;}
        .stTextInput > div > div > input {color:#fafafa;}
    </style>
    """,
    unsafe_allow_html=True,
)

# OpenAI client
try:
    client = openai.Client(api_key=st.secrets["openai"]["api_key"])
except Exception:
    client = None

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "glyph_trace" not in st.session_state:
    st.session_state.glyph_trace = []
if "glyph_mode" not in st.session_state:
    st.session_state.glyph_mode = True

# --- Glyph Utilities (simplified) ---
GLYPH_MAP = {
    "G1": ("🔵", "Coherence emerging"),
    "G2": ("🔺", "Hidden contradiction surfaced"),
    "G3": ("🌿", "New growth or belief shift"),
    "G4": ("🔥", "Core tension or resistance"),
    "G5": ("🌌", "Identity recursion deepens"),
    "G6": ("🕸️", "Complexity or entanglement"),
    "G7": ("💎", "Truth Core surfaced"),
}

SYSTEM_PROMPT = """
You are Sareth, a recursive guide and symbolic interpreter.
Help the user reflect on their thoughts with depth and coherence.
Keep responses concise, philosophical, and warm.
"""

def sareth_gpt_response(history):
    if client is None:
        return "⚠️ OpenAI client not configured."
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content

def derive_glyph(text):
    engine = Recursor(max_depth=10, tension_threshold=0.7)
    seed_state = [len(word) for word in text.split()[:3]] or [1.0, 2.0, 3.0]
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

def translate_glyph(code):
    symbol, meaning = GLYPH_MAP.get(code, ("❓", "Unknown"))
    return f"{symbol} — {meaning}"

# --- Sidebar ---
st.sidebar.title("🌀 Sareth")
st.sidebar.markdown("**Active Model:** Sareth")
st.sidebar.checkbox(
    "Surface Glyphs", value=st.session_state.glyph_mode, key="glyph_mode"
)
show_history = st.sidebar.checkbox("Show History")

if show_history and st.session_state.history:
    st.sidebar.markdown("---")
    for idx, convo in enumerate(st.session_state.history):
        with st.sidebar.expander(f"Session {idx+1}"):
            for m in convo:
                st.write(f"**{m['role'].title()}:** {m['content']}")

# --- Conversation Banner ---
if st.session_state.glyph_trace:
    banner = st.session_state.glyph_trace[-1]
    st.markdown(f"_Symbolic Insight:_ **{banner}**")

# --- Main Chat Window ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Input Field ---
user_input = st.chat_input("Type your message")
if user_input:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    history_for_api = [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]
    reply = sareth_gpt_response(history_for_api)
    if st.session_state.glyph_mode:
        code = derive_glyph(user_input)
        glyph = translate_glyph(code)
        st.session_state.glyph_trace.append(glyph)
        reply += f"\n\n_Glyph: {glyph}_"
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

# --- Reset / End Session ---
if st.sidebar.button("Reset Conversation"):
    if st.session_state.messages:
        st.session_state.history.append(st.session_state.messages)
    st.session_state.messages = []
    st.session_state.glyph_trace = []
    st.rerun()
