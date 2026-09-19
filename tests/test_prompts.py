"""
Unit tests for PromptManager and PromptBoard library loading.
"""
import json
from unittest.mock import patch
from ellmos_tray.prompts import DEFAULT_PROMPTS, PromptManager


def test_default_prompts_loaded_when_no_files(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.delenv("ELLMOS_PROMPTBOARD_LIBRARY", raising=False)
    monkeypatch.delenv("BACH_PROMPTBOARD_LIBRARY", raising=False)

    pm = PromptManager()
    assert pm.prompt_source == "defaults"
    assert "Aufgaben" in pm.prompts
    assert pm.prompts["Aufgaben"] == DEFAULT_PROMPTS["Aufgaben"]


def test_load_native_prompt_file(tmp_path):
    prompt_file = tmp_path / "prompts.json"
    prompt_file.write_text(
        json.dumps({
            "CustomCategory": {
                "P1": "Prompt 1 text",
                "P2": "Prompt 2 text",
            }
        }),
        encoding="utf-8",
    )

    pm = PromptManager(custom_library_path=prompt_file)
    assert pm.prompt_source == str(prompt_file)
    assert pm.prompts["CustomCategory"]["P1"] == "Prompt 1 text"


def test_load_promptboard_library_format(tmp_path):
    library_file = tmp_path / "library.json"
    library_file.write_text(
        json.dumps({
            "items": [
                {
                    "name": "Analyze Code",
                    "content": "Analyze the selected code.",
                    "category": "Development",
                },
                {
                    "name": "Write Tests",
                    "content": "Generate comprehensive unit tests.",
                    "category": "Development",
                },
            ]
        }),
        encoding="utf-8",
    )

    pm = PromptManager(custom_library_path=library_file)
    assert pm.prompt_source == str(library_file)
    assert "Development" in pm.prompts
    assert pm.prompts["Development"]["Analyze Code"] == "Analyze the selected code."
    assert pm.prompts["Development"]["Write Tests"] == "Generate comprehensive unit tests."


def test_smoke_snapshot_reporting(tmp_path):
    library_file = tmp_path / "library.json"
    library_file.write_text(
        json.dumps({
            "items": [
                {"name": "Smoke", "content": "Test text", "category": "SmokeCat"}
            ]
        }),
        encoding="utf-8",
    )

    pm = PromptManager(custom_library_path=library_file)
    snapshot = pm.smoke_snapshot()

    assert snapshot["prompt_source"] == str(library_file)
    assert snapshot["using_default_prompts"] is False
    assert snapshot["prompt_count"] == 1
    assert "SmokeCat" in snapshot["prompt_categories"]


def test_clipboard_copy():
    with patch("subprocess.run") as mock_run:
        res = PromptManager.copy_to_clipboard("Test copy text")
        assert res is True
        mock_run.assert_called_once()
