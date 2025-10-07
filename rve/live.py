from typing import List, Dict, Any, Generator
import streamlit as st
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from rve.openai_client import openai_client

SYSTEM_BASELINE = (
    "You are Sareth inside the Recursive Emergence Framework (REF). "
    "Think clearly, be concise, and map signals to glyphs when useful."
)


def ensure_chat_state():
    st.session_state.setdefault("chat", [])  # type: List[Dict[str, str]]
    st.session_state.setdefault("glyph_trace", [])  # type: List[Dict[str, Any]]
    st.session_state.setdefault("last_response", "")
    st.session_state.setdefault("system_prompt", SYSTEM_BASELINE)


def push_user(msg: str):
    st.session_state.chat.append({"role": "user", "content": msg})


def push_assistant(msg: str):
    st.session_state.chat.append({"role": "assistant", "content": msg})


def messages_for_llm() -> List[Dict[str, str]]:
    return [{"role": "system", "content": st.session_state.system_prompt}] + st.session_state.chat


def stream_chat(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
) -> Generator[str, None, None]:
    client = openai_client()
    stream = client.chat.completions.create(
        model=model, temperature=temperature, stream=True, messages=messages
    )
    for chunk in stream:  # type: ChatCompletionChunk
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
