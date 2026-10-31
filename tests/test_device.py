"""
Unit tests for Device Acceptance preflight check and sleep detection.
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

from ellmos_tray.branding import TrayBranding
from ellmos_tray.device import (
    DeviceAcceptanceReport,
    check_device_acceptance,
    detect_sleep_skip,
)


def test_detect_sleep_skip():
    # Normal elapsed time: no sleep skip
    is_sleep, elapsed = detect_sleep_skip(last_timestamp=100.0, expected_interval=5.0)
    # patch time.monotonic to simulate 5 seconds
    with patch("time.monotonic", return_value=105.0):
        is_sleep, elapsed = detect_sleep_skip(last_timestamp=100.0, expected_interval=5.0)
        assert is_sleep is False
        assert elapsed == 5.0

    # Suspended / sleep elapsed time (> 15s)
    with patch("time.monotonic", return_value=130.0):
        is_sleep, elapsed = detect_sleep_skip(last_timestamp=100.0, expected_interval=5.0)
        assert is_sleep is True
        assert elapsed == 30.0


def test_device_acceptance_check_passes(tmp_path):
    branding = TrayBranding.ellmos()
    branding.lock_file = tmp_path / "test.lock"

    # Mock socket connection to services
    with patch("socket.create_connection") as mock_conn:
        mock_conn.return_value.__enter__.return_value = MagicMock()
        report = check_device_acceptance(branding=branding, host="127.0.0.1", port=8081)

    assert isinstance(report, DeviceAcceptanceReport)
    assert report.passed is True
    assert "loopback" in report.checks
    assert report.checks["loopback"]["status"] == "PASS"
    assert report.checks["storage"]["status"] == "PASS"
    assert report.checks["graphics"]["status"] == "PASS"
    assert report.checks["environment"]["status"] == "PASS"

    rep_dict = report.to_dict()
    assert rep_dict["passed"] is True
    assert isinstance(rep_dict["platform"], str)


def test_device_acceptance_handles_storage_failure(tmp_path):
    branding = TrayBranding.ellmos()
    branding.lock_file = tmp_path / "test.lock"

    with patch.object(Path, "write_text", side_effect=PermissionError("Permission denied")):
        report = check_device_acceptance(branding=branding, host="127.0.0.1", port=8081)

    assert report.passed is False
    assert report.checks["storage"]["status"] == "FAIL"
    assert len(report.errors) > 0
