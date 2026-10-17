import streamlit as st
from rve.openai_client import api_error_message, get_api_key

st.set_page_config(page_title="Sareth • REF", page_icon="✨", layout="wide")

# --- Preflight: secrets are checked server-side; never display secret values. ---
def _preflight_openai():
    try:
        get_api_key()
    except RuntimeError as exc:
        st.error(api_error_message(exc))
        st.info("In Streamlit Cloud, open the app's settings and add OPENAI_API_KEY to Secrets. The ChatGPT subscription and API billing are separate.")
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
