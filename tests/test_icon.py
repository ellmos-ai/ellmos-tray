"""
Unit tests for dynamic tray icon rendering and color calculations.
"""
from PIL import Image
from ellmos_tray.branding import TrayBranding
from ellmos_tray.icon import generate_tray_icon, get_status_color


def test_status_color_resolution():
    branding = TrayBranding()

    # Processing takes precedence
    assert get_status_color(branding, connected=True, mode="safe", is_processing=True) == branding.color_processing
    assert get_status_color(branding, connected=False, mode="safe", is_processing=True) == branding.color_processing

    # Full mode when connected
    assert get_status_color(branding, connected=True, mode="full", is_processing=False) == branding.color_full_mode

    # Safe mode when connected
    assert get_status_color(branding, connected=True, mode="safe", is_processing=False) == branding.color_connected

    # Disconnected
    assert get_status_color(branding, connected=False, mode="safe", is_processing=False) == branding.color_disconnected


def test_generate_tray_icon_rendering():
    branding = TrayBranding.ellmos()
    icon_img = generate_tray_icon(branding, connected=True, mode="safe")

    assert isinstance(icon_img, Image.Image)
    assert icon_img.size == (64, 64)
    assert icon_img.mode == "RGBA"


def test_generate_tray_icon_bach():
    branding = TrayBranding.bach()
    icon_img = generate_tray_icon(branding, connected=True, mode="full")

    assert isinstance(icon_img, Image.Image)
    assert icon_img.size == (64, 64)
