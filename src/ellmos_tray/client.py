"""
HTTP client for communicating with the Control API, GUI server, and LLM backends.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional


def _resolve_auth_header(explicit: Optional[str] = None) -> Optional[str]:
    """Resolves the Bearer authentication header from explicit arg, env, or credentials file."""
    if explicit:
        return explicit
    hdr = os.environ.get("CONTROL_API_AUTH_HEADER")
    if hdr:
        return hdr
    tok = os.environ.get("BACH_CONTROL_API_TOKEN")
    if tok:
        return f"Bearer {tok.strip()}"
    tok_file = os.environ.get("BACH_CONTROL_API_TOKEN_FILE")
    if tok_file:
        try:
            val = Path(tok_file).read_text(encoding="utf-8").strip()
            if val:
                return f"Bearer {val}"
        except Exception:
            pass
    for p in (
        Path.home() / ".credentials" / "bach_control_api_token",
        Path.home() / ".credentials" / "control_api_token",
        Path("C:/_Local_DEV/CREDENTIALS/bach/control_api_token.txt"),
    ):
        if p.exists():
            try:
                val = p.read_text(encoding="utf-8").strip()
                if val:
                    return f"Bearer {val}"
            except Exception:
                pass
    return None


class ControlApiClient:
    """Handles communication with the local or remote Control API and GUI services."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8081,
        gui_url: Optional[str] = None,
        ollama_url: Optional[str] = None,
        telegram_url: str = "https://t.me/bach_assistant_bot",
        auth_header: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.gui_url = gui_url or f"http://{host}:8000"
        self.ollama_url = ollama_url or f"http://{host}:11434"
        self.telegram_url = telegram_url
        self._auth_header = _resolve_auth_header(auth_header)

    @property
    def auth_header(self) -> Optional[str]:
        return self._auth_header

    @auth_header.setter
    def auth_header(self, value: Optional[str]) -> None:
        self._auth_header = value

    def api_request(
        self,
        method: str,
        path: str,
        body: Optional[dict[str, Any]] = None,
        base: Optional[str] = None,
        timeout: int = 8,
    ) -> Optional[dict[str, Any]]:
        """Sends an HTTP request with JSON encoding and returns decoded JSON."""
        target_base = base or self.base_url
        url = target_base + path
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json"} if data else {}
        if self._auth_header and target_base == self.base_url:
            headers["Authorization"] = self._auth_header

        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers=headers,
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                content = resp.read()
                if not content:
                    return {}
                return json.loads(content.decode("utf-8"))
        except (urllib.error.URLError, OSError, json.JSONDecodeError):
            return None

    def check_url(self, url: str, timeout: int = 2) -> bool:
        """Checks if an HTTP GET request to url returns 200 OK."""
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status == 200
        except (urllib.error.URLError, OSError):
            return False

    def get_status(self) -> Optional[dict[str, Any]]:
        return self.api_request("GET", "/api/status", timeout=8)

    def get_backends(self) -> Optional[dict[str, Any]]:
        return self.api_request("GET", "/api/backends")

    def get_models(self) -> Optional[dict[str, Any]]:
        return self.api_request("GET", "/api/models")

    def get_slots(self) -> Optional[dict[str, Any]]:
        return self.api_request("GET", "/api/slots")

    def set_backend(self, name: str, model: Optional[str] = None) -> Optional[dict[str, Any]]:
        payload: dict[str, Any] = {"name": name}
        if model:
            payload["model"] = model
        return self.api_request("POST", "/api/backend", payload)

    def set_model(self, model: str) -> Optional[dict[str, Any]]:
        return self.api_request("POST", "/api/model", {"model": model})

    def set_mode(self, mode: str) -> Optional[dict[str, Any]]:
        return self.api_request("POST", "/api/mode", {"mode": mode})

    def set_think(self, think: bool) -> Optional[dict[str, Any]]:
        return self.api_request("POST", "/api/think", {"think": think})

    def set_max_tool_rounds(self, rounds: int) -> Optional[dict[str, Any]]:
        return self.api_request("POST", "/api/max_tool_rounds", {"rounds": rounds})

    def set_fackel(self, preference: str) -> Optional[dict[str, Any]]:
        return self.api_request("POST", "/api/fackel", {"preference": preference})

    def update_slot(self, slot_id: str, updates: dict[str, Any]) -> Optional[dict[str, Any]]:
        return self.api_request("POST", "/api/slots", {"slot_id": slot_id, "updates": updates})

    def run_worker(self, worker_id: str) -> Optional[dict[str, Any]]:
        return self.api_request("POST", "/api/workers/run", {"id": worker_id})

    def toggle_worker(self, worker_id: str, new_status: str) -> Optional[dict[str, Any]]:
        return self.api_request("POST", "/api/workers/toggle", {"id": worker_id, "status": new_status})

    def delete_worker(self, worker_id: str) -> Optional[dict[str, Any]]:
        return self.api_request("POST", "/api/workers/delete", {"id": worker_id})

    def send_chat(
        self,
        prompt: str,
        chat_id: str = "tray-prompt",
        mode: Optional[str] = None,
        timeout: int = 300,
    ) -> Optional[dict[str, Any]]:
        payload: dict[str, Any] = {"prompt": prompt, "chat_id": chat_id}
        if mode:
            payload["mode"] = mode
        return self.api_request("POST", "/api/chat", payload, timeout=timeout)

    def get_history(self, chat_id: str) -> Optional[dict[str, Any]]:
        return self.api_request("GET", f"/api/history?chat_id={chat_id}")
