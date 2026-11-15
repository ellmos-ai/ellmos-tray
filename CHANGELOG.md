# Changelog

All notable changes to `ellmos-tray` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security
- Removed hardcoded personal macOS path in `LegacyBachIdleRunner._detect_repo_dir()` (`src/ellmos_tray/runner.py`), replacing it with user-neutral `Path.home() / "services" / "bach"`.
- Hardened `ControlApiClient` (`src/ellmos_tray/client.py`) against `CR`/`LF`/`NUL` HTTP header injection (`CWE-113`), added a `4 MiB` response payload ceiling (`MAX_API_RESPONSE_BYTES`, `CWE-400`), URL-encoded `chat_id` query parameters in `get_history()`, and validated `telegram_url` against `is_safe_http_url()`.
- Enforced explicit `http`/`https` scheme validation (`_open_browser_url` / `is_safe_http_url`) before all `webbrowser.open()` calls in `MenuBuilder` (`src/ellmos_tray/menu.py`) to block `file://`, SMB, and custom URI handler execution.
- Hardened `LegacyBachIdleRunner._auto_commit_task()` (`src/ellmos_tray/runner.py`) with `--` end-of-options delimiter on `git add` (`CWE-88`), parent-traversal filtering, newline sanitization in commit titles, and URL-encoded task/assignee identifiers.
- Upgraded `SECURITY.md` to bilingual (EN/DE) policy with GitHub Private Vulnerability Reporting and binding response SLAs (`INV-SLA-09` & `INV-SLA-10`: `48h` acknowledgement, `5` business days triage, `30` calendar days remediation).

### Added
- `THIRD_PARTY_LICENSES.md` (Level-1 SBOM) documenting `pystray` (`LGPL-3.0-or-later` dynamic runtime import & MSIX freeze boundary), `Pillow` (`MIT-CMU`), transitive packages, dev dependencies, and governance invariants; registered under PEP 639 `license-files` and `[project.urls]` in `pyproject.toml`.
- `.github/dependabot.yml` for weekly `pip` and `github-actions` supply-chain security updates.
- `.github/workflows/ci.yml` least-privilege (`contents: read`) CI matrix running `pip check`, `ruff check .`, `compileall`, `pytest -v`, and `tools/store_readiness.py --json`.
- `TODO.md` with 10-gate release status table (`final_gate_check.py`), `CHANGELOG.md`, PEP 561 `src/ellmos_tray/py.typed`, `ellmos-module.v2.json`, and expanded security/metadata contract tests.

### Changed
- Synchronized `README_de.md` and `PRIVACY_POLICY.md` with `README.md` (`--smoke-promptboard`, `#510`/`#511` security & claim boundaries, and cloud credential clarity).
- Hardened `.gitignore` with SSH key wildcards (`id_rsa*`, `id_ed25519*`, `id_ecdsa*`, `id_dsa*`), `*.csr`, `*.token`, `*.secret`, token JSON patterns, `.pytest_temp/`, agent caches, `CONFLICT_REVIEW_LOG*`, `LOCK-CACHE*`, and multi-host conflict exclusions.

## [0.1.2]

### Added
- Live RAM claiming status, Control API redirect boundary (`#510`), and Store preflight claim boundary (`#511`).
- `Direktzugriff` submenu grouping individual GUI page links.
- `Deine Agenten (Modell-Bindung & Claim)` and `RAM-Distributor` menu labeling.
- Buddha Talk radio slot, 1-click compute model release, Permissions sub-flyout, and ELLMOS Talk shortcut.
- Process ownership (`BackendProcessManager`), exponential-backoff reconnect, and Microsoft Store readiness preflight tool (`tools/store_readiness.py`).

### Fixed
- Aligned shared GUI navigation, backend observation, and environment-based Control API token lookup.

## [0.1.0]

### Added
- Initial release of `ellmos-tray` with pluggable `TrayBranding`, `PromptManager`, single-instance lock, device acceptance diagnostics (`--check-device`), and decoupled task runner.
