import os
import streamlit as st
from rve.ledger import get_session, get_or_create_user

st.set_page_config(page_title="Sareth • REF", page_icon="✨", layout="wide")

# --- Preflight: ensure key exists (Secrets > OPENAI_API_KEY or env var) ---
def _preflight_openai():
    try:
        _ = st.secrets.get("OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
        if not _:
            raise RuntimeError
    except Exception:
        st.error(
            "OpenAI key not found.\n\n"
            "Add **OPENAI_API_KEY** in Streamlit Secrets (Cloud) or set the environment variable locally."
        )
        st.stop()

# Auth bootstrap for guest
AUTH_DISABLED = os.getenv("AUTH_DISABLED", "true").lower() in ("1", "true", "yes")
if AUTH_DISABLED and "user_id" not in st.session_state:
    sess = get_session()
    guest = get_or_create_user(sess, "guest@sareth.app", "guest")
    st.session_state["user_id"] = guest.id
    st.session_state["user_email"] = guest.email
    st.session_state["authentication_status"] = True
    st.session_state["name"] = "Guest"
    st.session_state["username"] = "guest"
    st.session_state["auth_ok"] = True

# Minimal responsive CSS
st.markdown(
    """
    <style>
    @media (max-width: 640px){
      [data-testid="stSidebar"] { display: none; }
      [data-testid="stHeader"] { height: 3rem; }
      .block-container { padding-top: 1rem; }
    }
    [data-testid="stSidebarNav"] ul { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Fail early if no key
_preflight_openai()

# Go straight to the live agent
try:
    st.switch_page("pages/Recursive_Emergence_Framework.py")
except Exception:
    st.markdown("### Redirecting to Recursive Emergence Framework…")
    st.experimental_set_query_params(page="Recursive_Emergence_Framework")
    st.page_link(
        "pages/Recursive_Emergence_Framework.py",
        label="Click here if not redirected",
        icon="✨",
    )
