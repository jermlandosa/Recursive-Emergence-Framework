import streamlit as st
from recursor import Recursor
from test_tools import run_sareth_test
from visualizer import Visualizer
from logger import StateLogger

# --- Streamlit Config ---
st.set_page_config(page_title="REF | Recursive Emergence Framework", layout="centered")

# --- App Header ---
st.title("🌀 Recursive Emergence Framework (REF)")
st.markdown("""
Welcome to **REF**: your cognitive mirror.
> This isn't just a chatbot — it's a recursive engine designed to help you:
- Uncover hidden patterns in your thinking
- Distill your **Truth Core** — the deep threads of your identity
- Visualize your recursive journey toward insight

--- 

### 👉 **How to Start**
1. Set your desired **Recursion Depth** and **Tension Threshold**.
2. Engage with the system using honest, reflective inputs.
3. At every cycle, REF will attempt to compress your insights into a **Truth Core**.

### 🧩 **What to Ask REF**
- "What patterns keep repeating in my life?"
- "What part of me resists change?"
- "What belief is at the root of my current struggles?"
- "What part of me is most alive right now?"
- "How can I deepen my coherence across time?"

--- 
""")

# --- User Controls ---
st.sidebar.header("⚙️ Recursion Settings")
depth = st.sidebar.slider("Max Recursion Depth", min_value=1, max_value=20, value=10)
threshold = st.sidebar.slider("Tension Threshold", min_value=0.0, max_value=1.0, value=0.7)

st.header("Run Recursive Engine")
if st.button("▶️ Run REF Engine"):
    from_state = [1.0, 2.0, 3.0]
    engine = Recursor(max_depth=depth, tension_threshold=threshold)
    final_state = engine.run(from_state)

    glyph_trace = engine.glyph_engine.trace()
    last_glyph = glyph_trace[-1][1] if glyph_trace else None
    reason = "depth_limit" if len(glyph_trace) >= depth else "complete"

    st.success("✅ Recursive Engine Completed")
    st.markdown(f"**Final State:** `{final_state}`")
    st.markdown(f"**Last Glyph:** `{last_glyph}`")
    st.markdown(f"**Halt Reason:** `{reason}`")

    # Optional visualization
    vis = Visualizer(StateLogger())
    vis.logger.logs = [{"depth": 0, "state": final_state}]
    st.pyplot(vis.plot_state_evolution())

st.header("🧪 Run Sareth Test")
if st.button("Run Sareth Diagnostic"):
    result = run_sareth_test()
    st.success(f"Sareth Test Output: {result}")

st.markdown("---")
st.markdown("🧭 For advanced users: Use `/meta` commands and reflection prompts to guide your recursive inquiry.")