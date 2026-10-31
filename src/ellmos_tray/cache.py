"""
Performance caching for icons, fonts, and desktop thumbnails.
Prevents redundant PIL canvas allocations, disk font parsing, and repaints
across polling ticks and tray menu refreshes.
"""
from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from PIL import Image

    from ellmos_tray.branding import TrayBranding


class IconCache:
    """Thread-safe cache for generated tray icons and fonts."""

    _instance: IconCache | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._cache: dict[tuple[Any, ...], Image.Image] = {}
        self._font_cache: dict[tuple[str, int], Any] = {}
        self._hits = 0
        self._misses = 0

    @classmethod
    def get_instance(cls) -> IconCache:
        """Returns the process-wide IconCache singleton."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def get_font(self, font_name: str | None = None, size: int = 32) -> Any:
        """Retrieves or loads a cached ImageFont."""
        from PIL import ImageFont

        target_font = font_name or self._default_font_name()
        key = (target_font, size)
        with self._lock:
            if key in self._font_cache:
                return self._font_cache[key]

        font: Any = None
        try:
            font = ImageFont.truetype(target_font, size)
        except OSError:
            try:
                font = ImageFont.load_default()
            except Exception:
                font = None

        with self._lock:
            self._font_cache[key] = font
        return font

    @staticmethod
    def _default_font_name() -> str:
        if sys.platform == "darwin":
            return "/System/Library/Fonts/Helvetica.ttc"
        if sys.platform == "win32":
            return "arial"
        return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    def get_or_render_icon(
        self,
        branding: TrayBranding,
        connected: bool,
        mode: str = "safe",
        is_processing: bool = False,
        override_char: str | None = None,
    ) -> Image.Image:
        """Retrieves a cached icon or renders a new one if not present in cache."""
        from ellmos_tray.icon import generate_tray_icon_uncached

        char = override_char if override_char is not None else branding.icon_char
        custom_icon_path = str(branding.icon_path) if branding.icon_path else ""

        cache_key = (
            branding.app_id,
            custom_icon_path,
            connected,
            mode,
            is_processing,
            char,
            branding.color_connected,
            branding.color_full_mode,
            branding.color_processing,
            branding.color_disconnected,
        )

        with self._lock:
            if cache_key in self._cache:
                self._hits += 1
                return self._cache[cache_key]

        # Render without cache
        rendered = generate_tray_icon_uncached(
            branding=branding,
            connected=connected,
            mode=mode,
            is_processing=is_processing,
            override_char=override_char,
            font_provider=self.get_font,
        )

        with self._lock:
            self._misses += 1
            self._cache[cache_key] = rendered

        return rendered

    def clear(self) -> None:
        """Clears all cached icons and fonts."""
        with self._lock:
            self._cache.clear()
            self._font_cache.clear()
            self._hits = 0
            self._misses = 0

    @property
    def stats(self) -> dict[str, int]:
        with self._lock:
            return {
                "cached_icons": len(self._cache),
                "cached_fonts": len(self._font_cache),
                "hits": self._hits,
                "misses": self._misses,
            }


class ThumbnailCache:
    """Thread-safe cache for downscaled previews and image thumbnails."""

    _instance: ThumbnailCache | None = None
    _lock = threading.Lock()

    def __init__(self, max_items: int = 128) -> None:
        self._thumbnails: dict[tuple[str, int, int], Image.Image] = {}
        self._max_items = max_items

    @classmethod
    def get_instance(cls) -> ThumbnailCache:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def get_thumbnail(
        self,
        image_or_path: str | Path | Any,
        size: tuple[int, int] = (64, 64),
    ) -> Any:
        """Returns a cached thumbnail image scaled to target size."""
        from PIL import Image

        key_source = str(image_or_path) if isinstance(image_or_path, (str, Path)) else id(image_or_path)
        cache_key = (str(key_source), size[0], size[1])

        with self._lock:
            if cache_key in self._thumbnails:
                return self._thumbnails[cache_key]

        # Load and scale
        img: Image.Image
        if isinstance(image_or_path, (str, Path)):
            path = Path(image_or_path)
            if not path.exists():
                return None
            img = Image.open(path).convert("RGBA")
        elif hasattr(image_or_path, "copy"):
            img = image_or_path.copy()
        else:
            return None

        # Resize with high quality resampling
        resample = getattr(Image, "Resampling", Image).LANCZOS
        thumb = img.resize(size, resample=resample)

        with self._lock:
            if len(self._thumbnails) >= self._max_items:
                # Evict oldest entry
                self._thumbnails.pop(next(iter(self._thumbnails)))
            self._thumbnails[cache_key] = thumb

        return thumb

    def clear(self) -> None:
        with self._lock:
            self._thumbnails.clear()

    @property
    def count(self) -> int:
        with self._lock:
            return len(self._thumbnails)
