"""
Unit tests for TrayApp lifecycle, notifications, and CLI entry point.
"""
import json
import sys
from unittest.mock import MagicMock
import pytest

from ellmos_tray import __main__ as main_mod
from ellmos_tray.app import TrayApp
from ellmos_tray.branding import TrayBranding


def test_app_refresh_updates_state(mock_pystray):
    app = TrayApp()
    app.client.get_status = MagicMock(return_value={"backend": "ollama", "mode": "safe"})
    app.client.get_backends = MagicMock(return_value={"ollama": {}, "claude": {}})
    app.client.get_models = MagicMock(return_value={"models": ["qwen", "llama"]})
    app.client.get_slots = MagicMock(return_value={"ok": True, "slots": {"buddha_chat": {}}})
    app.client.check_url = MagicMock(return_value=True)

    app.refresh()

    assert app.state["connected"] is True
    assert app.state["backend"] == "ollama"
    assert "ollama" in app.backends
    assert app.models == ["qwen", "llama"]
    assert "buddha_chat" in app.slots
    assert app.services["gui"] is True


def test_app_notification(mock_pystray):
    app = TrayApp(branding=TrayBranding.bach())
    app.icon = mock_pystray.Icon("test")

    app.notify("Test notification message")
    assert len(app.icon.notifications) == 1
    msg, title = app.icon.notifications[0]
    assert msg == "Test notification message"
    assert title == "BACH"


def test_main_cli_smoke_promptboard(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ellmos-tray", "--smoke-promptboard"])
    main_mod.main()

    out = capsys.readouterr().out
    data = json.loads(out)
    assert "library_candidates" in data
    assert "prompt_count" in data


def test_main_refuses_duplicate_instance(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ellmos-tray", "--brand", "bach"])
    monkeypatch.setattr(main_mod, "acquire_single_instance_lock", lambda *_: None)

    with pytest.raises(SystemExit) as exc:
        main_mod.main()

    assert exc.value.code == 3
    err = capsys.readouterr().err
    assert "läuft bereits" in err
