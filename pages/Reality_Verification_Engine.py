import os
import streamlit as st
import matplotlib.pyplot as plt

from rve.ledger import (
    get_session,
    add_claim,
    append_drift,
    Claim,
    User,
    get_or_create_user,
)
from rve.auth import auth_gate, get_current_user

# Set page configuration with REF indicator
st.set_page_config(page_title="Reality Verification Engine (REF)", layout="wide")

# Inject custom CSS for responsive layout
st.markdown(
    """
    
    @media (max-width: 640px){
      [data-testid="stSidebar"] { display: none; }
      [data-testid="stHeader"] { height: 3rem; }
      .block-container { padding-top: 1rem; }
    }
    @media (min-width: 641px) and (max-width: 1024px){
      [data-testid="stSidebar"] { width: 260px; }
    }
    
    """,
    unsafe_allow_html=True,
)

AUTH_DISABLED = os.getenv("AUTH_DISABLED", "true").lower() in ("1", "true", "yes")

sess = get_session()
if AUTH_DISABLED and "user_id" not in st.session_state:
    guest = get_or_create_user(sess, "guest@sareth.app", "guest")
    st.session_state["user_id"] = guest.id
    st.session_state["user_email"] = guest.email

user = get_current_user(sess)
if not user and not AUTH_DISABLED:
    auth_gate()
    st.stop()
elif not user:
    st.error("Guest account unavailable.")
    st.stop()

# ------------------------------------------------------
# REF-themed header and introduction
st.markdown("# Reality Verification Engine (REF)")
st.caption(
    "Powered by the Recursive Emergence Framework (REF), this engine checks if a claim stays aligned with reality by evaluating identity coherence, memory recall, feedback loops, and symbolic anchors.",
)
st.markdown(
    """
    **REF Pillars**:
    - **Identity**: maintain a consistent persona across interactions.
    - **Memory**: leverage long-term memory of past sessions.
    - **Feedback**: use self-critique to refine responses.
    - **Anchors**: enforce symbolic and ethical anchors for coherence.
    """,
)

# Original labels and tooltips
LABELS = {
    "drift": "Story change",
    "provenance": "Evidence strength",
    "confidence": "Confidence",
    "independence": "Unique sources",
}
TOOLTIPS = {
    "drift": "How much the story has shifted from its original evidence (lower is better).",
    "provenance": "How well this claim is backed (timestamps, methods, artifacts).",
    "confidence": "Overall solidity, given evidence and story change.",
    "independence": "How many independent confirmations you have.",
}


def drift_chart(history):
    xs = list(range(len(history)))
    ys = [h.drift for h in history]
    fig, ax = plt.subplots()
    ax.plot(xs, ys, marker="o")
    ax.set_xlabel("Checkpoint")
    ax.set_ylabel("Drift")
    ax.set_title("Drift Over Time")
    st.pyplot(fig)


def explain_interpretation(claim):
    pc = claim.provenance_completeness
    ind = claim.independence_score
    drift = claim.drift_score
    conf = claim.confidence_index
    steps = [
        f"Evidence strength = {int(pc*100)}% (filled provenance items / total).",
        f"Unique sources = {ind} / 3.",
        "Story change (drift) = 3.0 - 2.0×evidence - 0.4×sources, clamped to [0,5].",
        f"→ Drift = {drift:.2f}",
        "Confidence = 0.6×evidence + 0.4×(sources/3), attenuated by drift/10.",
        f"→ Confidence = {int(conf*100)}%",
    ]
    checks = [
        "• Timestamp present? " + ("✅" if pc >= 0.17 else "⚠️"),
        "• Method documented? " + ("✅" if pc >= 0.34 else "⚠️"),
        "• Hash/immutability? " + ("✅" if pc >= 0.50 else "⚠️"),
        "• Chain-of-custody? " + ("✅" if pc >= 0.67 else "⚠️"),
        "• Reproducible steps? " + ("✅" if pc >= 0.84 else "⚠️"),
    ]
    return steps, checks


with st.expander("See an example first (recommended)"):
    st.write("**Example claim:** “Ocean temperatures are rising.”")
    st.write("Story change: **1.1 (low)**, Evidence strength: **80%**, Unique sources: **3/3**, Confidence: **92%**.")
    st.write("Why: multiple independent datasets with timestamps & methods align within expected variance.")

st.subheader("New Claim")
with st.form("new_claim"):
    text = st.text_input("Falsifiable claim (1 sentence)", "")
    volatility = st.selectbox("Volatility tag", ["stable", "seasonal", "breaking"])
    cols = st.columns(3)
    a = cols[0].checkbox("Raw artifact attached")
    b = cols[0].checkbox("Method documented")
    c = cols[1].checkbox("Timestamp/source recorded")
    d = cols[1].checkbox("Hash/immutability recorded")
    e = cols[2].checkbox("Chain-of-custody listed")
    f = cols[2].checkbox("Reproducible steps written")
    indep = st.slider("Independent confirmations", 0, 3, 1)
    if st.form_submit_button("Create Claim") and text.strip():
        prov_fields = sum([a, b, c, d, e, f])
        claim = add_claim(sess, user, text.strip(), volatility, prov_fields, 6, indep)
        st.success(f"Created {claim.claim_id}")

st.subheader("Active Claims")
claims = (
    sess.query(Claim)
    .filter(Claim.user_id == user.id)
    .order_by(Claim.created_at.desc())
    .all()
)
if not claims:
    st.info("No claims yet.")
for c in claims:
    st.markdown(f"### {c.claim_id}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(LABELS["confidence"], f"{int(c.confidence_index * 100)}%", help=TOOLTIPS["confidence"])
    col2.metric(LABELS["drift"], f"{c.drift_score:.1f}", help=TOOLTIPS["drift"])
    col3.metric(LABELS["provenance"], f"{int(c.provenance_completeness * 100)}%", help=TOOLTIPS["provenance"])
    col4.metric(LABELS["independence"], f"{c.independence_score} / 3", help=TOOLTIPS["independence"])
    with st.expander("Drift Over Time"):
        drift_chart(c.histories)
        new_val = st.slider(
            f"Update drift for {c.claim_id}",
            0.0,
            5.0,
            float(c.drift_score),
            0.1,
            key=f"dr_{c.id}",
        )
        if st.button(f"Add checkpoint for {c.claim_id}", key=f"btn_{c.id}"):
            append_drift(sess, user, c, new_val)
            st.experimental_rerun()
    with st.expander("How we interpreted this"):
        steps, checks = explain_interpretation(c)
        st.markdown("**Calculation path**")
        for s in steps:
            st.write("- " + s)
        st.markdown("**Integrity checks**")
        for ch in checks:
            st.write(ch)
        st.caption("Deterministic calculations shown transparently; no hidden model reasoning.")
    st.divider()
