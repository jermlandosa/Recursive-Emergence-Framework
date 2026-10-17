"""OpenAI client configuration and safe, actionable API diagnostics.

Credentials stay server-side. Never include API keys or raw provider errors
in Streamlit's public UI.
"""
import os
from collections.abc import Mapping

import streamlit as st
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    OpenAI,
    PermissionDeniedError,
    RateLimitError,
)


def get_api_key() -> str:
    """Find the key in the environment or the documented Streamlit secrets formats."""
    value = os.getenv("OPENAI_API_KEY")
    if isinstance(value, str) and value.strip():
        return value.strip()

    try:
        secrets = st.secrets
        value = secrets.get("OPENAI_API_KEY")
        if isinstance(value, str) and value.strip():
            return value.strip()
        for section_name in ("openai", "serith"):
            section = secrets.get(section_name, {})
            if isinstance(section, Mapping):
                for name in ("api_key", "OPENAI_API_KEY"):
                    value = section.get(name)
                    if isinstance(value, str) and value.strip():
                        return value.strip()
    except FileNotFoundError:
        pass

    raise RuntimeError(
        "Missing OpenAI API key. Add OPENAI_API_KEY to this app's "
        "Streamlit Cloud Settings → Secrets, then restart the app."
    )


def openai_client() -> OpenAI:
    # Construct on demand so a rotated key is not stranded in a cached client.
    return OpenAI(api_key=get_api_key(), timeout=45.0, max_retries=0)


_QUOTA_CODES = {
    "insufficient_quota",
    "credit_balance_exhausted",
    "organization_spend_limit_exceeded",
    "project_spend_limit_exceeded",
    "organization_usage_limit_exceeded",
}


def api_error_message(error: Exception) -> str:
    """Return an actionable category without revealing keys or provider payloads."""
    if isinstance(error, RuntimeError) and str(error).startswith("Missing OpenAI API key."):
        return str(error)
    if isinstance(error, AuthenticationError):
        return "OpenAI rejected the API key (401). Update OPENAI_API_KEY in Streamlit Secrets and restart the app."
    if isinstance(error, PermissionDeniedError):
        return "OpenAI denied this key or project's request (403). Check project permissions and access to the selected model."
    if isinstance(error, NotFoundError):
        return "OpenAI could not find or authorize the selected model (404). Try another listed model and check project access."
    if isinstance(error, RateLimitError):
        code = getattr(error, "code", None)
        if code in _QUOTA_CODES:
            return "OpenAI API credits or a usage/spend limit were reached (429). Check API billing, credits, and project limits."
        return "OpenAI returned a rate/quota limit (429). Check API usage, credits, and rate limits before retrying."
    if isinstance(error, BadRequestError):
        return "OpenAI rejected the request (400). Check that the selected model accepts the request parameters."
    if isinstance(error, APITimeoutError):
        return "The OpenAI request timed out. Retry after checking network and provider status."
    if isinstance(error, APIConnectionError):
        return "Sareth could not connect to OpenAI. Check connectivity and service status."
    if isinstance(error, APIStatusError):
        return f"OpenAI returned HTTP {error.status_code}. Check the model, API project, and service status."
    return "Sareth encountered an unexpected error. Check the Streamlit app logs for the error type; do not share API keys."
