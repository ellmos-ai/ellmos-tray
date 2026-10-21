"""
Entry point for running ellmos-tray from the command line.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from ellmos_tray.app import TrayApp
from ellmos_tray.branding import TrayBranding
from ellmos_tray.client import ControlApiClient
from ellmos_tray.lock import acquire_single_instance_lock
from ellmos_tray.runner import LegacyBachIdleRunner, PassiveTaskDelegate


def main() -> None:
    parser = argparse.ArgumentParser(description="ELLMOS & BACH Unified System Tray")
    parser.add_argument("--host", default="127.0.0.1", help="Control API Host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8081, help="Control API Port (default: 8081)")
    parser.add_argument(
        "--gui-url", default=None,
        help="Separate GUI-Basisadresse einschließlich eines optionalen Basispfads",
    )
    parser.add_argument(
        "--brand",
        choices=["ellmos", "bach", "ocean"],
        default="ellmos",
        help="Branding preset to use (default: ellmos)",
    )
    parser.add_argument(
        "--smoke-promptboard",
        action="store_true",
        help="Print PromptBoard tray detection smoke data and exit",
    )
    parser.add_argument(
        "--idle-worker",
        choices=["auto", "on", "off", "legacy"],
        default="auto",
        help="Backend observer mode; only 'legacy' starts a local idle executor (default: auto)",
    )
    parser.add_argument(
        "--repo-dir",
        type=Path,
        default=None,
        help="Repository root for legacy worker auto-commits",
    )

    args = parser.parse_args()

    # Resolve branding
    if args.brand == "bach":
        branding = TrayBranding.bach()
    elif args.brand == "ocean":
        branding = TrayBranding.ocean()
    else:
        branding = TrayBranding.ellmos()

    # Determine runner
    if args.idle_worker == "legacy":
        runner = LegacyBachIdleRunner(repo_dir=args.repo_dir)
    elif args.idle_worker == "off":
        runner = PassiveTaskDelegate(enabled=False)
    else:
        runner = PassiveTaskDelegate(enabled=True)

    gui_url = args.gui_url
    if not gui_url and args.brand == "ocean":
        gui_url = os.environ.get("OCEAN_GUI_URL")
    client = ControlApiClient(host=args.host, port=args.port, gui_url=gui_url)
    tray = TrayApp(branding=branding, client=client, runner=runner)

    if args.smoke_promptboard:
        print(json.dumps(tray.prompt_manager.smoke_snapshot(), ensure_ascii=False, indent=2))
        return

    lock_file = branding.get_lock_file()
    lock = acquire_single_instance_lock(lock_file)
    if lock is None:
        print(
            f"{branding.app_title} läuft bereits (Single-Instance-Lock: {lock_file}).",
            file=sys.stderr,
        )
        sys.exit(3)

    tray._instance_lock = lock
    try:
        tray.run()
    finally:
        tray.stop()


if __name__ == "__main__":
    main()
