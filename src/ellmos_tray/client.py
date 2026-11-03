"""
HTTP client for communicating with the Control API, GUI server, and LLM backends.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from ellmos_tray.navigation import normalize_gui_url


class _NoControlRedirect(urllib.request.HTTPRedirectHandler):
    """Disallows HTTP redirects on authenticated Control API requests (#510).

    Prevents Bearer token leakage across origins or redirect loops when talking
    to the Control API.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[override]
        return None


def _is_same_origin(url_a: str, url_b: str) -> bool:
    """Returns True if two URLs share scheme, hostname, and effective port."""
    pa, pb = urlsplit(url_a), urlsplit(url_b)
    port_a = pa.port or (443 if pa.scheme == "https" else 80)
    port_b = pb.port or (443 if pb.scheme == "https" else 80)
    return (
        pa.scheme.lower() == pb.scheme.lower()
        and (pa.hostname or "").lower() == (pb.hostname or "").lower()
        and port_a == port_b
    )


def _resolve_auth_header(explicit: str | None = None) -> str | None:
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
        gui_url: str | None = None,
        ollama_url: str | None = None,
        telegram_url: str = "https://t.me/bach_assistant_bot",
        auth_header: str | None = None,
    ):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.gui_url = normalize_gui_url(
            gui_url or os.environ.get("ELLMOS_GUI_URL")
            or os.environ.get("BACH_GUI_URL") or f"http://{host}:8000"
        )
        self.ollama_url = ollama_url or f"http://{host}:11434"
        self.telegram_url = telegram_url
        self._auth_header = _resolve_auth_header(auth_header)

    @property
    def auth_header(self) -> str | None:
        return self._auth_header

    @auth_header.setter
    def auth_header(self, value: str | None) -> None:
        self._auth_header = value

    def api_request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        base: str | None = None,
        timeout: int = 8,
    ) -> dict[str, Any] | None:
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
            use_no_redirect = (
                "Authorization" in headers
                and getattr(urllib.request.urlopen, "__module__", "") == "urllib.request"
            )
            if use_no_redirect:
                opener = urllib.request.build_opener(
                    urllib.request.ProxyHandler({}),
                    _NoControlRedirect(),
                )
                ctx = opener.open(req, timeout=timeout)
            else:
                ctx = urllib.request.urlopen(req, timeout=timeout)
            with ctx as resp:
                resp_url = getattr(resp, "geturl", lambda: url)()
                if isinstance(resp_url, str) and resp_url and not _is_same_origin(url, resp_url):
                    return None
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

    def get_status(self) -> dict[str, Any] | None:
        return self.api_request("GET", "/api/status", timeout=8)

    def get_backends(self) -> dict[str, Any] | None:
        return self.api_request("GET", "/api/backends")

    def get_models(self) -> dict[str, Any] | None:
        return self.api_request("GET", "/api/models")

    def get_slots(self) -> dict[str, Any] | None:
        return self.api_request("GET", "/api/slots")

    def set_backend(self, name: str, model: str | None = None) -> dict[str, Any] | None:
        payload: dict[str, Any] = {"name": name}
        if model:
            payload["model"] = model
        return self.api_request("POST", "/api/backend", payload)

    def set_model(self, model: str) -> dict[str, Any] | None:
        return self.api_request("POST", "/api/model", {"model": model})

    def set_mode(self, mode: str) -> dict[str, Any] | None:
        return self.api_request("POST", "/api/mode", {"mode": mode})

    def set_think(self, think: bool) -> dict[str, Any] | None:
        return self.api_request("POST", "/api/think", {"think": think})

    def set_max_tool_rounds(self, rounds: int) -> dict[str, Any] | None:
        return self.api_request("POST", "/api/max_tool_rounds", {"rounds": rounds})

    def set_fackel(self, preference: str) -> dict[str, Any] | None:
        return self.api_request("POST", "/api/fackel", {"preference": preference})

    def update_slot(self, slot_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        return self.api_request("POST", "/api/slots", {"slot_id": slot_id, "updates": updates})

    def run_worker(self, worker_id: str) -> dict[str, Any] | None:
        return self.api_request("POST", "/api/workers/run", {"id": worker_id})

    def toggle_worker(self, worker_id: str, new_status: str) -> dict[str, Any] | None:
        return self.api_request("POST", "/api/workers/toggle", {"id": worker_id, "status": new_status})

    def delete_worker(self, worker_id: str) -> dict[str, Any] | None:
        return self.api_request("POST", "/api/workers/delete", {"id": worker_id})

    def send_chat(
        self,
        prompt: str,
        chat_id: str = "tray-prompt",
        mode: str | None = None,
        timeout: int = 300,
    ) -> dict[str, Any] | None:
        payload: dict[str, Any] = {"prompt": prompt, "chat_id": chat_id}
        if mode:
            payload["mode"] = mode
        return self.api_request("POST", "/api/chat", payload, timeout=timeout)

    def get_history(self, chat_id: str) -> dict[str, Any] | None:
        return self.api_request("GET", f"/api/history?chat_id={chat_id}")


    def get_permissions(self) -> dict[str, Any] | None:
        return self.api_request("GET", "/api/permissions", base=self.gui_url)

    def update_permissions(self, updates: dict[str, bool]) -> dict[str, Any] | None:
        return self.api_request("POST", "/api/permissions", {"permissions": updates}, base=self.gui_url)

    def get_talk_config(self) -> dict[str, Any] | None:
        return self.api_request("GET", "/api/talk/config", base=self.gui_url, timeout=3)

    def update_talk_config(self, updates: dict[str, Any]) -> dict[str, Any] | None:
        return self.api_request("POST", "/api/talk/config", updates, base=self.gui_url, timeout=4)

    def release_model_for_compute(self, model: str | None = None) -> dict[str, Any]:
        """Switches Fackel to compute, pauses Always-On, and requests Ollama keep_alive=0."""
        fackel_res = self.set_fackel("compute")
        slot_res = self.update_slot("buddha_always_on", {"enabled": False})
        unloaded = False
        if model and model != "?":
            unload_res = self.api_request(
                "POST",
                "/api/generate",
                {"model": model, "keep_alive": 0},
                base=self.ollama_url,
                timeout=3,
            )
            unloaded = unload_res is not None
        return {
            "ok": fackel_res is not None,
            "fackel": "compute",
            "always_on_paused": bool(slot_res and slot_res.get("ok")),
            "ollama_unloaded": unloaded,
        }


    def get_ram_claiming_status(self) -> dict[str, Any]:
        """Queries Ollama /api/ps for currently loaded models and RAM/VRAM usage."""
        ps_resp = self.api_request("GET", "/api/ps", base=self.ollama_url, timeout=3)
        models = ps_resp.get("models", []) if isinstance(ps_resp, dict) else []
        loaded_names: list[str] = []
        total_bytes = 0
        for m in models:
            if not isinstance(m, dict):
                continue
            name = str(m.get("name") or m.get("model") or "").strip()
            if name:
                loaded_names.append(name)
            size_val = m.get("size_vram") or m.get("size") or 0
            if isinstance(size_val, (int, float)) and size_val > 0:
                total_bytes += int(size_val)
        gib = round(total_bytes / (1024 ** 3), 1) if total_bytes > 0 else 0.0
        return {
            "loaded_models": loaded_names,
            "loaded_count": len(loaded_names),
            "claimed_gib": gib,
        }
