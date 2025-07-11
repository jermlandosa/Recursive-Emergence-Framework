import streamlit as st
from sareth import run_recursive_engine

st.title("Recursive Emergence: Sareth Engine")

state_str = st.text_input("Enter State (comma-separated)", "1.0, 2.0, 3.0")
if st.button("Run Engine"):
    try:
        state = [float(x.strip()) for x in state_str.split(",")]
        result = run_recursive_engine(state)
        st.json(result)
    except Exception as e:
        st.error(f"Error: {e}")
