"""
Unit tests for TaskExecutionDelegate and LegacyBachIdleRunner.
"""
from unittest.mock import MagicMock

from ellmos_tray.runner import LegacyBachIdleRunner, PassiveTaskDelegate


def test_passive_delegate():
    delegate = PassiveTaskDelegate(enabled=True)
    assert delegate.is_enabled is True
    assert delegate.toggle_enabled() is False
    assert delegate.is_enabled is False


def test_idle_runner_does_not_disarm_on_active_sessions():
    runner = LegacyBachIdleRunner(enabled=True)
    runner.consecutive_idle = 5

    app = MagicMock()
    app.slots = {"buddha_always_on": {"enabled": True, "backend": "ollama"}}
    app.state = {"active_sessions": 2, "sessions": 5}

    runner.on_poll_tick(app)

    assert runner.consecutive_idle == 6


def test_idle_runner_respects_slot_cooldown_pause():
    runner = LegacyBachIdleRunner(enabled=True)
    runner.consecutive_idle = 5

    app = MagicMock()
    app.slots = {
        "buddha_always_on": {
            "enabled": True,
            "backend": "ollama",
            "pause_info": {"is_paused": True, "remaining_minutes": 5},
        }
    }
    app.state = {"active_sessions": 0}

    runner.on_poll_tick(app)

    assert runner.consecutive_idle == 5


def test_idle_runner_guards_against_cloud_backends():
    runner = LegacyBachIdleRunner(enabled=True)
    runner.consecutive_idle = 5

    for cloud_backend in ("claude", "claude-api", "openai", "codex", "openrouter", "ollama-cloud"):
        app = MagicMock()
        app.slots = {
            "buddha_always_on": {
                "enabled": True,
                "backend": cloud_backend,
            }
        }
        app.state = {"active_sessions": 0}

        runner.on_poll_tick(app)
        assert runner.consecutive_idle == 5, (
            f"Cloud backend '{cloud_backend}' should not advance idle worker"
        )
