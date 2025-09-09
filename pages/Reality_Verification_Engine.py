import streamlit as st
import matplotlib.pyplot as plt

from rve.ledger import get_session, add_claim, append_drift, Claim


st.set_page_config(page_title="Reality Verification Engine", layout="wide")


def drift_chart(history):
    xs = list(range(len(history)))
    ys = [h.drift for h in history]
    fig, ax = plt.subplots()
    ax.plot(xs, ys, marker="o")
    ax.set_xlabel("Checkpoint")
    ax.set_ylabel("Drift")
    ax.set_title("Drift Over Time")
    st.pyplot(fig)


def page():
    st.markdown("# Reality Verification Engine")
    st.caption(
        "REF-integrated page to verify claims, track provenance, and visualize drift."
    )

    sess = get_session()

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
            claim = add_claim(sess, text.strip(), volatility, prov_fields, 6, indep)
            st.success(f"Created {claim.claim_id}")

    st.subheader("Active Claims")
    claims = sess.query(Claim).order_by(Claim.created_at.desc()).all()
    if not claims:
        st.info("No claims yet.")
    for c in claims:
        st.markdown(f"### {c.claim_id}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Confidence", f"{int(c.confidence_index * 100)}%")
        col2.metric("Drift", f"{c.drift_score:.1f}")
        col3.metric("Provenance", f"{int(c.provenance_completeness * 100)}%")
        col4.metric("Independence", f"{c.independence_score} / 3")
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
                append_drift(sess, c, new_val)
                st.experimental_rerun()
        st.divider()


if __name__ == "__main__":
    page()

