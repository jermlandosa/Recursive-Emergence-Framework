import os
import streamlit as st
from openai import OpenAI


def main():
    """
    A cleaned-up Streamlit app for the Recursive Emergence Framework (REF) assistant.

    This version avoids reliance on a separate `openai_client` helper and performs its own
    API key lookup. It checks both Streamlit secrets and environment variables for
    `OPENAI_API_KEY`, displaying a helpful error message if the key is missing. Once a
    client is instantiated, it maintains conversation state in `st.session_state` and
    streams responses back to the user from OpenAI's chat completions endpoint.
    """

    st.set_page_config(page_title="REF • Sareth", page_icon="🔁")

    SYSTEM_PROMPT = (
        "You are Sareth, the REF assistant. Be concise, deep, and precise. "
        "Default to recursive truth checks and avoid fluff."
    )

    # Retrieve the API key from Streamlit secrets or environment variables.
    api_key = st.secrets.get("OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")

    if not api_key:
        st.error(
            "❌ Missing OpenAI API key.\n\n"
            "To run this app you need to provide an API key.\n\n"
            "**Locally**: set an environment variable before running Streamlit, e.g.\n"
            "```
            export OPENAI_API_KEY=\"sk-...\"
            streamlit run ref_sareth_chat.py
            ```\n\n"
            "**On Streamlit Cloud**: go to your app’s Settings → Secrets and add:\n"
            "```toml\n"
            "OPENAI_API_KEY = \"sk-...\"\n"
            "```"
        )
        st.stop()

    # Instantiate the OpenAI client with the retrieved API key.
    client = OpenAI(api_key=api_key)

    # Initialize conversation state with a system message if it doesn't exist yet.
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Display the app title.
    st.title("REF • Sareth")

    # Sidebar controls: choose model and reset the conversation.
    with st.sidebar:
        st.subheader("Settings")
        # Let the user choose the model; default to a lightweight one.
        model = st.text_input("OpenAI model", value="gpt-4o-mini")
        if st.button("Reset chat"):
            st.session_state.messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
            st.rerun()

    # Render the chat history excluding the system prompt.
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        with st.chat_message(
            "user" if message["role"] == "user" else "assistant"
        ):
            st.markdown(message["content"])

    # Input box for the user.
    user_text = st.chat_input("Type your message…")
    if user_text:
        # Append the user's message to the conversation history.
        st.session_state.messages.append(
            {"role": "user", "content": user_text}
        )

        # Immediately display the user's message.
        with st.chat_message("user"):
            st.markdown(user_text)

        # Create a placeholder for the assistant's streaming reply.
        with st.chat_message("assistant"):
            out_placeholder = st.empty()
            accumulated_response = ""

            # Stream the assistant's response using OpenAI's API.
            stream = client.chat.completions.create(
                model=model,
                temperature=0.3,
                stream=True,
                messages=st.session_state.messages,
            )

            # Iterate over the streamed chunks and update the output.
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    accumulated_response += delta
                    out_placeholder.markdown(accumulated_response + "▌")

            # Once complete, store the full assistant response.
            st.session_state.messages.append(
                {"role": "assistant", "content": accumulated_response}
            )


if __name__ == "__main__":
    main()
