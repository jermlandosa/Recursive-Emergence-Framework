"""Offline tests for Sareth API configuration and public-safe diagnostics."""
from types import SimpleNamespace

import pytest

from rve import openai_client as module


def test_environment_key_takes_precedence(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "  sk-env-example  ")
    monkeypatch.setattr(module.st, "secrets", {"OPENAI_API_KEY": "sk-other-example"})
    assert module.get_api_key() == "sk-env-example"


@pytest.mark.parametrize("secrets", [
    {"OPENAI_API_KEY": "sk-root-example"},
    {"openai": {"api_key": "sk-nested-example"}},
    {"serith": {"api_key": "sk-legacy-example"}},
])
def test_secrets_formats(monkeypatch, secrets):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(module.st, "secrets", secrets)
    assert module.get_api_key().startswith("sk-")


def test_blank_environment_falls_back_to_secrets(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "  ")
    monkeypatch.setattr(module.st, "secrets", {"OPENAI_API_KEY": "sk-streamlit-example"})
    assert module.get_api_key() == "sk-streamlit-example"


def test_missing_key_has_actionable_error(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(module.st, "secrets", {})
    with pytest.raises(RuntimeError, match="Streamlit Cloud"):
        module.get_api_key()


def test_client_not_cached_after_key_rotation(monkeypatch):
    keys = iter(["sk-old-example", "sk-new-example"])
    captured = []
    monkeypatch.setattr(module, "get_api_key", lambda: next(keys))
    monkeypatch.setattr(module, "OpenAI", lambda **kwargs: captured.append(kwargs) or SimpleNamespace())
    module.openai_client()
    module.openai_client()
    assert [item["api_key"] for item in captured] == ["sk-old-example", "sk-new-example"]
    assert all(item["max_retries"] == 0 for item in captured)


def test_unknown_error_never_exposes_payload():
    msg = module.api_error_message(RuntimeError("sk-secret-should-not-leak"))
    assert "sk-secret-should-not-leak" not in msg


def test_missing_key_error_explains_configuration():
    msg = module.api_error_message(RuntimeError(
        "Missing OpenAI API key. Add OPENAI_API_KEY to this app's "
        "Streamlit Cloud Settings → Secrets, then restart the app."
    ))
    assert "OPENAI_API_KEY" in msg
