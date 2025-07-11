import streamlit as st
import matplotlib.pyplot as plt
import json
from main import run_recursive_engine  # your core function

st.set_page_config(page_title="Sareth Interface", layout="centered")

st.title("🌀 Sareth Interface Portal")

# Session state
if "glyph_log" not in st.session_state:
    st.session_state.glyph_log = []

# Depth slider
depth = st.slider("Recursion Depth", 1, 10, 3)

# Prompt input (optional enhancement)
prompt = st.text_input("Optional prompt input (not yet wired)")

# Run engine
if st.button("Run Sareth"):
    result = run_recursive_engine(depth=depth)
    glyph_id = result.get("glyph", "Unknown")
    state = result.get("state", [])
    tension = result.get("tension", None)
    
    # Save to log
    st.session_state.glyph_log.append({
        "glyph": glyph_id,
        "state": state,
        "tension": tension
    })

# Log display
if st.session_state.glyph_log:
    st.subheader("🧬 Glyph Log")
    for entry in reversed(st.session_state.glyph_log):
        st.success(f"Glyph: {entry['glyph']} | Tension: {entry['tension']}")
        fig, ax = plt.subplots()
        ax.plot(entry["state"])
        ax.set_title("State Vector")
        st.pyplot(fig)

    # Export button
    st.download_button("📁 Export Glyph Log", json.dumps(st.session_state.glyph_log, indent=2), file_name="glyph_log.json")

