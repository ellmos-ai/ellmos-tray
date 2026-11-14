"""
Contract tests for repository metadata, PEP 561 typing marker, and release hygiene.
"""
from __future__ import annotations

import json
import tomllib
from pathlib import Path

import ellmos_tray

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_pyproject_version_and_typing_metadata() -> None:
    pyproject_path = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    project = data["project"]
    assert project["name"] == "ellmos-tray"
    assert project["version"] == ellmos_tray.__version__
    assert "Typing :: Typed" in project["classifiers"]

    package_data = data["tool"]["setuptools"]["package-data"]
    assert "py.typed" in package_data["ellmos_tray"]
    assert (REPO_ROOT / "src" / "ellmos_tray" / "py.typed").is_file()


def test_v2_module_manifest_consistency() -> None:
    pyproject_data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    manifest = json.loads((REPO_ROOT / "ellmos-module.v2.json").read_text(encoding="utf-8"))

    assert manifest["schema"] == "ellmos.module.v2"
    assert manifest["id"] == "ellmos-tray"
    assert manifest["package"] == "ellmos-tray"
    assert manifest["version"] == pyproject_data["project"]["version"]
    assert manifest["category"] == "runtime"
    assert manifest["kind"] == "ui"
    assert manifest["visibility"] == "public"
    assert set(["ui", "cli", "library"]).issubset(set(manifest["surfaces"]))
    assert manifest["entrypoints"]["cli"] == "ellmos-tray = ellmos_tray.__main__:main"
    assert manifest["source_of_truth"]["path"] == "."


def test_release_hygiene_docs_and_gitignore() -> None:
    for filename in ("README.md", "LICENSE", "SECURITY.md", "CHANGELOG.md", "TODO.md"):
        path = REPO_ROOT / filename
        assert path.is_file(), f"Missing required root file: {filename}"
        assert path.stat().st_size > 0, f"Empty root file: {filename}"

    todo_text = (REPO_ROOT / "TODO.md").read_text(encoding="utf-8")
    assert "## STATUS" in todo_text
    assert "| Category | Status | Notes |" in todo_text

    gitignore_text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    for entry in ("__pycache__", "*.pyc", ".env", "*.db", ".venv/", ".idea/", ".vscode/", "data/"):
        assert entry in gitignore_text or entry.rstrip("/") in gitignore_text
