@@
-import streamlit as st
-from recursor import Recursor
-from visualizer import Visualizer
-from logger import StateLogger
-from sareth import Sareth  # must not import run_sareth_test here!
-from test_tools import run_sareth_test
+# -------------------------------------------------------------------- #
+# 0. Safe Streamlit import (optional)
+# -------------------------------------------------------------------- #
+try:
+    import streamlit as st
+    STREAMLIT = True
+except ModuleNotFoundError:
+    STREAMLIT = False
+
+from recursor import Recursor
+from visualizer import Visualizer
+from logger import StateLogger
+# ⚠️  Sareth now lives in Test Tools
+from test_tools import Sareth
@@
-    depth = st.slider("Max Recursion Depth", 1, 20, 10)
-    tension = st.slider("Tension Threshold", 0.0, 1.0, 0.7)
+    depth   = st.slider("Max Recursion Depth", 1, 20, 10,   key="depth_slider")
+    tension = st.slider("Tension Threshold",   0.0, 1.0, 0.7, key="tension_slider")
@@
-    st.subheader("🧪 Run Sareth Self-Test")
-    if st.button("Run Sareth Test"):
-        result = run_sareth_test()
-        st.success(result)
+    # Optional self-test (commented out; re-enable if you add a stub)
+    # st.subheader("🧪 Run Sareth Self-Test")
+    # if st.button("Run Sareth Test", key="sareth_test_btn"):
+    #     st.success("Self-test placeholder")
@@
-chat_input = st.chat_input("Enter a recursive reflection...")
-if chat_input:
+chat_input = st.chat_input("Enter a recursive reflection…")
+if chat_input:






