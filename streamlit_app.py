import json
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="REF • Sareth", page_icon="🔁", layout="centered")

# ============== CONFIG ==============
DB_PATH = Path("ref_history.db")

SYSTEM_PROMPT = (
    "You are Sareth, the REF assistant for the Recursive Emergence Framework (REF). "
    "Your style: concise, deep, precise; no filler. Apply truth-rich recursion, contradiction checks, "
    "and depth integrity by default.\n\n"
    "OUTPUT CONTRACT:\n"
    "1) First, produce the natural-language reply for the user (streamed).\n"
    "2) Then, on the FINAL line ONLY, append a single-line JSON object with this shape: "
    "{\"ref\":{\"glyph\":\"G1|G2|G3|G4|G5|G6|G7\",\"glyph_meaning\":\"short context-aware phrase\","
    "\"plan\":{\"goal\":\"...\",\"steps\":[\"step1\",\"step2\"],\"question\":\"one precise focusing question\"},"
    "\"suggestions\":[\"short next message 1\",\"short next message 2\"]}}\n"
    "Do not add commentary after the JSON. Keep JSON compact, no newlines inside it."
)

GLYPH_FALLBACKS = {
    "G1": "greeting / orientation",
    "G2": "tension surfaced",
    "G3": "new thread / growth",
    "G4": "core friction",
    "G5": "identity recursion",
    "G6": "complex entanglement",
    "G7": "truth core surfaced",
}

# ============== UTILITIES ==============
def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"

st.caption(f"Deployed commit: `{_git_sha()}` on branch: `Main`")

def _resolve_api_key() -> str:
    # Preferred
    if "OPENAI_API_KEY" in st.secrets and st.secrets["OPENAI_API_KEY"]:
        return st.secrets["OPENAI_API_KEY"]
    # Fallbacks
    if "openai" in st.secrets and st.secrets["openai"].get("api_key"):
        return st.secrets["openai"]["api_key"]
    if "serith" in st.secrets and st.secrets["serith"].get("api_key"):
        return st.secrets["serith"]["api_key"]
    return ""

api_key = _resolve_api_key()
if not api_key:
    st.error(
        "No API key found. Add one of:\n"
        '- OPENAI_API_KEY = "sk-..."\n'
        "- [openai]\\napi_key = \"sk-...\"\n"
        "- [serith]\\napi_key = \"sk-...\""
    )
    st.stop()

client = OpenAI(api_key=api_key)

# ============== STORAGE (SQLite) ==============
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
        """)

def new_session(title: str) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("INSERT INTO sessions(title, created_at) VALUES(?,?)",
                           (title, datetime.utcnow().isoformat()))
        return cur.lastrowid

def list_sessions():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT id, title, created_at FROM sessions ORDER BY id DESC").fetchall()
        return rows

def save_message(session_id: int, role: str, content: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages(session_id, role, content, created_at) VALUES(?,?,?,?)",
            (session_id, role, content, datetime.utcnow().isoformat())
        )

def load_messages(session_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE session_id=? ORDER BY id ASC", (session_id,)
        ).fetchall()
        return [{"role": r, "content": c} for (r, c) in rows]

init_db()

# ============== STATE ==============
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "last_ref_meta" not in st.session_state:
    st.session_state.last_ref_meta = None

# ============== SIDEBAR ==============
with st.sidebar:
    st.subheader("Session")
    sessions = list_sessions()
    titles = [f"#{sid} • {title}" for (sid, title, _) in sessions]
    choice = st.selectbox("Load a session", ["— New session —"] + titles, index=0)
    if choice != "— New session —":
        idx = [f"#{sid} • {title}" for (sid, title, _ ) in sessions].index(choice)
        sid, title, _ = sessions[idx]
        st.session_state.session_id = sid
        msgs = load_messages(sid)
        # Rebuild memory with system
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}] + msgs
        st.success(f"Loaded session: {title}")

    new_title = st.text_input("New session title", value=datetime.now().strftime("REF %Y-%m-%d %H:%M"))
    if st.button("Start new session"):
        sid = new_session(new_title or f"REF {datetime.utcnow().isoformat(timespec='minutes')}")
        st.session_state.session_id = sid
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.session_state.last_ref_meta = None
        st.success(f"Started session #{sid}")
        st.rerun()

    st.markdown("---")
    st.subheader("Model")
    model = st.text_input("OpenAI model", value="gpt-4o-mini")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    coaching = st.select_slider("Coaching intensity", options=["low", "medium", "high"], value="medium")
    depth_on = st.toggle("Depth recursion hints", value=True)

    st.caption("Tip: sessions persist in this container. Redeploys reset storage.")

st.title("REF • Sareth")

# ============== RENDER HISTORY ==============
for m in st.session_state.messages:
    if m["role"] == "system":
        continue
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])

# ============== INPUT & STREAM ==============
prompt = st.chat_input("Type your message…")
if prompt:
    # Augment user message with optional meta flags
    user_msg = prompt
    if depth_on:
        user_msg += "\n\n[meta: depth=on]"
    user_msg += f"\n[meta: coaching={coaching}]"

    st.session_state.messages.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Persist user msg
    if st.session_state.session_id:
        save_message(st.session_state.session_id, "user", prompt)

    # Stream assistant
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
                out.markdown(acc)

        # Parse trailing JSON
        ref_meta = None
        try:
            last_line = acc.splitlines()[-1].strip()
            if last_line.startswith("{") and last_line.endswith("}"):
                data = json.loads(last_line)
                if "ref" in data and isinstance(data["ref"], dict):
                    ref_meta = data["ref"]
                    # remove JSON from visible text
                    acc = "\n".join(acc.splitlines()[:-1]).rstrip()
        except Exception:
            pass

        # Render assistant text + REF panel
        out.markdown(acc)
        if ref_meta:
            glyph = ref_meta.get("glyph", "")
            meaning = ref_meta.get("glyph_meaning") or GLYPH_FALLBACKS.get(glyph, "")
            plan = ref_meta.get("plan", {}) or {}
            suggestions = ref_meta.get("suggestions", []) or []

            st.session_state.last_ref_meta = ref_meta

            st.markdown("---")
            st.markdown(f"**Symbolic Marker:** `{glyph or '—'}` — {meaning or '—'}")

            # Coaching panel
            if plan or suggestions:
                with st.expander("🧭 Guidance (REF Plan)", expanded=True):
                    st.write(f"**Goal:** {plan.get('goal','—')}")
                    steps = plan.get("steps") or []
                    if steps:
                        st.write("**Next steps:**")
                        for i, s in enumerate(steps[:3], 1):
                            st.write(f"{i}. {s}")
                    if plan.get("question"):
                        st.write(f"**Focusing question:** {plan['question']}")
                    if suggestions:
                        st.write("**Suggestions:**")
                        st.write(" · " + " · ".join(suggestions[:4]))

        # Save assistant message (without JSON)
        st.session_state.messages.append({"role": "assistant", "content": acc})
        if st.session_state.session_id:
            save_message(st.session_state.session_id, "assistant", acc)