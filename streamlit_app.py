# streamlit_app.py
import streamlit as st
from main import run_recursive_engine

st.set_page_config(page_title="Sareth UI", layout="centered")
st.title("🌀 Recursive Emergence Framework")

depth = st.slider("Max Recursion Depth", 1, 10, 5)
tension = st.slider("Tension Threshold", 0.0, 1.0, 0.4)

if st.button("Run Sareth Engine"):
    state, glyph, halt_reason = run_recursive_engine(depth=depth, threshold=tension)
    st.success("Run Complete.")
    st.markdown(f"**🧠 Final State:** `{state}`")
    st.markdown(f"**🔣 Glyph ID:** `{glyph}`")
    st.markdown(f"**⛔ Halt Reason:** `{halt_reason}`")

