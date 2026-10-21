"""
Core TrayApp application class.
Coordinates configuration, Control API client, dynamic menus, icon generation, and background polling.
"""
from __future__ import annotations

import os
import subprocess
import sys
import threading
from typing import Any, Optional

from ellmos_tray.branding import TrayBranding
from ellmos_tray.client import ControlApiClient
from ellmos_tray.icon import generate_tray_icon
from ellmos_tray.lock import release_single_instance_lock
from ellmos_tray.menu import MenuBuilder
from ellmos_tray.prompts import PromptManager
from ellmos_tray.runner import PassiveTaskDelegate, TaskExecutionDelegate


class TrayApp:
    """The main System Tray application."""

    DEFAULT_POLL_INTERVAL = 5

    def __init__(
        self,
        branding: Optional[TrayBranding] = None,
        client: Optional[ControlApiClient] = None,
        host: str = "127.0.0.1",
        port: int = 8081,
        runner: Optional[TaskExecutionDelegate] = None,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
    ):
        self.branding = branding or TrayBranding.ellmos()
        self.client = client or ControlApiClient(host=host, port=port)
        self.runner = runner or PassiveTaskDelegate()
        self.poll_interval = poll_interval

        self.prompt_manager = PromptManager()
        self.menu_builder = MenuBuilder(self)

        self.state: dict[str, Any] = {
            "backend": "?",
            "backend_cli": "",
            "model": "?",
            "mode": "safe",
            "think": True,
            "sessions": 0,
            "connected": False,
            "max_tool_rounds": 12,
            "fackel_preference": "compute",
            "current_tool": "",
            "last_tools": [],
        }
        self.backends: dict[str, Any] = {}
        self.models: list[str] = []
        self.slots: dict[str, Any] = {}
        self.dynamic_workers: list[dict[str, Any]] = []
        self.services: dict[str, bool] = {"gui": False, "control": False, "ollama": False}

        self.max_status_failures = 3
        self._failed_status_count = 0
        self._stop_event = threading.Event()
        self._instance_lock: Optional[Any] = None
        self.icon: Any = None

    @property
    def icon_image(self) -> Any:
        return generate_tray_icon(
            branding=self.branding,
            connected=self.state.get("connected", False),
            mode=self.state.get("mode", "safe"),
            is_processing=self.runner.is_processing(),
        )

    def refresh(self) -> None:
        """Fetches status, backends, models, slots, and service availability."""
        status = self.client.get_status()
        if status and "backend" in status:
            self._failed_status_count = 0
            self.state.update(status)
            self.state["connected"] = True
        else:
            self._failed_status_count += 1
            if self._failed_status_count >= self.max_status_failures:
                self.state["connected"] = False

        bs = self.client.get_backends()
        if bs and not bs.get("error"):
            self.backends = bs

        ms = self.client.get_models()
        if ms and "models" in ms:
            self.models = ms["models"]

        slots_resp = self.client.get_slots()
        if slots_resp and slots_resp.get("ok"):
            self.slots = slots_resp.get("slots", {})
            self.dynamic_workers = slots_resp.get("dynamic_workers", [])
            if "fackel_preference" in slots_resp:
                self.state["fackel_preference"] = slots_resp["fackel_preference"]

        self.services["control"] = self.state["connected"]
        self.services["gui"] = self.client.check_url(self.client.gui_url + "/")
        self.services["ollama"] = self.client.check_url(self.client.ollama_url + "/api/tags")

    def menu_signature(self) -> tuple[Any, ...]:
        worker_sig = tuple(
            (
                w.get("id"),
                w.get("status"),
                w.get("model"),
                w.get("current_activity"),
                w.get("max_tool_rounds"),
                w.get("running"),
                w.get("worker_active"),
                tuple(
                    (w["execution"] if isinstance(w.get("execution"), dict) else {}).get(key)
                    for key in (
                        "state", "terminal", "generation", "start_request_id",
                        "worker_thread_started", "service_instance",
                    )
                ),
            )
            for w in self.dynamic_workers
        )
        slot_sig = tuple(
            (
                k,
                v.get("model"),
                v.get("backend"),
                v.get("max_tool_rounds"),
                v.get("mode"),
                v.get("enabled"),
                v.get("current_activity"),
            )
            for k, v in sorted(self.slots.items())
        )
        return (
            self.state.get("connected"),
            self.state.get("mode"),
            self.state.get("think"),
            self.state.get("fackel_preference"),
            self.state.get("backend"),
            self.state.get("model"),
            len(self.models),
            self.runner.get_current_task_name(),
            self.runner.is_processing(),
            self.runner.is_enabled,
            worker_sig,
            slot_sig,
            tuple(sorted(self.services.items())),
        )

    def update_ui(self) -> None:
        """Updates the tray icon image and menu items if running."""
        if self.icon:
            self.icon.icon = self.icon_image
            self.icon.menu = self.menu_builder.build_menu()

    def notify(self, message: str, title: Optional[str] = None) -> None:
        """Displays a desktop notification balloon."""
        if self.icon:
            header = title or self.branding.notification_title
            try:
                self.icon.notify(message, header)
            except Exception:
                pass

    def toggle_idle(self) -> None:
        new_state = self.runner.toggle_enabled()
        self.refresh()
        self.update_ui()
        status_text = "aktiviert" if new_state else "deaktiviert"
        self.notify(f"Idle-Modus {status_text}", self.branding.notification_title)

    def open_promptboard(self) -> None:
        app_path = self.prompt_manager.find_app_path()
        if not app_path:
            self.notify("PromptBoard-App nicht gefunden", f"{self.branding.notification_title} PromptBoard")
            return
        try:
            if sys.platform == "win32" and app_path.suffix.lower() in {".bat", ".msix"}:
                os.startfile(str(app_path))
            else:
                subprocess.Popen(
                    [str(app_path)],
                    cwd=str(app_path.parent),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except OSError:
            self.notify("PromptBoard-Start fehlgeschlagen", f"{self.branding.notification_title} PromptBoard")

    def _poll_loop(self) -> None:
        old_sig = self.menu_signature()
        while not self._stop_event.is_set():
            self.refresh()
            new_sig = self.menu_signature()
            if new_sig != old_sig:
                self.update_ui()
                old_sig = new_sig
            self.runner.on_poll_tick(self)
            self._stop_event.wait(self.poll_interval)

    def run(self) -> None:
        """Starts background polling and runs the system tray event loop."""
        import pystray

        self.refresh()
        self.icon = pystray.Icon(
            self.branding.app_id,
            self.icon_image,
            self.branding.app_title,
            self.menu_builder.build_menu(),
        )

        poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        poll_thread.start()

        def _on_ready(icon: Any) -> None:
            icon.visible = True
            conn_status = "verbunden (:8081)" if self.state.get("connected") else "offline (Reconnect-Modus)"
            try:
                self.notify(
                    f"{self.branding.app_title} ist aktiv ({conn_status}).",
                    self.branding.notification_title,
                )
            except Exception:
                pass

        self.icon.run(setup=_on_ready)

    def stop(self) -> None:
        """Signals shutdown and releases the instance lock."""
        self._stop_event.set()
        if self.icon:
            self.icon.stop()
        if self._instance_lock:
            release_single_instance_lock(self._instance_lock)
            self._instance_lock = None
