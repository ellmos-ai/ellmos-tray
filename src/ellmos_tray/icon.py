"""
Dynamic icon generation for ellmos-tray.
Generates multi-platform RGBA icons indicating connectivity, execution mode, and activity.
"""
from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from PIL import Image
    from ellmos_tray.branding import TrayBranding


def get_status_color(
    branding: TrayBranding,
    connected: bool,
    mode: str = "safe",
    is_processing: bool = False,
) -> tuple[int, int, int, int]:
    """Resolves the appropriate status color based on connectivity and state."""
    if is_processing:
        return branding.color_processing
    if connected:
        if mode == "full":
            return branding.color_full_mode
        return branding.color_connected
    return branding.color_disconnected


def generate_tray_icon(
    branding: TrayBranding,
    connected: bool,
    mode: str = "safe",
    is_processing: bool = False,
    override_char: Optional[str] = None,
) -> Image.Image:
    """Renders a 64x64 RGBA icon displaying the branding character on a status-colored background."""
    from PIL import Image, ImageDraw, ImageFont

    if branding.icon_path and branding.icon_path.exists():
        try:
            custom_img = Image.open(branding.icon_path).convert("RGBA")
            return custom_img.resize((64, 64))
        except Exception:
            pass

    color = get_status_color(
        branding,
        connected=connected,
        mode=mode,
        is_processing=is_processing,
    )
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([4, 4, 60, 60], radius=12, fill=color)

    char = override_char if override_char is not None else branding.icon_char
    font: Any = None
    try:
        if sys.platform == "darwin":
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        elif sys.platform == "win32":
            font = ImageFont.truetype("arial", 32)
        else:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except (OSError, IOError):
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

    if font:
        try:
            # Anchor or center calculation
            bbox = font.getbbox(char)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            draw.text(((64 - text_w) / 2, (60 - text_h) / 2), char, fill="white", font=font)
        except Exception:
            draw.text((16, 12), char, fill="white", font=font)
    else:
        draw.text((16, 14), char, fill="white")

    return img
