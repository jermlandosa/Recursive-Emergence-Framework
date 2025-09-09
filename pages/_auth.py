import streamlit as st
from rve.ledger import get_session, get_or_create_user, User


def get_current_user():
    if "user_email" in st.session_state:
        return st.session_state["user_email"]
    return None


def auth_gate():
    st.markdown("### Sign in")
    email = st.text_input("Email")
    pw = st.text_input("Password", type="password")
    if st.button("Sign in / Create account"):
        sess = get_session()
        u = get_or_create_user(sess, email, pw)
        st.session_state["user_email"] = u.email
        st.session_state["user_id"] = u.id
        st.experimental_rerun()
