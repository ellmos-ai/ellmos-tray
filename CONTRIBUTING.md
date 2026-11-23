# Contributing to `ellmos-tray` / Mitwirken an `ellmos-tray`

Thank you for your interest in contributing to `ellmos-tray`! Please follow these guidelines to keep the repository secure, portable, and test-verified.

---

## English

### Development Setup

1. Clone the repository and create a clean virtual environment:
   ```bash
   git clone https://github.com/ellmos-ai/ellmos-tray.git
   cd ellmos-tray
   python -m venv .venv
   # Activate .venv, then install in editable mode with dev dependencies:
   pip install -e ".[dev]"
   ```
2. Always work on a dedicated feature or fix branch — never commit directly to `master`.

### Quality Gates Before Opening a Pull Request

Run all local checks and verify zero errors:

```bash
python -m pip check
python -m ruff check .
python -m compileall -q src tests tools
python -m pytest -ra -v
python tools/store_readiness.py --json
```

### Engineering & Privacy Boundaries

- **Loopback by default:** Default HTTP connections must target `127.0.0.1` (`localhost`) with zero telemetry.
- **No personal paths or secrets:** Never hardcode user home directories, local development drive paths, tokens, or `.db` files. Use environment variables (`BACH_CONTROL_API_TOKEN`, `BACH_REPO_DIR`, `ELLMOS_GUI_URL`, `ELLMOS_CREDENTIALS_DIR`) or `Path.home()`.
- **Control API & URL safety:** Preserve `_NoControlRedirect` same-origin checks, `CR`/`LF`/`NUL` header rejection, `4 MiB` response ceiling, and `is_safe_http_url` (`http`/`https` only) before browser launches.
- **Keep docs synchronized:** Update `README.md`, `README_de.md`, `CHANGELOG.md` (`## [Unreleased]`), and `llms.txt` when behavior or CLI flags change.

---

## Deutsch (Richtlinien für Beiträge)

Vielen Dank für dein Interesse an der Weiterentwicklung von `ellmos-tray`!

### Einrichtung der Entwicklungsumgebung

1. Repository klonen, virtuelle Umgebung anlegen und mit Entwicklungsabhängigkeiten installieren:
   ```bash
   git clone https://github.com/ellmos-ai/ellmos-tray.git
   cd ellmos-tray
   python -m venv .venv
   pip install -e ".[dev]"
   ```
2. Änderungen immer auf einem eigenen Feature- oder Fix-Branch umsetzen — niemals direkt auf `master` pushen.

### Pflichtprüfungen vor einem Pull Request

```bash
python -m pip check
python -m ruff check .
python -m compileall -q src tests tools
python -m pytest -ra -v
python tools/store_readiness.py --json
```

### Architektur- & Datenschutzgrenzen

- **Loopback als Standard:** Standardverbindungen richten sich ausschließlich an `127.0.0.1` (`localhost`), ohne Telemetrie oder Tracking.
- **Keine persönlichen Pfade oder Geheimnisse:** Niemals lokale Benutzerverzeichnisse, rechnergebundene Entwicklungspfade, Tokens oder `.db`-Dateien fest einbauen. Stattdessen Umgebungsvariablen (`BACH_CONTROL_API_TOKEN`, `BACH_REPO_DIR`, `ELLMOS_GUI_URL`, `ELLMOS_CREDENTIALS_DIR`) oder `Path.home()` verwenden.
- **Dokumentation synchron halten:** Bei neuen CLI-Optionen oder Verhaltensänderungen `README.md`, `README_de.md`, `CHANGELOG.md` (`## [Unreleased]`) und `llms.txt` mitführen.
