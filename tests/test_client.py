"""
Unit tests for ControlApiClient HTTP calls, header/URL security guards, and error resilience.
"""
import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from ellmos_tray.client import MAX_API_RESPONSE_BYTES, ControlApiClient


def test_client_urls():
    client = ControlApiClient(host="myhost", port=9000)
    assert client.base_url == "http://myhost:9000"
    assert client.gui_url == "http://myhost:8000"
    assert client.ollama_url == "http://myhost:11434"


def test_api_request_success():
    client = ControlApiClient(host="127.0.0.1", port=8081, auth_header="Bearer CHANGE-ME-TEST")
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"backend": "ollama", "connected": True}).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen:
        status = client.get_status()
        assert status == {"backend": "ollama", "connected": True}

        # Verify request headers
        req = mock_urlopen.call_args[0][0]
        assert req.get_header("Authorization") == "Bearer CHANGE-ME-TEST"


def test_api_request_network_failure():
    client = ControlApiClient(host="127.0.0.1", port=8081)

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Connection refused")):
        status = client.get_status()
        assert status is None


def test_check_url():
    client = ControlApiClient(host="127.0.0.1", port=8081)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        assert client.check_url("http://127.0.0.1:8000/") is True

    with patch("urllib.request.urlopen", side_effect=OSError("Unreachable")):
        assert client.check_url("http://127.0.0.1:8000/") is False


def test_send_chat():
    client = ControlApiClient(host="127.0.0.1", port=8081)
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"ok": True, "answer": "Hello from model"}).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = client.send_chat("Test Prompt", chat_id="chat-1", mode="full")
        assert res["ok"] is True
        assert res["answer"] == "Hello from model"


def test_no_control_redirect_boundary():
    from ellmos_tray.client import _is_same_origin, _NoControlRedirect

    handler = _NoControlRedirect()
    assert handler.redirect_request(None, None, 302, "Found", {}, "http://evil.example/api") is None
    assert _is_same_origin("http://127.0.0.1:8081/api/status", "http://127.0.0.1:8081/api/v2") is True
    assert _is_same_origin("http://127.0.0.1:8081/api/status", "http://127.0.0.1:8000/api/status") is False

    client = ControlApiClient(host="127.0.0.1", port=8081, auth_header="Bearer CHANGE-ME-TEST")
    mock_resp = MagicMock()
    mock_resp.geturl.return_value = "http://evil.example:8081/api/status"
    mock_resp.read.return_value = json.dumps({"backend": "ollama"}).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        assert client.get_status() is None


def test_get_ram_claiming_status():
    client = ControlApiClient(host="127.0.0.1", port=8081)
    mock_resp = MagicMock()
    mock_resp.geturl.return_value = "http://127.0.0.1:11434/api/ps"
    mock_resp.read.return_value = json.dumps({
        "models": [{"name": "qwen3.8:27b-mlx", "size_vram": 18 * 1024**3}]
    }).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        info = client.get_ram_claiming_status()
        assert info["loaded_count"] == 1
        assert info["loaded_models"] == ["qwen3.8:27b-mlx"]
        assert info["claimed_gib"] == 18.0


def test_auth_header_rejects_crlf_and_reads_commented_token_file(tmp_path, monkeypatch):
    # Explicit CRLF header injection attempt must fail closed to None without fallback
    injected = ControlApiClient(host="127.0.0.1", port=8081, auth_header="Bearer ok\r\nX-Evil: 1")
    assert injected.auth_header is None

    injected.auth_header = "Bearer valid"
    assert injected.auth_header == "Bearer valid"
    injected.auth_header = "Bearer bad\nX-Injected: 1"
    assert injected.auth_header is None

    # Token file with comments and blank lines resolves first valid token line
    tok_file = tmp_path / "control_token.txt"
    tok_file.write_text("# local control token\n\nplaceholder-test-token\n", encoding="utf-8")
    monkeypatch.delenv("CONTROL_API_AUTH_HEADER", raising=False)
    monkeypatch.delenv("BACH_CONTROL_API_TOKEN", raising=False)
    monkeypatch.setenv("BACH_CONTROL_API_TOKEN_FILE", str(tok_file))

    from_file = ControlApiClient(host="127.0.0.1", port=8081)
    assert from_file.auth_header == "Bearer placeholder-test-token"


def test_api_request_enforces_response_size_limit():
    client = ControlApiClient(host="127.0.0.1", port=8081)
    mock_resp = MagicMock()
    mock_resp.geturl.return_value = "http://127.0.0.1:8081/api/status"
    mock_resp.read.return_value = b"x" * (MAX_API_RESPONSE_BYTES + 1)
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        assert client.get_status() is None


def test_get_history_url_encodes_chat_id():
    client = ControlApiClient(host="127.0.0.1", port=8081)
    mock_resp = MagicMock()
    mock_resp.geturl.return_value = "http://127.0.0.1:8081/api/history"
    mock_resp.read.return_value = json.dumps({"messages": []}).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen:
        res = client.get_history("idle-role-1&admin=true#frag")
        assert res == {"messages": []}
        req = mock_urlopen.call_args[0][0]
        assert req.full_url == "http://127.0.0.1:8081/api/history?chat_id=idle-role-1%26admin%3Dtrue%23frag"


@pytest.mark.parametrize(
    "unsafe_url",
    [
        "file:///C:/Windows/System32/calc.exe",
        "javascript:alert(1)",
        "\\\\attacker.example\\share\\payload.exe",
        "https://t.me/bach_assistant_bot\r\nX-Evil: 1",
        "\x01http://127.0.0.1:8000",
        "ht\ttp://example.com",
    ],
)
def test_telegram_url_requires_safe_http_scheme(unsafe_url):
    with pytest.raises(ValueError, match="HTTP"):
        ControlApiClient(host="127.0.0.1", port=8081, telegram_url=unsafe_url)
