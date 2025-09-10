import os
import streamlit as st
from rve.ledger import get_session, get_or_create_user

st.set_page_config(page_title="Sareth • RVE", page_icon="✨", layout="wide")

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
</style>
""",
    unsafe_allow_html=True,
)

try:
    st.switch_page("pages/Reality_Verification_Engine.py")
except Exception:
    st.markdown("### Redirecting to Reality Verification Engine…")
    st.experimental_set_query_params(page="Reality_Verification_Engine")
    st.page_link(
        "pages/Reality_Verification_Engine.py",
        label="Click here if not redirected",
        icon="✨",
    )
