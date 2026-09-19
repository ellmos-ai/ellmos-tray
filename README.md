# ellmos-tray

**Pluggable System Tray and Desktop Control Client for ELLMOS, BACH, and OCEAN**

`ellmos-tray` provides a cross-platform (Windows, macOS, Linux) system tray application and quick-control interface for local AI environments. It extracts the proven, high-utility desktop tray capabilities of BACH OS into a clean, standalone, decoupled module.

---

## Key Features

1. **Pluggable Branding & Theming**
   - Built-in presets for **ELLMOS** (`"E"`), **BACH** (`"B"`), and **Open Ocean** (`"O"`).
   - Fully customizable application IDs, menu labels, notification titles, and lock files.
   - Dynamic RGBA status icons reflecting operational state (Safe Mode, Full/Write Mode, Active Processing, Disconnected).

2. **Decoupled Architecture & Task Execution**
   - Clean separation between UI state observation and background task execution.
   - Passive observer mode by default (execution delegated to `agents-heart` or background worker pools).
   - Optional pluggable execution runners (`TaskExecutionDelegate`, `LegacyBachIdleRunner`) for full backward compatibility without hardcoded paths.

3. **Robust Single-Instance Guarantees**
   - Fail-closed single-instance enforcement via OS byte-range locks (`msvcrt` on Windows, `fcntl.flock` on POSIX).
   - Crash-resilient: Locks are held at the OS kernel file handle level and are immediately freed if a process terminates.

4. **Dynamic Context Menu**
   - **Status & Modes:** Real-time visibility into active mode (`SAFE` / `FULL`) and reasoning (`THINK`).
   - **Slot Control:** Interactive model, backend, turn limits, and mode configuration for Chat, Always-On, and Connector slots.
   - **Dynamic Workers:** Inspect, start, pause, resume, and terminate background workers.
   - **Resource Prioritization (Fackel):** Switch priority between local LLM inference (Ollama) and background compute jobs.
   - **Services Health:** Live health indicators for GUI Dashboard (:8000), Control API (:8081), and Ollama (:11434).
   - **Prompt Launcher:** Integrates with PromptBoard libraries and native JSON prompt collections with single-click clipboard copying or direct execution.

---

## Installation

```bash
pip install -e .
```

Dependencies: `pystray>=0.19.5`, `Pillow>=10.0.0`.

---

## CLI Usage

Run with default ELLMOS branding:
```bash
ellmos-tray
```

Run with BACH OS branding and settings:
```bash
ellmos-tray --brand bach
```

Run with Open Ocean branding:
```bash
ellmos-tray --brand ocean
```

Diagnostic smoke test for PromptBoard integration:
```bash
ellmos-tray --smoke-promptboard
```

---

## Python API Usage

```python
from ellmos_tray import TrayApp, TrayBranding

# 1. Using predefined brandings
app = TrayApp(branding=TrayBranding.bach())

# 2. Or custom branding
custom_branding = TrayBranding(
    app_id="my-assistant",
    app_title="My AI Assistant",
    icon_char="A",
    notification_title="Assistant",
)
app = TrayApp(branding=custom_branding, host="127.0.0.1", port=8081)

# Run the system tray
app.run()
```

---

## Testing

```bash
pytest
ruff check .
```

---

## License

MIT License. Copyright (c) 2026 Lukas Geiger.
