"""
Unit tests for ConnectionState transitions, reconnect exponential backoff,
adaptive polling, and sleep/wake recovery.
"""
from unittest.mock import MagicMock

from ellmos_tray.app import ConnectionState, TrayApp


def test_connection_state_transitions(mock_pystray):
    app = TrayApp()
    app.client.get_status = MagicMock(return_value={"backend": "ollama", "mode": "safe"})
    app.client.get_backends = MagicMock(return_value={})
    app.client.get_models = MagicMock(return_value={"models": []})
    app.client.get_slots = MagicMock(return_value={"ok": True})
    app.client.check_url = MagicMock(return_value=True)

    # 1. Initial refresh -> CONNECTED
    app.refresh()
    assert app.connection_state == ConnectionState.CONNECTED
    assert app.state["connected"] is True
    assert app.reconnect_delay == app.min_reconnect_delay

    # 2. Transient failures < max_status_failures (3)
    app.client.get_status.return_value = None
    app.refresh()  # failure 1
    assert app.connection_state == ConnectionState.DISCONNECTED
    assert app.state["connected"] is True  # threshold not yet breached

    app.refresh()  # failure 2
    assert app.connection_state == ConnectionState.DISCONNECTED
    assert app.state["connected"] is True

    # 3. Third failure reaches max_status_failures -> RECONNECTING
    app.refresh()  # failure 3
    assert app.connection_state == ConnectionState.RECONNECTING
    assert app.state["connected"] is False
    assert app.reconnect_delay > app.min_reconnect_delay

    # 4. Success restores connection -> CONNECTED
    app.client.get_status.return_value = {"backend": "ollama", "mode": "safe"}
    app.notify = MagicMock()
    app.refresh()
    assert app.connection_state == ConnectionState.CONNECTED
    assert app.state["connected"] is True
    assert app.reconnect_delay == app.min_reconnect_delay
    app.notify.assert_called_once()
    assert "wiederhergestellt" in app.notify.call_args[0][0]


def test_adaptive_poll_interval():
    app = TrayApp(poll_interval=5)
    app.connection_state = ConnectionState.CONNECTED

    # Normal connected & idle interval
    assert app.current_poll_interval == 5.0

    # When runner is actively processing a task
    app.runner.is_processing = MagicMock(return_value=True)
    assert app.current_poll_interval == 2.0  # active_poll_interval

    # When reconnecting with backed off delay
    app.runner.is_processing.return_value = False
    app.connection_state = ConnectionState.RECONNECTING
    app.reconnect_delay = 12.0
    assert app.current_poll_interval == 12.0


def test_sleep_recovery_handling():
    app = TrayApp()
    app.backend_manager.detect_or_attach = MagicMock()
    app.notify = MagicMock()
    app.reconnect_delay = 20.0

    app.handle_sleep_recovery(elapsed=45.0)

    assert app.sleep_recoveries_count == 1
    assert app.reconnect_delay == app.min_reconnect_delay
    app.backend_manager.detect_or_attach.assert_called_once()
    app.notify.assert_called_once()
    assert "Aufwachphase" in app.notify.call_args[0][0]
