import json
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
import streamlit as st
from openai import OpenAI

# =================== App config ===================
st.set_page_config(page_title="REF • Sareth", page_icon="🔁", layout="centered")
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
    "\"suggestions\":[\"short next message 1\",\"short next message 2\"]}} "
    "Do not add commentary after the JSON. Keep JSON compact, no newlines inside it."
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

# =================== Utilities ===================
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

# =================== Storage (SQLite) ===================
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS insights(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                glyph TEXT,
                glyph_meaning TEXT,
                goal TEXT,
                steps TEXT,            -- JSON array
                question TEXT,
                suggestions TEXT,      -- JSON array
                created_at TEXT NOT NULL,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
        """)

def new_session(title: str) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "INSERT INTO sessions(title, created_at) VALUES(?,?)",
            (title, datetime.utcnow().isoformat(timespec="seconds"))
        )
        return cur.lastrowid

def list_sessions():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT id, title, created_at FROM sessions ORDER BY id DESC"
        ).fetchall()

def save_message(session_id: int, role: str, content: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages(session_id, role, content, created_at) VALUES(?,?,?,?)",
            (session_id, role, content, datetime.utcnow().isoformat(timespec="seconds"))
        )

def load_messages(session_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE session_id=? ORDER BY id ASC",
            (session_id,)
        ).fetchall()
        return [{"role": r, "content": c} for (r, c) in rows]

def save_insight(session_id: int, meta: dict):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO insights(session_id, glyph, glyph_meaning, goal, steps, question, suggestions, created_at) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (
                session_id,
                meta.get("glyph"),
                meta.get("glyph_meaning"),
                (meta.get("plan") or {}).get("goal"),
                json.dumps((meta.get("plan") or {}).get("steps") or []),
                (meta.get("plan") or {}).get("question"),
                json.dumps(meta.get("suggestions") or []),
                datetime.utcnow().isoformat(timespec="seconds")
            )
        )

def last_insight(session_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT glyph, glyph_meaning, goal, steps, question, suggestions FROM insights "
            "WHERE session_id=? ORDER BY id DESC LIMIT 1",
            (session_id,)
        ).fetchone()
        if not row:
            return None
        glyph, meaning, goal, steps, question, suggestions = row
        return {
            "glyph": glyph,
            "glyph_meaning": meaning,
            "plan": {"goal": goal, "steps": json.loads(steps or "[]"), "question": question},
            "suggestions": json.loads(suggestions or "[]"),
        }

init_db()

# =================== State ===================
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "last_ref_meta" not in st.session_state:
    st.session_state.last_ref_meta = None

# =================== Sidebar ===================
with st.sidebar:
    st.subheader("Session")
    sessions = list_sessions()
    titles = ["— New session —"] + [f"#{sid} • {title}" for (sid, title, _) in sessions]
    selected = st.selectbox("Load a session", titles, index=0)
    if selected != "— New session —":
        idx = titles.index(selected) - 1
        sid, title, _ = sessions[idx]
        st.session_state.session_id = sid
        msgs = load_messages(sid)
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}] + msgs
        st.success(f"Loaded session: {title}")
        li = last_insight(sid)
        if li:
            st.caption(f"Last marker: {li.get('glyph','—')} — {li.get('glyph_meaning','—')}")

    new_title = st.text_input("New session title", value=datetime.now().strftime("REF %Y-%m-%d %H:%M"))
    if st.button("Start"):
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
    st.caption("Sessions persist while the container lives. Redeploy resets storage.")

st.title("REF • Sareth")

# =================== History ===================
for m in st.session_state.messages:
    if m["role"] == "system":
        continue
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])

# =================== Input & Stream ===================
prompt = st.chat_input("Type your message…")
if prompt:
    # Augment the message with light meta (lets the model adapt depth/coaching)
    user_msg = prompt
    if depth_on:
        user_msg += "\n\n[meta: depth=on]"
    user_msg += f"\n[meta: coaching={coaching}]"

    st.session_state.messages.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.session_id:
        save_message(st.session_state.session_id, "user", prompt)

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

        # Parse trailing JSON meta (REF block)
        ref_meta = None
        try:
            last_line = acc.splitlines()[-1].strip()
            if last_line.startswith("{") and last_line.endswith("}"):
                data = json.loads(last_line)
                if "ref" in data and isinstance(data["ref"], dict):
                    ref_meta = data["ref"]
                    # remove JSON from visible text for display/history
                    acc = "\n".join(acc.splitlines()[:-1]).rstrip()
        except Exception:
            pass

        # Show final assistant text
        out.markdown(acc)

        # Guidance panel
        if ref_meta:
            glyph = ref_meta.get("glyph", "")
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
                        st.write("**Next steps:**")
                        for i, s in enumerate(steps[:3], 1):
                            st.write(f"{i}. {s}")
                    if plan.get("question"):
                        st.write(f"**Focusing question:** {plan['question']}")
                    if suggestions:
                        st.write("**Suggestions:**")
                        st.write(" · " + " · ".join(suggestions[:4]))

            # Persist the insight
            if st.session_state.session_id:
                save_insight(st.session_state.session_id, {
                    "glyph": glyph,
                    "glyph_meaning": meaning,
                    "plan": plan,
                    "suggestions": suggestions
                })

        # Save assistant message (text only)
        st.session_state.messages.append({"role": "assistant", "content": acc})
        if st.session_state.session_id:
            save_message(st.session_state.session_id, "assistant", acc)