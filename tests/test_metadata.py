"""
Contract tests for repository metadata, PEP 561/639 packaging, SBOM, security SLAs, and hygiene.
"""
from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

import ellmos_tray

REPO_ROOT = Path(__file__).resolve().parent.parent

# Username-neutral personal home-directory detector across Windows, macOS, and Linux
PERSONAL_HOME_RE = re.compile(
    r"(?:[A-Za-z]:[\\/]+Users[\\/]+|/(?:Users|home)/)"
    r"(?!Public\b|Default\b|Shared\b|runner\b|ubuntu\b|root\b)"
    r"[A-Za-z0-9._-]{3,}[\\/]+"
)

SECRET_TOKEN_RE = re.compile(
    r"(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-proj-[A-Za-z0-9_-]{20,}"
    r"|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)"
)


def test_pyproject_version_typing_pep639_and_pytest_safety() -> None:
    pyproject_path = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    project = data["project"]
    assert project["name"] == "ellmos-tray"
    assert project["version"] == ellmos_tray.__version__
    assert "Typing :: Typed" in project["classifiers"]
    assert project["license-files"] == ["LICENSE", "THIRD_PARTY_LICENSES.md"]
    assert "Security" in project["urls"]
    assert "Third-Party Licenses" in project["urls"]

    package_data = data["tool"]["setuptools"]["package-data"]
    assert "py.typed" in package_data["ellmos_tray"]
    assert (REPO_ROOT / "src" / "ellmos_tray" / "py.typed").is_file()

    # Guard against relative --basetemp data-loss hazard under pytest 9.x
    pytest_opts = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    addopts = str(pytest_opts.get("addopts", ""))
    assert "--basetemp" not in addopts


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
    assert {"ui", "cli", "library"}.issubset(set(manifest["surfaces"]))
    assert manifest["entrypoints"]["cli"] == "ellmos-tray = ellmos_tray.__main__:main"
    assert manifest["source_of_truth"]["path"] == "."


def test_release_hygiene_docs_and_gitignore() -> None:
    for filename in (
        "README.md",
        "README_de.md",
        "LICENSE",
        "THIRD_PARTY_LICENSES.md",
        "SECURITY.md",
        "PRIVACY_POLICY.md",
        "CHANGELOG.md",
        "TODO.md",
    ):
        path = REPO_ROOT / filename
        assert path.is_file(), f"Missing required root file: {filename}"
        assert path.stat().st_size > 0, f"Empty root file: {filename}"

    todo_text = (REPO_ROOT / "TODO.md").read_text(encoding="utf-8")
    assert "## STATUS" in todo_text
    assert "| Category | Status | Notes |" in todo_text

    gitignore_text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    for entry in (
        "__pycache__",
        "*.pyc",
        ".env",
        "*.db",
        ".venv/",
        ".idea/",
        ".vscode/",
        "data/",
        "id_rsa*",
        "id_ed25519*",
        "*.csr",
        "*.token",
        "*.secret",
        ".pytest_temp/",
        "CONFLICT_REVIEW_LOG*",
        "LOCK-CACHE*",
    ):
        assert entry in gitignore_text or entry.rstrip("/") in gitignore_text


def test_security_policy_slas_and_sbom_contracts() -> None:
    sec_text = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "## English" in sec_text
    assert "## Deutsch" in sec_text
    assert "https://github.com/ellmos-ai/ellmos-tray/security/advisories/new" in sec_text
    assert "48 hours" in sec_text and "48 Stunden" in sec_text
    assert "5 business days" in sec_text and "5 Werktagen" in sec_text
    assert "30 calendar days" in sec_text and "30 Kalendertagen" in sec_text

    sbom_text = (REPO_ROOT / "THIRD_PARTY_LICENSES.md").read_text(encoding="utf-8")
    assert "pystray" in sbom_text and "LGPL-3.0-or-later" in sbom_text
    assert "Pillow" in sbom_text and "MIT-CMU" in sbom_text
    assert "INV-SLA-09" in sbom_text and "INV-SLA-10" in sbom_text

    dependabot_text = (REPO_ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
    assert 'package-ecosystem: "pip"' in dependabot_text
    assert 'package-ecosystem: "github-actions"' in dependabot_text

    ci_text = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "contents: read" in ci_text
    assert "pytest" in ci_text and "ruff check" in ci_text


def test_zero_hardcoded_personal_paths_and_secrets() -> None:
    skip_dirs = {".git", ".pytest_cache", ".pytest_temp", "__pycache__", ".ruff_cache", ".venv", "build", "dist"}
    text_suffixes = {".py", ".md", ".json", ".toml", ".ps1", ".cmd", ".yml", ".yaml", ".txt"}

    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(REPO_ROOT).parts
        if any(part in skip_dirs for part in rel_parts):
            continue
        if path.suffix.lower() not in text_suffixes and path.name not in {"LICENSE", ".gitignore"}:
            continue

        content = path.read_text(encoding="utf-8")
        rel_str = str(path.relative_to(REPO_ROOT))
        assert not PERSONAL_HOME_RE.search(content), f"Hardcoded personal path in {rel_str}"
        assert not SECRET_TOKEN_RE.search(content), f"Potential secret token in {rel_str}"
