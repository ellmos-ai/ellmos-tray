"""
Unit tests for TaskExecutionDelegate and LegacyBachIdleRunner.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

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


def test_detect_repo_dir_darwin_uses_user_neutral_home(monkeypatch, tmp_path):
    fake_bach = tmp_path / "services" / "bach"
    fake_bach.mkdir(parents=True)
    monkeypatch.delenv("BACH_REPO_DIR", raising=False)
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))

    runner = LegacyBachIdleRunner(enabled=False)
    assert runner.repo_dir == fake_bach


def test_resolve_role_sanitizes_untrusted_assignee():
    role_id, display, _ = LegacyBachIdleRunner._resolve_role("agent:dev&ops/../test#1")
    assert role_id == "devopstest1"
    assert "/" not in role_id and "&" not in role_id and "#" not in role_id
    assert display == "Devopstest1"


def test_auto_commit_task_uses_end_of_options_and_filters_traversal(monkeypatch, tmp_path):
    runner = LegacyBachIdleRunner(repo_dir=tmp_path, enabled=False)
    diff_proc = MagicMock(
        stdout="-dash-flag-file.py\n../outside.py\nsystem/data/state.db\nsrc/ok.py\n"
    )
    ok_proc = MagicMock(returncode=0, stdout="")

    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    saved_pytest = sys.modules.pop("pytest", None)
    try:
        with patch("subprocess.run", side_effect=[diff_proc, ok_proc, ok_proc]) as mock_run:
            runner._auto_commit_task(99, "Fix line 1\r\nTrailer: injected")
    finally:
        if saved_pytest is not None:
            sys.modules["pytest"] = saved_pytest

    assert mock_run.call_count == 3
    git_add_cmd = mock_run.call_args_list[1][0][0]
    git_commit_cmd = mock_run.call_args_list[2][0][0]
    assert git_add_cmd == ["git", "add", "--", "-dash-flag-file.py", "src/ok.py"]
    assert git_commit_cmd == ["git", "commit", "-m", "bach(buddha): #99 Fix line 1 Trailer: injected"]
