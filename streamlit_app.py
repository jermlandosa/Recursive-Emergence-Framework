import streamlit as st
from main import run_recursive_engine  # Assuming main.py has a callable function

st.title("Recursive Emergence Framework UI")

depth = st.slider("Initial Depth", 0, 10, 0)
tension = st.slider("Tension Threshold", 0.0, 1.0, 0.4)

if st.button("Run Recursive Engine"):
    state, glyph, halt_reason = run_recursive_engine(depth=depth, threshold=tension)
    st.write(f"State: {state}")
    st.write(f"Glyph: {glyph}")
    st.write(f"Halt Reason: {halt_reason}")
