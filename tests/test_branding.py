"""
Unit tests for TrayBranding configuration and factory presets.
"""
from pathlib import Path

from ellmos_tray.branding import TrayBranding


def test_branding_defaults():
    branding = TrayBranding()
    assert branding.app_id == "ellmos-tray"
    assert branding.app_title == "ELLMOS System Tray"
    assert branding.icon_char == "E"
    assert branding.notification_title == "ELLMOS"
    assert branding.get_lock_file() == Path.home() / ".ellmos" / "tray.lock"


def test_branding_ellmos_preset():
    branding = TrayBranding.ellmos()
    assert branding.icon_char == "E"
    assert "Chat" in branding.slot_labels["buddha_chat"]
    assert branding.get_lock_file() == Path.home() / ".ellmos" / "tray.lock"


def test_branding_bach_preset():
    branding = TrayBranding.bach()
    assert branding.app_id == "bach-system"
    assert branding.app_title == "BACH System"
    assert branding.icon_char == "B"
    assert branding.notification_title == "BACH"
    assert branding.get_lock_file() == Path.home() / ".bach" / "chat_tray.lock"
    assert branding.slot_labels["buddha_chat"] == "💬 Buddha Chat"
    assert branding.slot_labels["buddha_always_on"] == "⚡ Buddha Always-On"
    assert branding.slot_labels["buddha_connector"] == "📱 Buddha Connector"


def test_branding_ocean_preset():
    branding = TrayBranding.ocean()
    assert branding.app_id == "ocean-tray"
    assert branding.icon_char == "O"
    assert branding.get_lock_file() == Path.home() / ".ocean" / "tray.lock"


def test_branding_custom_lock_file():
    custom_path = Path("/tmp/custom.lock")
    branding = TrayBranding(lock_file=custom_path)
    assert branding.get_lock_file() == custom_path


def test_branding_from_dict():
    data = {
        "app_id": "custom-tray",
        "app_title": "Custom Tray",
        "icon_char": "C",
        "notification_title": "Custom",
        "lock_file": "/tmp/custom.lock",
    }
    branding = TrayBranding.from_dict(data)
    assert branding.app_id == "custom-tray"
    assert branding.icon_char == "C"
    assert branding.get_lock_file() == Path("/tmp/custom.lock")
