import streamlit as st
import matplotlib.pyplot as plt

from rve.ledger import get_session, add_claim, append_drift, Claim, User
from ._auth import auth_gate, get_current_user


st.set_page_config(page_title="Reality Verification Engine", layout="wide")

LABELS = {
    "drift": "Story change",
    "provenance": "Evidence strength",
    "confidence": "Confidence",
    "independence": "Unique sources",
}
TOOLTIPS = {
    "drift": "How much the story has shifted from its original evidence (lower is better).",
    "provenance": "How well this claim is backed by timestamps, methods, and artifacts.",
    "confidence": "Overall how solid this looks, given evidence and story change.",
    "independence": "How many independent confirmations support this.",
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
    steps = []
    pc = claim.provenance_completeness
    ind = claim.independence_score
    drift = claim.drift_score
    conf = claim.confidence_index

    steps.append(
        f"Evidence strength (provenance completeness) = {int(pc*100)}% from checklist items filled / total."
    )
    steps.append(f"Unique sources = {ind} out of 3.")
    steps.append(
        "Story change (drift): baseline 3.0, minus 2.0×evidence, minus 0.4×sources, clamped to [0,5]."
    )
    steps.append(f"→ Drift = {drift:.2f}")
    steps.append(
        "Confidence: 60% weight on evidence + 40% on sources, attenuated by drift/10."
    )
    steps.append(f"→ Confidence = {int(conf*100)}%")

    integrity = []
    integrity.append("• Timestamp present?" + (" ✅" if pc >= 0.17 else " ⚠️"))
    integrity.append("• Method documented?" + (" ✅" if pc >= 0.34 else " ⚠️"))
    integrity.append("• Hash/immutability?" + (" ✅" if pc >= 0.50 else " ⚠️"))
    integrity.append("• Chain-of-custody listed?" + (" ✅" if pc >= 0.67 else " ⚠️"))
    integrity.append("• Reproducible steps?" + (" ✅" if pc >= 0.84 else " ⚠️"))

    return steps, integrity


def page():
    st.markdown("# Reality Verification Engine")
    st.caption(
        "Check if a claim stays aligned with reality. RVE shows how much the story changed, how strong the evidence is, and how confident you can be."
    )

    st.markdown("## What RVE does for you")
    st.write("RVE helps you check whether a claim stays aligned with reality. It shows:")
    st.write("• Story change — how much the story has shifted from its original evidence.")
    st.write("• Evidence strength — how well the claim is backed up (timestamps, methods, artifacts).")
    st.write("• Unique sources — how many independent confirmations you have.")
    st.write("• Confidence — how solid this looks overall.")

    user_email = get_current_user()
    if not user_email:
        auth_gate()
        st.stop()

    with st.expander("See an example first (recommended)"):
        st.write("**Example claim:** “Ocean temperatures are rising.”")
        st.write("Story change: **1.1 (low)**, Evidence strength: **80%**, Unique sources: **3/3**, Confidence: **92%**.")
        st.write("Why: multiple independent datasets with timestamps & methods align within expected variance.")

    sess = get_session()
    user = sess.query(User).filter_by(email=user_email).one()

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
            steps, integrity = explain_interpretation(c)
            st.markdown("**Calculation path**")
            for s in steps:
                st.write("- " + s)
            st.markdown("**Integrity checks**")
            for ic in integrity:
                st.write(ic)
            st.caption("These are transparent, deterministic calculations; no hidden model reasoning.")
        st.divider()


if __name__ == "__main__":
    page()

