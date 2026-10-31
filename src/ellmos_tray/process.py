"""
Process ownership and lifecycle management for ellmos-tray.
Distinguishes between attached (pre-existing) backends and managed child processes,
ensuring that tray shutdown only terminates child processes it spawned itself.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ellmos_tray.client import ControlApiClient


class ProcessOwnership(StrEnum):
    """Lifecycle ownership of the Control API backend process."""

    ATTACHED = "attached"          # Backend was already running; tray merely attached
    SPAWNED = "spawned"            # Backend was launched by tray as a managed child
    NOT_RUNNING = "not_running"    # Backend is offline and no child process exists
    UNKNOWN = "unknown"            # Ownership not yet evaluated


class BackendProcessManager:
    """Manages start/attach detection and graceful shutdown of the backend service."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8081,
        client: ControlApiClient | None = None,
    ):
        self.host = host
        self.port = port
        self.client = client
        self.ownership = ProcessOwnership.UNKNOWN
        self.child_process: subprocess.Popen[Any] | None = None
        self._spawn_command: list[str] | None = None
        self._spawn_time: float | None = None

    @property
    def is_managed(self) -> bool:
        """Returns True if the backend process was spawned by this tray and is still alive."""
        return (
            self.ownership == ProcessOwnership.SPAWNED
            and self.child_process is not None
            and self.child_process.poll() is None
        )

    def detect_or_attach(self) -> ProcessOwnership:
        """Detects whether backend is online, and classifies it as ATTACHED or SPAWNED."""
        is_online = False
        if self.client:
            status = self.client.get_status()
            is_online = bool(status and "backend" in status)
        else:
            is_online = self._probe_socket(self.host, self.port)

        if is_online:
            if self.child_process is not None and self.child_process.poll() is None:
                self.ownership = ProcessOwnership.SPAWNED
            else:
                self.ownership = ProcessOwnership.ATTACHED
        else:
            if self.child_process is not None and self.child_process.poll() is None:
                # Spawned, but not yet listening or crashed
                self.ownership = ProcessOwnership.SPAWNED
            else:
                self.ownership = ProcessOwnership.NOT_RUNNING

        return self.ownership

    def spawn_backend(
        self,
        command: list[str] | str,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        wait_ready_sec: float = 3.0,
    ) -> bool:
        """Launches the backend as a child process if it is not already running."""
        # 1. Check if backend is already running
        current = self.detect_or_attach()
        if current == ProcessOwnership.ATTACHED:
            # Backend already exists; do not spawn a second instance
            return True

        # 2. Prepare command and environment
        cmd_args = [command] if isinstance(command, str) else list(command)
        run_env = os.environ.copy()
        if env:
            run_env.update(env)

        creationflags = 0
        if sys.platform == "win32":
            # Detach console window if needed
            creationflags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0

        try:
            proc = subprocess.Popen(
                cmd_args,
                cwd=str(cwd) if cwd else None,
                env=run_env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creationflags,
            )
            self.child_process = proc
            self.ownership = ProcessOwnership.SPAWNED
            self._spawn_command = cmd_args
            self._spawn_time = time.time()
        except OSError:
            self.ownership = ProcessOwnership.NOT_RUNNING
            return False

        # 3. Wait for readiness if requested
        if wait_ready_sec > 0:
            deadline = time.time() + wait_ready_sec
            while time.time() < deadline:
                if proc.poll() is not None:
                    # Child exited prematurely
                    self.ownership = ProcessOwnership.NOT_RUNNING
                    return False
                if self.client and self.client.get_status():
                    return True
                time.sleep(0.2)

        return proc.poll() is None

    def shutdown(self, grace_period: float = 3.0) -> bool:
        """Terminates the backend ONLY if it is an owned child process.
        
        If the backend was attached (pre-existing), it is left untouched.
        Returns True if a child process was shut down, False otherwise.
        """
        if self.ownership != ProcessOwnership.SPAWNED or self.child_process is None:
            # Not an owned child process: leave untouched
            return False

        proc = self.child_process
        self.child_process = None
        self.ownership = ProcessOwnership.NOT_RUNNING

        if proc.poll() is not None:
            return True

        try:
            proc.terminate()
            proc.wait(timeout=grace_period)
        except (subprocess.TimeoutExpired, OSError):
            try:
                proc.kill()
                proc.wait(timeout=1.0)
            except Exception:
                pass

        return True

    def get_info(self) -> dict[str, Any]:
        """Returns structured metadata about current process ownership."""
        pid = self.child_process.pid if self.child_process and self.child_process.poll() is None else None
        return {
            "ownership": self.ownership.value,
            "is_managed": self.is_managed,
            "pid": pid,
            "host": self.host,
            "port": self.port,
            "spawn_time": self._spawn_time,
        }

    @staticmethod
    def _probe_socket(host: str, port: int, timeout: float = 1.0) -> bool:
        """Quick socket check for open TCP port."""
        import socket
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False
