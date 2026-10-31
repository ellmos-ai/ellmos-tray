"""
Unit tests for Windows Store & MSIX readiness preflight check tool.
"""
import json
from pathlib import Path

from tools.store_readiness import (
    check_assets_and_icons,
    check_msix_manifest,
    check_offline_and_loopback,
    check_publisher_placeholders,
    generate_store_assets,
    run_store_readiness_check,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_real_repo_store_readiness_passes():
    passed, report = run_store_readiness_check(REPO_ROOT)
    assert passed is True
    assert report["overall_status"] == "READY"
    assert report["summary"]["failed"] == 0
    assert len(report["errors"]) == 0
    assert report["checks"]["msix_manifest"]["status"] == "PASS"
    assert report["checks"]["publisher_identity"]["status"] == "PASS"
    assert report["checks"]["assets_icons"]["status"] == "PASS"
    assert report["checks"]["wack_criteria"]["status"] == "PASS"
    assert report["checks"]["offline_loopback"]["status"] == "PASS"
    assert report["checks"]["documentation"]["status"] == "PASS"


def test_check_msix_manifest_detects_missing_file(tmp_path):
    ok, errs, _warns = check_msix_manifest(tmp_path)
    assert ok is False
    assert any("store_package.json is missing" in e for e in errs)


def test_check_msix_manifest_detects_missing_fields(tmp_path):
    pkg_file = tmp_path / "store_package.json"
    pkg_file.write_text(json.dumps({"app_name": "IncompleteApp"}), encoding="utf-8")

    ok, errs, _warns = check_msix_manifest(tmp_path)
    assert ok is False
    assert any("publisher" in e for e in errs)
    assert any("identity_name" in e for e in errs)


def test_check_publisher_placeholders(tmp_path):
    pkg_file = tmp_path / "store_package.json"

    # Placeholder case
    pkg_file.write_text(
        json.dumps({
            "publisher": "CN=YourPublisher",
            "identity_name": "Bad Identity With Spaces",
        }),
        encoding="utf-8",
    )
    ok, errs, _warns = check_publisher_placeholders(tmp_path)
    assert ok is False
    assert any("placeholder" in e for e in errs)
    assert any("spaces" in e for e in errs)

    # Valid case
    pkg_file.write_text(
        json.dumps({
            "publisher": "CN=RealCertifiedPublisher",
            "identity_name": "RealPublisher.App",
        }),
        encoding="utf-8",
    )
    ok, errs, _warns = check_publisher_placeholders(tmp_path)
    assert ok is True
    assert len(errs) == 0


def test_generate_store_assets_creates_valid_icons(tmp_path):
    created = generate_store_assets(tmp_path, branding_char="O")
    assert len(created) == 5

    ok, errs, _warns = check_assets_and_icons(tmp_path)
    assert ok is True
    assert len(errs) == 0


def test_check_offline_and_loopback_validates_disclosure(tmp_path):
    listing_file = tmp_path / "STORE_LISTING.md"
    privacy_file = tmp_path / "PRIVACY_POLICY.md"

    # Missing disclosure case (no mention of local address or loopback)
    listing_file.write_text("# App description without network details", encoding="utf-8")
    privacy_file.write_text("# Privacy", encoding="utf-8")
    ok, errs, _warns = check_offline_and_loopback(tmp_path)
    assert ok is False
    assert any("loopback" in e for e in errs)

    # Valid disclosure case
    listing_file.write_text(
        "# App\n\nPrüferhinweise: Connects via loopback (127.0.0.1) for local AI.",
        encoding="utf-8",
    )
    privacy_file.write_text("# Privacy\n\nRein lokaler Betrieb.", encoding="utf-8")
    ok, errs, _warns = check_offline_and_loopback(tmp_path)
    assert ok is True
    assert len(errs) == 0
