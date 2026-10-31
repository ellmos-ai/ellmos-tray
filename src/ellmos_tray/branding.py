"""
Branding and appearance configuration for ellmos-tray.
Allows seamless switching between ELLMOS, BACH, and OCEAN brandings.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TrayBranding:
    """Configuration class defining the branding, names, icons and labels of the tray."""

    app_id: str = "ellmos-tray"
    app_title: str = "ELLMOS System Tray"
    icon_char: str = "E"
    icon_path: Path | None = None
    notification_title: str = "ELLMOS"
    lock_file: Path | None = None

    # Colors (RGBA)
    color_connected: tuple[int, int, int, int] = (0, 200, 100, 255)       # Green
    color_full_mode: tuple[int, int, int, int] = (255, 165, 0, 255)       # Orange
    color_processing: tuple[int, int, int, int] = (90, 120, 220, 255)     # Blue
    color_disconnected: tuple[int, int, int, int] = (180, 40, 40, 255)    # Red

    # Slot display names
    slot_labels: dict[str, str] = field(default_factory=lambda: {
        "buddha_chat": "💬 Chat",
        "buddha_always_on": "⚡ Always-On Worker",
        "buddha_connector": "📱 Connector",
    })

    # Service display names
    service_labels: dict[str, str] = field(default_factory=lambda: {
        "gui": "GUI Dashboard (:8000)",
        "control": "Control API (:8081)",
        "ollama": "Ollama (:11434)",
    })

    # Navigation link labels
    gui_label: str = "Oberfläche öffnen"
    chat_label: str = "Web Chat"
    activity_label: str = "Aktivitätsanzeige"
    messenger_label: str = "Telegram"

    def get_lock_file(self) -> Path:
        """Returns the canonical single-instance lock file path for this branding."""
        if self.lock_file:
            return self.lock_file
        if self.app_id.startswith("bach"):
            return Path.home() / ".bach" / "chat_tray.lock"
        if self.app_id.startswith("ocean"):
            return Path.home() / ".ocean" / "tray.lock"
        return Path.home() / ".ellmos" / "tray.lock"

    @classmethod
    def ellmos(cls) -> TrayBranding:
        """Factory for the default ELLMOS branding."""
        return cls(
            app_id="ellmos-tray",
            app_title="ELLMOS System Tray",
            icon_char="E",
            notification_title="ELLMOS",
            lock_file=Path.home() / ".ellmos" / "tray.lock",
            slot_labels={
                "buddha_chat": "💬 Chat",
                "buddha_always_on": "⚡ Always-On Worker",
                "buddha_connector": "📱 Connector",
            },
            gui_label="ELLMOS öffnen",
            chat_label="ELLMOS Chat",
            activity_label="Aktivitätsanzeige",
            messenger_label="Telegram",
        )

    @classmethod
    def bach(cls) -> TrayBranding:
        """Factory for the BACH OS branding (100% parity with legacy chat_tray.py)."""
        return cls(
            app_id="bach-system",
            app_title="BACH System",
            icon_char="B",
            notification_title="BACH",
            lock_file=Path.home() / ".bach" / "chat_tray.lock",
            slot_labels={
                "buddha_chat": "💬 Buddha Chat",
                "buddha_always_on": "⚡ Buddha Always-On",
                "buddha_connector": "📱 Buddha Connector",
            },
            gui_label="BACH öffnen",
            chat_label="Buddha Chat",
            activity_label="Aktivitätsanzeige",
            messenger_label="Telegram",
        )

    @classmethod
    def ocean(cls) -> TrayBranding:
        """Factory for Open Ocean branding."""
        return cls(
            app_id="ocean-tray",
            app_title="Open Ocean Tray",
            icon_char="O",
            notification_title="OCEAN",
            lock_file=Path.home() / ".ocean" / "tray.lock",
            slot_labels={
                "buddha_chat": "💬 Ocean Chat",
                "buddha_always_on": "⚡ Ocean Worker",
                "buddha_connector": "📱 Ocean Connector",
            },
            gui_label="Ocean öffnen",
            chat_label="Ocean Chat",
            activity_label="Aktivitätsanzeige",
            messenger_label="Telegram",
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TrayBranding:
        """Builds branding from a configuration dictionary."""
        clean = dict(data)
        if clean.get("lock_file"):
            clean["lock_file"] = Path(clean["lock_file"])
        if clean.get("icon_path"):
            clean["icon_path"] = Path(clean["icon_path"])
        return cls(**clean)
