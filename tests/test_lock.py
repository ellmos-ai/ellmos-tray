"""
Unit tests for single-instance lock mechanics.
"""
from ellmos_tray.lock import acquire_single_instance_lock, release_single_instance_lock


def test_acquire_creates_parent_dir(tmp_path):
    lock_path = tmp_path / "deep" / "nested" / "dir" / "test.lock"
    handle = acquire_single_instance_lock(lock_path)
    assert handle is not None
    assert lock_path.is_file()
    release_single_instance_lock(handle)


def test_mutual_exclusion(tmp_path):
    lock_path = tmp_path / "app.lock"
    handle1 = acquire_single_instance_lock(lock_path)
    assert handle1 is not None

    # Second acquisition on the same file MUST fail (return None)
    handle2 = acquire_single_instance_lock(lock_path)
    assert handle2 is None

    # Releasing the first handle allows subsequent acquisition
    release_single_instance_lock(handle1)

    handle3 = acquire_single_instance_lock(lock_path)
    assert handle3 is not None
    release_single_instance_lock(handle3)
