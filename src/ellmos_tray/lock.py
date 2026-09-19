"""
Single-instance lock mechanics for ellmos-tray.
Guarantees fail-closed, crash-safe single instance enforcement via OS byte-range or flock locks.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional


def acquire_single_instance_lock(lock_path: Path) -> Optional[Any]:
    """Return an open, exclusively locked handle -- or None if another tray holds it.

    Single-instance contract for the tray: the lock is an OS-held byte-range
    (Windows, msvcrt) or flock (POSIX) lock on an open handle, so the OS drops it
    when the holder dies. A crashed tray therefore never leaves a stale lock
    behind, and no PID guessing is needed. Keep the returned handle alive for
    the tray's whole lifetime.
    """
    try:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        handle = open(lock_path, "a+b")
    except OSError:
        return None

    try:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        try:
            handle.close()
        except OSError:
            pass
        return None

    return handle


def release_single_instance_lock(handle: Optional[Any]) -> None:
    """Releases the locked file handle and closes it cleanly."""
    if handle is None:
        return
    try:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass
    finally:
        try:
            handle.close()
        except OSError:
            pass
