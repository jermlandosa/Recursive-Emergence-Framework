import os
import streamlit as st
from openai import OpenAI


@st.cache_resource
def openai_client() -> OpenAI:
    api_key = st.secrets.get("OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing OpenAI API key. Set st.secrets['OPENAI_API_KEY'] or OPENAI_API_KEY env var."
        )
    return OpenAI(api_key=api_key)
