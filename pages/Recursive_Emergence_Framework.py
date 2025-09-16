import os
import streamlit as st
import json

try:
    import openai  # type: ignore
except ImportError:
    openai = None  # Avoid breaking local dev if openai is unavailable

# Configure the page
st.set_page_config(
    page_title="Recursive Emergence Framework (REF)",
    layout="wide",
)

# Optionally hide the default Streamlit header in the sidebar
st.markdown(
    """
    <style>
    /* Hide the Streamlit app branding in the sidebar */
    [data-testid="stSidebar"] > div:nth-child(1) {
        display: none;
    }
    /* Hide the default sidebar navigation so only this page is visible */
    [data-testid="stSidebarNav"] ul {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and introduction
st.markdown("# Recursive Emergence Framework (REF)")
st.caption("A cognitive‑symbolic architecture for reflexive LLM agents.")

# Overview section
st.markdown(
    """
    ## Overview

    The **Recursive Emergence Framework** (REF) couples a persistent identity and long‑term memory with explicit self‑critique and symbolic anchoring.

    Four key components drive REF:

    - **Identity** – a consistent persona across turns, including traits, roles, style, and moral guidelines.
    - **Memory** – episodic and semantic memory built up from past interactions.
    - **Feedback** – a critic module that scores and comments on drafts, helping the agent refine its responses.
    - **Anchors** – symbolic and ethical rules (no‑contradiction, var‑consistency, no‑harm, privacy) that enforce coherence.

    These elements interact in a **closed loop** that runs at every conversational step. Without retraining the model’s weights, REF produces adaptive, self‑modifying behaviour by iterating through this loop.
    """,
)

# Pseudocode for the REF loop
st.markdown("## REF Loop (pseudocode)")
st.code(
    """
state = {identity, anchors, memory}
while turn:
    # Retrieve past context and build prompt
    ctx = retrieve(memory, user_query) + identity + anchors
    # Generate a draft using the underlying LLM
    draft = LLM(ctx, user_query)
    # Let the critic evaluate the draft against anchors and goals
    feedback = Critic(draft, anchors, goals)
    # Update memory with the turn and feedback
    memory = update(memory, summarize(turn, feedback))
    # Reconcile anchors if contradictions are found
    anchors = reconcile(anchors, contradictions(draft, memory))
    # Revise the draft based on feedback and anchors
    final = revise(draft, feedback, anchors)
    return final
    """,
    language="python",
)

# Data contract examples
st.markdown("## Data Contracts")
with st.expander("Identity schema"):
    st.code(
        json.dumps(
            {
                "traits": ["patient", "truth‑seeking"],
                "roles": ["research_assistant"],
                "style": {"tone": "concise"},
            },
            indent=2,
        ),
        language="json",
    )
with st.expander("Memory schema"):
    st.code(
        json.dumps(
            {
                "episodes": [
                    {"t": "2025-09-15", "q": "...", "a": "...", "outcome": "success"}
                ],
                "summaries": [
                    {"t": "2025-09-15", "insight": "prefers diagrams"}
                ],
            },
            indent=2,
        ),
        language="json",
    )
with st.expander("Anchors schema"):
    st.code(
        json.dumps(
            {
                "logic": ["no-contradiction", "var-consistency"],
                "ethics": ["no-harm", "privacy"],
                "session_facts": ["X implies Y"],
                "jargon": {"REF": "Recursive Emergence Framework"},
            },
            indent=2,
        ),
        language="json",
    )
with st.expander("Feedback record schema"):
    st.code(
        json.dumps(
            {
                "scores": {"correctness": 0.7, "coherence": 0.9},
                "notes": ["tone drifted from 'patient'"],
                "actions": ["reinforce_trait:patient", "add_anchor:term('REF')"],
            },
            indent=2,
        ),
        language="json",
    )

# Live agent interaction
st.markdown("## Talk to the REF agent")

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Input box for user question
task = st.text_input("Ask the REF agent a question:", "")

if st.button("Send") and task:
    # Append user message to session state
    st.session_state['messages'].append({"role": "user", "content": task})

    # Define identity for the system prompt
    identity = {
        "traits": ["patient", "truth‑seeking"],
        "roles": ["research_assistant"],
        "style": {"tone": "concise"},
    }
    system_prompt = (
        "You are a Recursive Emergence Framework (REF) agent. "
        "Your identity traits are {traits}, and your roles are {roles}. "
        "Respond truthfully, concisely, and maintain coherence across turns. "
        "If contradictions arise, resolve them based on your anchors: no-contradiction, var-consistency, no-harm, privacy. "
        "Use your memory to recall previous turns."
    ).format(traits=", ".join(identity["traits"]), roles=", ".join(identity["roles"]))

    messages = []
    # Append system message only once, at the beginning
    if not any(m["role"] == "system" for m in st.session_state['messages']):
        messages.append({"role": "system", "content": system_prompt})
    # Add past messages
    messages += st.session_state['messages']

    if openai is None:
        st.error("OpenAI library is not available. Cannot call the agent.")
    else:
        # Set API key from environment
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
            )
            answer = response.choices[0].message.content
            st.session_state['messages'].append({"role": "assistant", "content": answer})
            st.write(f"**Assistant:** {answer}")
        except Exception as e:
            st.error(f"Agent call failed: {e}")

# Footer
st.markdown(
    """
    ***Note:*** This page implements a basic REF agent using the OpenAI API. Make sure you have set your 'OPENAI_API_KEY' in the environment for it to work.
    """
)
