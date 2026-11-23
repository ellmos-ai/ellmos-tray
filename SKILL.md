---
name: ellmos-tray
version: 0.1.2
description: >
  Use when launching, scripting, configuring, or validating the pluggable desktop
  system tray client (`ellmos-tray`) for ELLMOS, BACH, or Open Ocean local AI runtimes
  via CLI flags, Python API (`TrayApp`, `TrayBranding`, `ControlApiClient`), or
  Windows Store preflight checks.
---

# ellmos-tray Skill

`ellmos-tray` is a cross-platform (Windows, macOS, Linux) system tray and quick-control client (`pystray` + `Pillow`) that connects over local loopback (`127.0.0.1` by default) to Control API (`:8081`), GUI (`:8000`), and Ollama (`:11434`).

## Quick CLI Workflows

```bash
# Start tray with default ELLMOS, BACH, or Open Ocean branding
ellmos-tray --brand ellmos
ellmos-tray --brand bach
ellmos-tray --brand ocean

# Run non-interactive diagnostics / preflight checks
ellmos-tray --smoke-promptboard
ellmos-tray --check-device
ellmos-tray --store-preflight
python tools/store_readiness.py --json
```

## Key CLI Options

| Flag | Default | Purpose |
|---|---|---|
| `--brand` | `ellmos` | Branding preset (`ellmos`, `bach`, `ocean`) |
| `--host` | `127.0.0.1` | Control API / local service host |
| `--port` | `8081` | Control API port |
| `--gui-url` | `None` | Custom GUI base URL (overrides `ELLMOS_GUI_URL` / `BACH_GUI_URL` / `OCEAN_GUI_URL`) |
| `--idle-worker` | `auto` | Observer mode (`auto`, `on`, `off`) or `legacy` (`LegacyBachIdleRunner`) |
| `--repo-dir` | `None` | Repository root for legacy worker mode |
| `--start-backend` | `None` | Optional command/script to spawn backend if offline |
| `--smoke-promptboard` | `False` | Print PromptBoard library detection snapshot as JSON and exit |
| `--check-device` | `False` | Run loopback/port/storage acceptance check and exit |
| `--store-preflight` | `False` | Run MSIX/Store metadata & asset preflight check and exit |

## Python API Usage

```python
from ellmos_tray import (
    ControlApiClient,
    PassiveTaskDelegate,
    TrayApp,
    TrayBranding,
    check_device_acceptance,
)

branding = TrayBranding.ocean()
client = ControlApiClient(host="127.0.0.1", port=8081)
report = check_device_acceptance(branding=branding)

if report.passed:
    app = TrayApp(branding=branding, client=client, runner=PassiveTaskDelegate())
    app.run()
```

## Security & Operational Boundaries

- **Authentication:** Supply tokens via `CONTROL_API_AUTH_HEADER`, `BACH_CONTROL_API_TOKEN`, `BACH_CONTROL_API_TOKEN_FILE`, or `~/.credentials/{bach_control_api_token,control_api_token}` (`ELLMOS_CREDENTIALS_DIR` optional). Redirects are blocked (`_NoControlRedirect`) and `CR`/`LF`/`NUL` header injection fails closed.
- **Browser Launches:** All companion links require explicit `http://` or `https://` (`is_safe_http_url`).
- **Store Preflight Scope:** `--store-preflight` validates source metadata and PNG assets only (`claim_boundary: source_and_metadata_preflight_only`).
