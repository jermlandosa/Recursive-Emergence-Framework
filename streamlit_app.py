"""Sareth Streamlit entry point.

Do not import OpenAI helpers before showing the page. Streamlit Cloud can
briefly serve mismatched revisions during an update; the entry point should
still render and provide a useful secret-configuration message.
"""
import os
from collections.abc import Mapping

import streamlit as st

st.set_page_config(page_title="Sareth • REF", page_icon="✨", layout="wide")


def _preflight_openai():
    """Check only that the secret exists; validate it through the chat UI."""
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        try:
            secrets = st.secrets
            key = str(secrets.get("OPENAI_API_KEY") or "").strip()
            if not key:
                for section_name in ("openai", "serith"):
                    section = secrets.get(section_name, {})
                    if isinstance(section, Mapping):
                        key = str(section.get("api_key") or "").strip()
                        if key:
                            break
        except FileNotFoundError:
            pass
    if not key:
        st.error("No OpenAI API key configured for Sareth.")
        st.info("Open Streamlit Cloud → Manage app → Settings → Secrets and add OPENAI_API_KEY. Restart the app after saving. Never put your key in GitHub.")
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
