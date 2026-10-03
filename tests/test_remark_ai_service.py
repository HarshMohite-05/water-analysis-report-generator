from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import groq

from services import remark_ai_service as service


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(service, "GROQ_API_KEY", "test-key")
    monkeypatch.setattr(service, "AI_MODEL", "openai/gpt-oss-20b")
    factory = MagicMock()
    monkeypatch.setattr(groq, "Groq", factory)
    return factory.return_value.__enter__.return_value


def test_rewrite_and_regeneration(client):
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(finish_reason="stop", message=SimpleNamespace(content="  The sample is clear.  "))]
    )
    result = service.improve_remark("sample clear", previous="The water is clear.")
    assert result == dict(text="The sample is clear.", source="ai", error="")
    request = client.chat.completions.create.call_args.kwargs
    assert request["model"] == "openai/gpt-oss-20b"
    assert "sample clear" in request["messages"][1]["content"]
    assert "The water is clear." in request["messages"][1]["content"]
    assert request["messages"][0]["content"] == service.SYSTEM
    assert request["include_reasoning"] is False


@pytest.mark.parametrize("status,text", [("stop", " "), ("length", "Partial"), ("stop", None)])
def test_unusable_response_falls_back(client, status, text):
    client.chat.completions.create.return_value = SimpleNamespace(choices=[SimpleNamespace(finish_reason=status, message=SimpleNamespace(content=text))])
    result = service.improve_remark("tds high")
    assert result["source"] == "fallback"
    assert result["text"] == "TDS high."
    assert result["error"]


@pytest.mark.parametrize("status", [401, 429, 500, None])
def test_failure_keeps_remark_and_hides_exception_details(client, status):
    error = RuntimeError("secret-key-in-error")
    error.status_code = status
    client.chat.completions.create.side_effect = error
    result = service.improve_remark("sample clear")
    assert result["source"] == "fallback"
    assert result["text"] == "Sample clear."
    assert result["error"]
    assert "secret-key" not in result["error"]


def test_missing_key_and_empty_note_do_not_call_api(client, monkeypatch):
    monkeypatch.setattr(service, "GROQ_API_KEY", "")
    assert service.improve_remark("sample clear")["error"] == "GROQ_API_KEY not set."
    assert service.improve_remark(" ")["text"] == ""
    client.chat.completions.create.assert_not_called()


def test_empty_choices_falls_back(client):
    client.chat.completions.create.return_value = SimpleNamespace(choices=[])
    assert service.improve_remark("sample clear")["source"] == "fallback"
