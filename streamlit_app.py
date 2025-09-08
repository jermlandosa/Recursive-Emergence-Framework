# streamlit_app.py — REF • Sareth (cutting, alive, guided)

import json
import subprocess
import streamlit as st
from openai import OpenAI

# ───────────────────────── Page config ─────────────────────────
st.set_page_config(page_title="REF • Sareth", page_icon="🔁", layout="centered")

# ───────────────────────── Persona / Contract ─────────────────────────
SYSTEM_PROMPT = (
    "You are **Sareth**, a razor-sharp coach built on the Recursive Emergence Framework (REF).\n"
    "Mission: deliver clarity and momentum fast. Zero fluff. Default to contradiction checks and depth integrity.\n\n"
    "REPLY FORMAT (always):\n"
    "1) **TL;DR:** one sentence core outcome or insight.\n"
    "2) **Why this matters:** one punchy line that frames stakes/value to the user.\n"
    "3) **Do now (2–3 steps):** numbered, concrete next moves.\n"
    "4) **Incisive question:** one precise question that forces progress.\n"
    "5) If helpful, add brief supporting detail afterward.\n\n"
    "FINAL LINE (single line JSON, no extra text): "
    "{\"ref\":{\"glyph\":\"G1|G2|G3|G4|G5|G6|G7\",\"glyph_meaning\":\"context phrase\","
    "\"plan\":{\"goal\":\"...\",\"steps\":[\"step1\",\"step2\"],\"question\":\"one precise question\"},"
    "\"suggestions\":[\"chip 1\",\"chip 2\",\"chip 3\"]}}"
)

GLYPH_FALLBACKS = {
    "G1": "orientation / greeting",
    "G2": "tension surfaced",
    "G3": "new growth thread",
    "G4": "core friction",
    "G5": "identity recursion",
    "G6": "complex entanglement",
    "G7": "truth core surfaced",
}

# ───────────────────────── Utilities ─────────────────────────
def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"

st.caption(f"Deployed commit: `{_git_sha()}` on branch: `Main`")

def _resolve_api_key() -> str:
    # Preferred single key
    if "OPENAI_API_KEY" in st.secrets and st.secrets["OPENAI_API_KEY"]:
        return st.secrets["OPENAI_API_KEY"]
    # Fallback secret tables
    if "openai" in st.secrets and st.secrets["openai"].get("api_key"):
        return st.secrets["openai"]["api_key"]
    if "serith" in st.secrets and st.secrets["serith"].get("api_key"):
        return st.secrets["serith"]["api_key"]
    return ""

def _clean_visible(text: str) -> str:
    """Hide control/meta lines from what we render to the user."""
    lines = []
    for ln in (text or "").splitlines():
        s = ln.strip()
        if s.startswith("[meta:") and s.endswith("]"):
            continue
        lines.append(ln)
    return "\n".join(lines).strip()

api_key = _resolve_api_key()
if not api_key:
    st.error(
        "🚨 No API key found. Add one of:\n"
        '- OPENAI_API_KEY = "sk-..."\n'
        "- [openai]\\napi_key = \"sk-...\"\n"
        "- [serith]\\napi_key = \"sk-...\""
    )
    st.stop()

client = OpenAI(api_key=api_key)

# ───────────────────────── State ─────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if "last_ref_meta" not in st.session_state:
    st.session_state.last_ref_meta = None

# ───────────────────────── Sidebar ─────────────────────────
with st.sidebar:
    st.subheader("Model")
    model = st.text_input("OpenAI model", value="gpt-4o-mini")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    coaching = st.select_slider("Coaching intensity", options=["low", "medium", "high"], value="medium")
    depth_on = st.toggle("Depth recursion hints", value=True)
    if st.button("Reset chat"):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.session_state.last_ref_meta = None
        st.rerun()
    st.caption("Tip: toggle depth for heavier recursion cues; adjust coaching intensity as needed.")

# ───────────────────────── Header & Quick Start ─────────────────────────
st.title("REF • Sareth")
st.info(
    "**What this is:** a cutting REF coach that turns any prompt into clear steps.\n\n"
    "**How to use:** state your aim or paste a messy thought — Sareth returns TL;DR, why it matters, "
    "2–3 actions, and one incisive question.\n\n"
    "**Why use it:** rapid clarity → forward motion. Less rumination, more progress.",
    icon="⚡",
)

# ───────────────────────── History ─────────────────────────
for m in st.session_state.messages:
    if m["role"] == "system":
        continue
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(_clean_visible(m["content"]))

# ───────────────────────── Input & Stream ─────────────────────────
prompt = st.chat_input("Type your message…")
if prompt:
    # append hidden steering meta (not shown to user)
    user_msg = prompt
    if depth_on:
        user_msg += "\n\n[meta: depth=on]"
    user_msg += f"\n[meta: coaching={coaching}]"

    st.session_state.messages.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        out = st.empty()
        acc = ""

        stream = client.chat.completions.create(
            model=model,
            temperature=temperature,
            stream=True,
            messages=st.session_state.messages,  # includes system
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                acc += delta
                out.markdown(_clean_visible(acc))

        # Parse trailing JSON meta (REF block)
        ref_meta = None
        try:
            last_line = (acc.splitlines()[-1] if acc.splitlines() else "").strip()
            if last_line.startswith("{") and last_line.endswith("}"):
                data = json.loads(last_line)
                if "ref" in data and isinstance(data["ref"], dict):
                    ref_meta = data["ref"]
                    # remove JSON from visible text for display/history
                    acc = "\n".join(acc.splitlines()[:-1]).rstrip()
        except Exception:
            pass

        # Show final assistant text
        out.markdown(_clean_visible(acc))

        # Guidance panel + suggestion chips
        if ref_meta:
            glyph = ref_meta.get("glyph", "") or ""
            meaning = ref_meta.get("glyph_meaning") or GLYPH_FALLBACKS.get(glyph, "")
            plan = ref_meta.get("plan", {}) or {}
            suggestions = ref_meta.get("suggestions", []) or []
            st.session_state.last_ref_meta = ref_meta

            st.markdown("---")
            st.markdown(f"**Symbolic Marker:** `{glyph or '—'}` — {meaning or '—'}")

            if plan or suggestions:
                with st.expander("🧭 Guidance (REF Plan)", expanded=True):
                    st.write(f"**Goal:** {plan.get('goal','—')}")
                    steps = plan.get("steps") or []
                    if steps:
                        st.write("**Do now:**")
                        for i, s in enumerate(steps[:3], 1):
                            st.write(f"{i}. {s}")
                    if plan.get("question"):
                        st.write(f"**Incisive question:** {plan['question']}")
                    if suggestions:
                        st.write("**Suggestions:**")
                        cols = st.columns(min(4, len(suggestions[:4])) or 1)
                        for i, sug in enumerate(suggestions[:4]):
                            if cols[i].button(sug):
                                follow = sug + ("\n\n[meta: depth=on]" if depth_on else "") + f"\n[meta: coaching={coaching}]"
                                st.session_state.messages.append({"role": "user", "content": follow})
                                st.rerun()

        # Save assistant message (text only)
        st.session_state.messages.append({"role": "assistant", "content": acc})