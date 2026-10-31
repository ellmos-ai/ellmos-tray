"""
ellmos-tray: Pluggable, modular system tray and quick control client for ELLMOS, BACH, and OCEAN.
"""
from ellmos_tray.app import ConnectionState, TrayApp
from ellmos_tray.branding import TrayBranding
from ellmos_tray.cache import IconCache, ThumbnailCache
from ellmos_tray.client import ControlApiClient
from ellmos_tray.device import DeviceAcceptanceReport, check_device_acceptance
from ellmos_tray.icon import generate_tray_icon, get_status_color
from ellmos_tray.lock import acquire_single_instance_lock, release_single_instance_lock
from ellmos_tray.process import BackendProcessManager, ProcessOwnership
from ellmos_tray.prompts import PromptManager
from ellmos_tray.runner import LegacyBachIdleRunner, PassiveTaskDelegate, TaskExecutionDelegate

__version__ = "0.1.2"

__all__ = [
    "BackendProcessManager",
    "ConnectionState",
    "ControlApiClient",
    "DeviceAcceptanceReport",
    "IconCache",
    "LegacyBachIdleRunner",
    "PassiveTaskDelegate",
    "ProcessOwnership",
    "PromptManager",
    "TaskExecutionDelegate",
    "ThumbnailCache",
    "TrayApp",
    "TrayBranding",
    "__version__",
    "acquire_single_instance_lock",
    "check_device_acceptance",
    "generate_tray_icon",
    "get_status_color",
    "release_single_instance_lock",
]
