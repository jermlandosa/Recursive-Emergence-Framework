import streamlit as st
from rve.ledger import get_session, get_or_create_user, User


def get_current_user(sess=None) -> User | None:
    uid = st.session_state.get("user_id")
    if not uid:
        return None
    sess = sess or get_session()
    return sess.query(User).get(uid)


def auth_gate():
    st.markdown("### Sign in")
    email = st.text_input("Email")
    pw = st.text_input("Password", type="password")
    if st.button("Sign in / Create account") and email and pw:
        sess = get_session()
        u = get_or_create_user(sess, email.strip(), pw)
        st.session_state["user_email"] = u.email
        st.session_state["user_id"] = u.id
        st.experimental_rerun()
