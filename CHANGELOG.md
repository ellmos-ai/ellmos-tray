# Changelog

All notable changes to `ellmos-tray` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `TODO.md` with 10-gate release status table (`final_gate_check.py`).
- `SECURITY.md` documenting loopback defaults, `#510` redirect/token boundary, and `#511` preflight claim boundaries.
- `CHANGELOG.md` release history.
- PEP 561 `src/ellmos_tray/py.typed` marker and `Typing :: Typed` classifier in `pyproject.toml`.
- Canonical `ellmos-module.v2.json` manifest aligned with `pyproject.toml` (`0.1.2`) in the Git repository root.
- Metadata and hygiene contract test suite in `tests/test_metadata.py`.

### Changed
- Hardened `.gitignore` with explicit `*.pyc`, `*.pyo`, `*.pyd`, `.env.*`, `*.db`, `*.sqlite*`, `data/`, `LOCK*.txt`, and key/certificate ignore patterns.

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
