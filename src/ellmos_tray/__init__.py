"""
ellmos-tray: Pluggable, modular system tray and quick control client for ELLMOS and BACH.
"""
from ellmos_tray.app import TrayApp
from ellmos_tray.branding import TrayBranding
from ellmos_tray.client import ControlApiClient
from ellmos_tray.icon import generate_tray_icon, get_status_color
from ellmos_tray.lock import acquire_single_instance_lock, release_single_instance_lock
from ellmos_tray.prompts import PromptManager
from ellmos_tray.runner import LegacyBachIdleRunner, PassiveTaskDelegate, TaskExecutionDelegate

__version__ = "0.1.0"

__all__ = [
    "TrayApp",
    "TrayBranding",
    "ControlApiClient",
    "generate_tray_icon",
    "get_status_color",
    "acquire_single_instance_lock",
    "release_single_instance_lock",
    "PromptManager",
    "TaskExecutionDelegate",
    "PassiveTaskDelegate",
    "LegacyBachIdleRunner",
    "__version__",
]
