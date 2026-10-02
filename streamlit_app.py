import os
import streamlit as st

st.set_page_config(page_title="Sareth • REF", page_icon="✨", layout="wide")

# --- Preflight: ensure key exists (Secrets > OPENAI_API_KEY or env var) ---
def _preflight_openai():
    try:
        _ = os.getenv("OPENAI_API_KEY")
        if not _:
            _ = st.secrets.get("OPENAI_API_KEY", None)
        if not _:
            raise RuntimeError
    except Exception:
        st.error(
            "OpenAI key not found.\n\n"
            "Add **OPENAI_API_KEY** in Streamlit Secrets (Cloud) or set the environment variable locally."
        )
        st.stop()

# Chat state is session-local; the optional legacy ledger is not needed to boot.

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
    st.query_params["page"] = "Recursive_Emergence_Framework"
    st.page_link(
        "pages/Recursive_Emergence_Framework.py",
        label="Click here if not redirected",
        icon="✨",
    )
