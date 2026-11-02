"""
Core TrayApp application class.
Coordinates configuration, Control API client, dynamic menus, icon generation,
background polling, reconnect logic, crash/sleep recovery, and process ownership.
"""
from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from enum import StrEnum
from typing import Any

from ellmos_tray.branding import TrayBranding
from ellmos_tray.client import ControlApiClient
from ellmos_tray.device import check_device_acceptance
from ellmos_tray.icon import generate_tray_icon
from ellmos_tray.lock import release_single_instance_lock
from ellmos_tray.menu import MenuBuilder
from ellmos_tray.process import BackendProcessManager
from ellmos_tray.prompts import PromptManager
from ellmos_tray.runner import PassiveTaskDelegate, TaskExecutionDelegate


class ConnectionState(StrEnum):
    """Network connection status to the backend Control API."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"


class TrayApp:
    """The main System Tray application."""

    DEFAULT_POLL_INTERVAL = 5

    def __init__(
        self,
        branding: TrayBranding | None = None,
        client: ControlApiClient | None = None,
        host: str = "127.0.0.1",
        port: int = 8081,
        runner: TaskExecutionDelegate | None = None,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        backend_manager: BackendProcessManager | None = None,
    ):
        self.branding = branding or TrayBranding.ellmos()
        self.client = client or ControlApiClient(host=host, port=port)
        self.runner = runner or PassiveTaskDelegate()
        self.poll_interval = poll_interval
        self.backend_manager = backend_manager or BackendProcessManager(
            host=host, port=port, client=self.client
        )

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
        self.permissions: dict[str, bool] = {
            "system_tools": True,
            "browser_control": True,
            "camera": False,
            "microphone": False,
            "screen_capture": True,
            "voice_tts": False,
            "speech_to_text": True,
            "smarthome_robotics": False,
            "ollama": True,
        }
        self.talk_config: dict[str, Any] = {
            "persona": "buddha",
            "operating_mode": "ptt",
            "primary_model": "qwen3.8:27b-mlx",
            "fast_relay_model": "smollm2:360m",
            "summon_policy": "knock",
        }

        # Connection & Reconnect state machine
        self.connection_state: ConnectionState = ConnectionState.DISCONNECTED
        self.max_status_failures = 3
        self._failed_status_count = 0
        self.min_reconnect_delay = 1.0
        self.max_reconnect_delay = 30.0
        self.reconnect_delay = self.min_reconnect_delay
        self.reconnect_factor = 1.5
        self.active_poll_interval = 2.0

        # Crash & Sleep recovery tracking
        self.last_poll_timestamp: float = time.monotonic()
        self.sleep_threshold: float = 15.0
        self.sleep_recoveries_count: int = 0

        self._stop_event = threading.Event()
        self._instance_lock: Any | None = None
        self.icon: Any = None

    @property
    def current_poll_interval(self) -> float:
        """Adaptive poll interval based on task processing state and connectivity."""
        if self.runner.is_processing():
            return min(self.active_poll_interval, float(self.poll_interval))
        if self.connection_state == ConnectionState.RECONNECTING:
            return max(float(self.poll_interval), self.reconnect_delay)
        return float(self.poll_interval)

    @property
    def icon_image(self) -> Any:
        return generate_tray_icon(
            branding=self.branding,
            connected=self.state.get("connected", False),
            mode=self.state.get("mode", "safe"),
            is_processing=self.runner.is_processing(),
            use_cache=True,
        )

    def refresh(self) -> None:
        """Fetches status, backends, models, slots, and service availability with reconnect state machine."""
        prev_connected = bool(self.state.get("connected", False))
        prev_conn_state = self.connection_state

        status = self.client.get_status()
        if status and "backend" in status:
            self._failed_status_count = 0
            self.state.update(status)
            self.state["connected"] = True
            self.connection_state = ConnectionState.CONNECTED
            self.reconnect_delay = self.min_reconnect_delay

            # Re-verify process ownership
            self.backend_manager.detect_or_attach()

            # Connection restored notification
            if (
                prev_conn_state in (ConnectionState.RECONNECTING, ConnectionState.DISCONNECTED)
                and not prev_connected
            ):
                try:
                    self.notify(
                        f"Verbindung zu {self.client.base_url} wiederhergestellt.",
                        self.branding.notification_title,
                    )
                except Exception:
                    pass
        else:
            self._failed_status_count += 1
            if self._failed_status_count >= self.max_status_failures:
                self.state["connected"] = False
                self.connection_state = ConnectionState.RECONNECTING
                self.reconnect_delay = min(
                    self.reconnect_delay * self.reconnect_factor,
                    self.max_reconnect_delay,
                )
            else:
                self.connection_state = ConnectionState.DISCONNECTED

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
        perms_resp = self.client.get_permissions()
        if isinstance(perms_resp, dict) and isinstance(perms_resp.get("permissions"), dict):
            for k, v in perms_resp["permissions"].items():
                if k in self.permissions:
                    self.permissions[k] = bool(v)
        if hasattr(self.client, "get_talk_config"):
            talk_resp = self.client.get_talk_config()
            if isinstance(talk_resp, dict) and talk_resp.get("ok"):
                cfg = talk_resp.get("config", talk_resp)
                if isinstance(cfg, dict):
                    for k in ("persona", "operating_mode", "primary_model", "fast_relay_model", "summon_policy"):
                        if k in cfg and cfg[k]:
                            self.talk_config[k] = cfg[k]

    def run_device_acceptance_check(self) -> dict[str, Any]:
        """Runs the device acceptance check and returns a structured report dictionary."""
        report = check_device_acceptance(
            branding=self.branding,
            client=self.client,
            host=self.client.host,
            port=self.client.port,
        )
        return report.to_dict()

    def handle_sleep_recovery(self, elapsed: float) -> None:
        """Handles recovery after system sleep or thread freeze."""
        self.sleep_recoveries_count += 1
        self.reconnect_delay = self.min_reconnect_delay
        self.backend_manager.detect_or_attach()
        try:
            self.notify(
                f"Aufwachphase ({int(elapsed)}s) erkannt. Verbindungen werden aktualisiert.",
                self.branding.notification_title,
            )
        except Exception:
            pass

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
        proc_info = self.backend_manager.get_info()
        return (
            self.state.get("connected"),
            self.connection_state.value,
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
            tuple(sorted(self.permissions.items())),
            tuple(sorted(self.talk_config.items())),
            proc_info.get("ownership"),
            proc_info.get("pid"),
        )

    def update_ui(self) -> None:
        """Updates the tray icon image and menu items if running."""
        if self.icon:
            self.icon.icon = self.icon_image
            self.icon.menu = self.menu_builder.build_menu()

    def notify(self, message: str, title: str | None = None) -> None:
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
        self.last_poll_timestamp = time.monotonic()
        while not self._stop_event.is_set():
            now = time.monotonic()
            elapsed = now - self.last_poll_timestamp
            expected = self.current_poll_interval
            if elapsed > max(expected * 3.0, self.sleep_threshold):
                self.handle_sleep_recovery(elapsed)
            self.last_poll_timestamp = time.monotonic()

            self.refresh()
            new_sig = self.menu_signature()
            if new_sig != old_sig:
                self.update_ui()
                old_sig = new_sig
            self.runner.on_poll_tick(self)

            wait_interval = self.current_poll_interval
            self._stop_event.wait(wait_interval)
            self.last_poll_timestamp = time.monotonic()

    def run(self) -> None:
        """Starts background polling and runs the system tray event loop."""
        import pystray

        self.backend_manager.detect_or_attach()
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
            conn_status = (
                f"verbunden (:{self.client.port})"
                if self.state.get("connected")
                else "offline (Reconnect-Modus)"
            )
            try:
                self.notify(
                    f"{self.branding.app_title} ist aktiv ({conn_status}).",
                    self.branding.notification_title,
                )
            except Exception:
                pass

        self.icon.run(setup=_on_ready)

    def stop(self) -> None:
        """Signals shutdown, terminates owned child backend if any, and releases the instance lock."""
        self._stop_event.set()
        if self.icon:
            self.icon.stop()
        # Clean shutdown only of own child process
        self.backend_manager.shutdown()
        if self._instance_lock:
            release_single_instance_lock(self._instance_lock)
            self._instance_lock = None
