"""Streamlit app for the Recursive Emergence Framework.

This refactored version focuses on safe startup and graceful degradation so the
app can boot even when optional dependencies, secrets, or engines are missing.
"""

from __future__ import annotations

import os
import sys
import traceback
from typing import Callable, Optional

import streamlit as st


def boot_panel() -> None:
    """Render diagnostic information in the sidebar for safe boot."""
    with st.sidebar:
        st.header("Boot Info")
        st.markdown(f"**Python:** {sys.version.split()[0]}")
        cwd = os.getcwd()
        st.markdown(f"**CWD:** `{cwd}`")
        try:
            st.markdown("**Files:**")
            st.write(sorted(os.listdir(cwd)))
        except Exception as exc:  # pragma: no cover - extremely unlikely
            st.warning(f"Unable to list directory contents: {exc}")


def load_api_keys() -> Optional[str]:
    """Retrieve the OpenAI API key from Streamlit secrets or the environment."""
    key = None
    try:
        # Secrets may contain either a flat key or nested under "openai"
        key = st.secrets.get("OPENAI_API_KEY") or st.secrets.get("openai", {}).get(
            "api_key"
        )
    except Exception:
        # Accessing st.secrets outside Streamlit or without config can raise
        key = None

    key = key or os.environ.get("OPENAI_API_KEY")
    if key:
        os.environ.setdefault("OPENAI_API_KEY", key)
    else:
        st.sidebar.warning("OPENAI_API_KEY not found – running in demo mode.")
    return key


def resolve_engine() -> Optional[Callable[[str], str]]:
    """Attempt to import a `run_ref` function from available modules."""
    root = os.path.dirname(__file__)
    if root not in sys.path:
        sys.path.append(root)

    candidates = [("ref_engine", "run_ref"), ("sareth", "main")]
    for module_name, attr in candidates:
        try:
            module = __import__(module_name, fromlist=[attr])
            return getattr(module, attr)
        except Exception:
            continue

    st.sidebar.error("REF engine import failed; input will be echoed back.")
    return None


def handle_prompt(prompt: str, runner: Optional[Callable[[str], str]]) -> str:
    """Run the REF engine or echo the prompt if unavailable."""
    if not runner:
        return prompt
    try:
        return runner(prompt)
    except Exception:
        st.error("REF engine error:")
        st.exception(traceback.format_exc())
        return prompt


def main() -> None:
    st.set_page_config(
        page_title="Sareth | Recursive Reflection", layout="wide", initial_sidebar_state="expanded"
    )
    boot_panel()
    load_api_keys()
    run_ref = resolve_engine()

    st.title("Sareth Streamlit Demo")
    user_prompt = st.text_area("Enter your prompt")

    if st.button("Submit"):
        if not user_prompt.strip():
            st.warning("Please enter a prompt.")
        else:
            output = handle_prompt(user_prompt, run_ref)
            st.write(output)


if __name__ == "__main__":
    main()

