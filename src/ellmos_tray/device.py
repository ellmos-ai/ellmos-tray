"""
Device acceptance check and hardware/runtime readiness verification for ellmos-tray.
Validates loopback networking, service ports, storage permissions, graphics subsystem,
and detects machine sleep/suspend resume events.
"""
from __future__ import annotations

import os
import platform as _sys_platform
import socket
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ellmos_tray.branding import TrayBranding
    from ellmos_tray.client import ControlApiClient


@dataclass
class DeviceAcceptanceReport:
    """Structured report produced by the device acceptance preflight check."""

    passed: bool
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    platform: str = field(default_factory=_sys_platform.platform)
    python_version: str = field(default_factory=_sys_platform.python_version)
    checks: dict[str, dict[str, Any]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def detect_sleep_skip(
    last_timestamp: float,
    expected_interval: float,
    threshold_factor: float = 3.0,
    min_threshold_sec: float = 15.0,
) -> tuple[bool, float]:
    """Detects if system experienced a sleep/suspend cycle or large timing gap.

    Returns (is_sleep_skip, elapsed_seconds).
    """
    now = time.monotonic()
    elapsed = now - last_timestamp
    threshold = max(expected_interval * threshold_factor, min_threshold_sec)
    return (elapsed > threshold, elapsed)


def check_device_acceptance(
    branding: TrayBranding | None = None,
    client: ControlApiClient | None = None,
    host: str = "127.0.0.1",
    port: int = 8081,
) -> DeviceAcceptanceReport:
    """Executes a comprehensive runtime and device environment acceptance check."""
    checks: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    warnings: list[str] = []

    # ── 1. Loopback Networking Stack ──
    # Tests that local loopback is enabled and socket binding is permitted.
    # Essential for Desktop Bridge and Microsoft Store loopback exemption requirements.
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, 0))
        bound_port = sock.getsockname()[1]
        sock.listen(1)
        sock.close()
        checks["loopback"] = {
            "status": "PASS",
            "host": host,
            "test_port": bound_port,
            "message": "Loopback interface binding verified.",
        }
    except Exception as exc:
        err = f"Loopback network binding failed on {host}: {exc}"
        checks["loopback"] = {"status": "FAIL", "error": str(exc)}
        errors.append(err)

    # ── 2. Storage Permissions (Config & Lock directories) ──
    try:
        from ellmos_tray.branding import TrayBranding as DefaultBranding
        target_branding = branding or DefaultBranding.ellmos()
        lock_path = target_branding.get_lock_file()
        lock_dir = lock_path.parent
        lock_dir.mkdir(parents=True, exist_ok=True)

        # Probe write/delete test
        test_file = lock_dir / f".probe_{os.getpid()}_{int(time.time())}.tmp"
        test_file.write_text("readiness_check", encoding="utf-8")
        test_file.unlink(missing_ok=True)

        checks["storage"] = {
            "status": "PASS",
            "lock_dir": str(lock_dir),
            "writable": True,
        }
    except Exception as exc:
        err = f"Storage directory write access failed: {exc}"
        checks["storage"] = {"status": "FAIL", "error": str(exc)}
        errors.append(err)

    # ── 3. Graphics & Icon Rendering Subsystem ──
    try:
        from PIL import Image

        from ellmos_tray.branding import TrayBranding as DefaultBranding
        from ellmos_tray.icon import generate_tray_icon

        test_branding = branding or DefaultBranding.ellmos()
        icon_img = generate_tray_icon(test_branding, connected=True, mode="safe", use_cache=False)
        assert isinstance(icon_img, Image.Image)
        assert icon_img.size == (64, 64)
        checks["graphics"] = {
            "status": "PASS",
            "pil_available": True,
            "icon_size": icon_img.size,
            "mode": icon_img.mode,
        }
    except Exception as exc:
        err = f"Graphics subsystem verification failed: {exc}"
        checks["graphics"] = {"status": "FAIL", "error": str(exc)}
        errors.append(err)

    # ── 4. Service Endpoints (Control API, GUI, Ollama) ──
    services_info: dict[str, Any] = {}
    service_endpoints = [
        ("control_api", host, port),
        ("gui", host, 8000),
        ("ollama", host, 11434),
    ]
    for s_name, s_host, s_port in service_endpoints:
        reachable = False
        try:
            with socket.create_connection((s_host, s_port), timeout=0.5):
                reachable = True
        except OSError:
            reachable = False
        services_info[s_name] = {"host": s_host, "port": s_port, "reachable": reachable}

    # Offline services are reported as warnings or info, not fatal errors (client works offline)
    if not services_info["control_api"]["reachable"]:
        warnings.append(f"Control API endpoint ({host}:{port}) is offline (Tray operates in Reconnect/Offline mode).")
    checks["services"] = {"status": "PASS", "endpoints": services_info}

    # ── 5. Environment & Platform Details ──
    checks["environment"] = {
        "status": "PASS",
        "platform_system": _sys_platform.system(),
        "platform_release": _sys_platform.release(),
        "architecture": _sys_platform.machine(),
        "python_executable": sys.executable,
    }

    passed = len(errors) == 0
    return DeviceAcceptanceReport(
        passed=passed,
        checks=checks,
        errors=errors,
        warnings=warnings,
    )
