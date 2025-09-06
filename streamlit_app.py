import json
import subprocess
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="REF • Sareth", page_icon="🔁")

SYSTEM_PROMPT = (
    "You are Sareth, the REF assistant for the Recursive Emergence Framework (REF). "
    "Be concise, deep, and precise. Apply truth-rich recursion, contradiction checks, "
    "and depth integrity by default. Avoid fluff.\n\n"
    "At the end of every answer, append a JSON block on a single line like:\n"
    '{"ref":{"glyph":"G1..G7","meaning":"short phrase"}}\n'
    "Do not add commentary after the JSON."
)

# Show deployed commit for sanity checks
def _git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"
st.caption(f"Deployed commit: `{_git_sha()}` on branch: `Main`")

# --- Secrets resolution with fallbacks ---
def _resolve_api_key() -> str:
    # preferred: top-level
    if "OPENAI_API_KEY" in st.secrets and st.secrets["OPENAI_API_KEY"]:
        return st.secrets["OPENAI_API_KEY"]
    # fallback: [openai].api_key
    if "openai" in st.secrets and "api_key" in st.secrets["openai"]:
        if st.secrets["openai"]["api_key"]:
            return st.secrets["openai"]["api_key"]
    # fallback: [serith].api_key
    if "serith" in st.secrets and "api_key" in st.secrets["serith"]:
        if st.secrets["serith"]["api_key"]:
            return st.secrets["serith"]["api_key"]
    return ""

# --- Secrets check (with fallback keys) ---
api_key = _resolve_api_key()
if not api_key:
    st.error("No API key found. Add one of:\n"
             "- OPENAI_API_KEY = \"sk-...\"\n"
             "- [openai]\napi_key = \"sk-...\"\n"
             "- [serith]\napi_key = \"sk-...\"\n"
             "in Streamlit Cloud → App → Settings → Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# --- State ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

st.title("REF • Sareth")

with st.sidebar:
    st.subheader("Settings")
    model = st.text_input("OpenAI model", value="gpt-4o-mini")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    if st.button("Reset chat"):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()

# Render history (no system)
for m in st.session_state.messages:
    if m["role"] == "system":
        continue
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])

# Input + stream
user_text = st.chat_input("Type your message…")
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        out = st.empty()
        acc = ""

        stream = client.chat.completions.create(
            model=model,
            temperature=temperature,
            stream=True,
            # include system prompt so Sareth/REF stays active
            messages=st.session_state.messages,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                acc += delta
                out.markdown(acc)

        # Parse trailing REF JSON block (if present) to show glyph separately
        glyph_line = ""
        try:
            # find last {...} JSON object on a single line
            last_line = acc.splitlines()[-1].strip()
            if last_line.startswith("{") and last_line.endswith("}"):
                data = json.loads(last_line)
                if "ref" in data and isinstance(data["ref"], dict):
                    g = data["ref"].get("glyph", "")
                    meaning = data["ref"].get("meaning", "")
                    if g or meaning:
                        glyph_line = f"**Symbolic Marker:** `{g}` — {meaning}"
                        # remove JSON line from visible text
                        acc = "\n".join(acc.splitlines()[:-1]).rstrip()
        except Exception:
            pass

        if glyph_line:
            out.markdown(acc + ("\n\n---\n" + glyph_line))
        st.session_state.messages.append({"role": "assistant", "content": acc + ("\n\n---\n" + glyph_line if glyph_line else "")})

