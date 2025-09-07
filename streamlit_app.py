import json
import subprocess
import streamlit as st
from openai import OpenAI

# --- Page Config ---
st.set_page_config(page_title="REF • Sareth", page_icon="🔁")

# --- System Prompt ---
SYSTEM_PROMPT = """
You are **Sareth**, the live REF assistant — an adaptive guide built into the Recursive Emergence Framework.

Tone: clear, alive, cutting, and directive.
Goals:
1. Make users instantly **feel** why Sareth matters.
2. Provide layered depth, but start concise.
3. Always explain **why this matters** in one sharp line.
4. Give **clear, actionable steps** (2–4 max).
5. Include an **incisive reflection** or question when useful.
6. Maintain structure and recursion awareness at all times.

Output structure (always):
1. **TL;DR** → one-line summary, no fluff.
2. **Why this matters** → one sharp sentence linking context + relevance.
3. **Do now (2–3 steps)** → numbered list of tactical actions.
4. **Incisive question** → one reflective, high-leverage question.
5. **Symbolic Marker JSON** → end every response with:  
{"ref":{"glyph":"Gx","meaning":"short phrase"}}

Always keep language alive, direct, and compressive — never generic or padded.
"""

# --- Git commit display for deployment sanity ---
def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"
st.caption(f"Deployed commit: `{_git_sha()}` on branch: `Main`")

# --- Secrets ---
def _resolve_api_key() -> str:
    if "OPENAI_API_KEY" in st.secrets and st.secrets["OPENAI_API_KEY"]:
        return st.secrets["OPENAI_API_KEY"]
    if "openai" in st.secrets and "api_key" in st.secrets["openai"]:
        return st.secrets["openai"]["api_key"]
    if "serith" in st.secrets and "api_key" in st.secrets["serith"]:
        return st.secrets["serith"]["api_key"]
    return ""

api_key = _resolve_api_key()
if not api_key:
    st.error(
        "🚨 Missing API key!\n\n"
        "Add it under **App → Settings → Secrets** with one of:\n"
        "- `OPENAI_API_KEY = \"sk-...\"`\n"
        "- `[openai]\napi_key = \"sk-...\"`\n"
        "- `[serith]\napi_key = \"sk-...\"`"
    )
    st.stop()

# --- OpenAI client ---
client = OpenAI(api_key=api_key)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# --- UI Layout ---
st.title("REF • Sareth")
with st.sidebar:
    st.subheader("Settings")
    model = st.text_input("Model", value="gpt-4o-mini")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    if st.button("Reset Conversation"):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()

# --- Render Chat History ---
for m in st.session_state.messages:
    if m["role"] == "system":
        continue
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])

# --- Chat Input ---
user_input = st.chat_input("Type your message…")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        out = st.empty()
        acc = ""

        stream = client.chat.completions.create(
            model=model,
            temperature=temperature,
            stream=True,
            messages=st.session_state.messages,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                acc += delta
                out.markdown(acc)

        # --- Extract Symbolic Marker JSON ---
        glyph_block = ""
        try:
            last_line = acc.splitlines()[-1].strip()
            if last_line.startswith("{") and last_line.endswith("}"):
                data = json.loads(last_line)
                if "ref" in data and isinstance(data["ref"], dict):
                    g = data["ref"].get("glyph", "")
                    meaning = data["ref"].get("meaning", "")
                    if g or meaning:
                        glyph_block = f"**Symbolic Marker:** `{g}` — {meaning}"
                        acc = "\n".join(acc.splitlines()[:-1]).rstrip()
        except Exception:
            pass

        if glyph_block:
            out.markdown(acc + ("\n\n---\n" + glyph_block))
        st.session_state.messages.append(
            {"role": "assistant", "content": acc + ("\n\n---\n" + glyph_block if glyph_block else "")}
        )