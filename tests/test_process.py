"""
Unit tests for BackendProcessManager and process ownership contracts.
"""
from unittest.mock import MagicMock, patch

from ellmos_tray.process import BackendProcessManager, ProcessOwnership


def test_process_ownership_enum_values():
    assert ProcessOwnership.ATTACHED == "attached"
    assert ProcessOwnership.SPAWNED == "spawned"
    assert ProcessOwnership.NOT_RUNNING == "not_running"
    assert ProcessOwnership.UNKNOWN == "unknown"


def test_detect_or_attach_attached_when_client_responds():
    client = MagicMock()
    client.get_status.return_value = {"backend": "ollama", "mode": "safe"}

    mgr = BackendProcessManager(host="127.0.0.1", port=8081, client=client)
    ownership = mgr.detect_or_attach()

    assert ownership == ProcessOwnership.ATTACHED
    assert mgr.is_managed is False
    assert mgr.get_info()["ownership"] == "attached"
    assert mgr.get_info()["pid"] is None


def test_detect_or_attach_not_running_when_client_fails():
    client = MagicMock()
    client.get_status.return_value = None

    mgr = BackendProcessManager(host="127.0.0.1", port=8081, client=client)
    with patch.object(mgr, "_probe_socket", return_value=False):
        ownership = mgr.detect_or_attach()

    assert ownership == ProcessOwnership.NOT_RUNNING
    assert mgr.is_managed is False


def test_spawn_backend_skips_spawn_if_already_attached():
    client = MagicMock()
    client.get_status.return_value = {"backend": "ollama"}

    mgr = BackendProcessManager(host="127.0.0.1", port=8081, client=client)
    with patch("subprocess.Popen") as mock_popen:
        success = mgr.spawn_backend(["python", "-m", "backend"])
        assert success is True
        mock_popen.assert_not_called()
        assert mgr.ownership == ProcessOwnership.ATTACHED
        assert mgr.is_managed is False


def test_spawn_backend_launches_child_when_offline():
    client = MagicMock()
    # Initially offline, then comes online
    client.get_status.side_effect = [None, {"backend": "ollama"}]

    mgr = BackendProcessManager(host="127.0.0.1", port=8081, client=client)
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None
    mock_proc.pid = 9999

    with patch("subprocess.Popen", return_value=mock_proc) as mock_popen:
        success = mgr.spawn_backend(["python", "-m", "backend"], wait_ready_sec=0.5)

        assert success is True
        mock_popen.assert_called_once()
        assert mgr.ownership == ProcessOwnership.SPAWNED
        assert mgr.is_managed is True
        assert mgr.get_info()["pid"] == 9999


def test_shutdown_only_terminates_spawned_child():
    client = MagicMock()
    mgr = BackendProcessManager(host="127.0.0.1", port=8081, client=client)

    # 1. Attached case: do not terminate!
    mgr.ownership = ProcessOwnership.ATTACHED
    mgr.child_process = None

    killed = mgr.shutdown()
    assert killed is False
    assert mgr.ownership == ProcessOwnership.ATTACHED

    # 2. Spawned child process case: terminate cleanly
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None
    mgr.ownership = ProcessOwnership.SPAWNED
    mgr.child_process = mock_proc

    killed = mgr.shutdown(grace_period=0.1)
    assert killed is True
    mock_proc.terminate.assert_called_once()
    mock_proc.wait.assert_called()
    assert mgr.child_process is None
    assert mgr.ownership == ProcessOwnership.NOT_RUNNING
