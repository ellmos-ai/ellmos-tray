"""
Unit tests for IconCache and ThumbnailCache performance optimization.
"""
from PIL import Image

from ellmos_tray.branding import TrayBranding
from ellmos_tray.cache import IconCache, ThumbnailCache
from ellmos_tray.icon import generate_tray_icon


def test_icon_cache_reuse_and_stats():
    cache = IconCache()
    cache.clear()
    branding = TrayBranding.ellmos()

    # First access: cache miss
    img1 = cache.get_or_render_icon(branding, connected=True, mode="safe", is_processing=False)
    assert isinstance(img1, Image.Image)
    stats1 = cache.stats
    assert stats1["misses"] == 1
    assert stats1["hits"] == 0
    assert stats1["cached_icons"] == 1

    # Second access with identical parameters: cache hit
    img2 = cache.get_or_render_icon(branding, connected=True, mode="safe", is_processing=False)
    assert img1 is img2
    stats2 = cache.stats
    assert stats2["hits"] == 1
    assert stats2["misses"] == 1

    # State change: new entry cached
    img3 = cache.get_or_render_icon(branding, connected=False, mode="safe", is_processing=False)
    assert img3 is not img1
    stats3 = cache.stats
    assert stats3["misses"] == 2
    assert stats3["cached_icons"] == 2


def test_generate_tray_icon_uses_cache():
    branding = TrayBranding.ocean()
    img_a = generate_tray_icon(branding, connected=True, mode="safe", use_cache=True)
    img_b = generate_tray_icon(branding, connected=True, mode="safe", use_cache=True)
    assert img_a is img_b


def test_thumbnail_cache(tmp_path):
    thumb_cache = ThumbnailCache(max_items=5)
    thumb_cache.clear()

    # Create dummy image
    test_img_path = tmp_path / "sample.png"
    img = Image.new("RGBA", (200, 200), (255, 0, 0, 255))
    img.save(test_img_path)

    # First fetch
    t1 = thumb_cache.get_thumbnail(test_img_path, size=(64, 64))
    assert t1.size == (64, 64)
    assert thumb_cache.count == 1

    # Second fetch returns cached
    t2 = thumb_cache.get_thumbnail(test_img_path, size=(64, 64))
    assert t1 is t2

    # Clear
    thumb_cache.clear()
    assert thumb_cache.count == 0
