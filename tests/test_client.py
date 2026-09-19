"""
Unit tests for ControlApiClient HTTP calls and error resilience.
"""
import json
import urllib.error
from unittest.mock import MagicMock, patch
from ellmos_tray.client import ControlApiClient


def test_client_urls():
    client = ControlApiClient(host="myhost", port=9000)
    assert client.base_url == "http://myhost:9000"
    assert client.gui_url == "http://myhost:8000"
    assert client.ollama_url == "http://myhost:11434"


def test_api_request_success():
    client = ControlApiClient(host="127.0.0.1", port=8081, auth_header="Bearer secret123")
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"backend": "ollama", "connected": True}).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen:
        status = client.get_status()
        assert status == {"backend": "ollama", "connected": True}

        # Verify request headers
        req = mock_urlopen.call_args[0][0]
        assert req.get_header("Authorization") == "Bearer secret123"


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
