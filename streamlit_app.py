import os
import streamlit as st
from rve.ledger import get_session, get_or_create_user

# Configure the main entry page for the Recursive Emergence Framework (REF)
st.set_page_config(page_title="Sareth • REF", page_icon="✨", layout="wide")

# When authentication is disabled, ensure there is a default guest user in session state
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

# Inject responsive CSS and hide the sidebar navigation on the root page
st.markdown(
    """
    <style>
    @media (max-width: 640px){
      [data-testid="stSidebar"] { display: none; }
      [data-testid="stHeader"] { height: 3rem; }
      .block-container { padding-top: 1rem; }
    }
    @media (min-width: 641px) and (max-width: 1024px){
      [data-testid="stSidebar"] { width: 260px; }
    }
    /* Hide the sidebar navigation items so only the target page appears */
    [data-testid="stSidebarNav"] ul {
      display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    # Redirect immediately to the REF page in the pages directory
    st.switch_page("pages/Recursive_Emergence_Framework.py")
except Exception:
    # Fallback link if automatic redirection fails
    st.markdown("### Redirecting to Recursive Emergence Framework…")
    st.experimental_set_query_params(page="Recursive_Emergence_Framework")
    st.page_link(
        "pages/Recursive_Emergence_Framework.py",
        label="Click here if not redirected",
        icon="✨",
    )