# ellmos-tray

**Pluggbarer System-Tray und Desktop-Steuerungs-Client für ELLMOS, BACH und OCEAN**

`ellmos-tray` bietet eine plattformübergreifende (Windows, macOS, Linux) System-Tray-Anwendung und Schnellsteuerungs-Schnittstelle für lokale KI-Umgebungen. Es überführt die bewährten Desktop-Tray-Funktionen aus BACH OS in ein sauberes, eigenständiges und entkoppeltes Modul.

---

## Kernfunktionen

1. **Pluggables Branding & Erscheinungsbild**
   - Vorkonfigurierte Presets für **ELLMOS** (`"E"`), **BACH** (`"B"`) und **Open Ocean** (`"O"`).
   - Vollständig anpassbare Anwendungs-IDs, Menübeschriftungen, Benachrichtigungstitel und Lock-Pfade.
   - Dynamische RGBA-Status-Icons, die den Betriebsstatus visualisieren (Safe-Modus = Grün, Full/Schreibrechte = Orange, Aktiv/Arbeitet = Blau, Getrennt = Rot).

2. **Entkoppelte Architektur & Aufgabenausführung**
   - Saubere Trennung zwischen reiner Anzeige/Bedienung und der Hintergrund-Aufgabenausführung.
   - Standardmäßig passiver Beobachter-Modus (Ausführung liegt bei `agents-heart` oder Hintergrund-Worker-Pools).
   - Optionale Ausführungs-Delegates (`TaskExecutionDelegate`, `LegacyBachIdleRunner`) für 100 % Rückwärtskompatibilität ohne fest verdrahtete Pfade.

3. **Zuverlässige Single-Instance-Garantie**
   - Fail-closed Single-Instance-Sperre über OS-Byte-Range-Locks (`msvcrt` unter Windows, `fcntl.flock` unter POSIX).
   - Absturzsicher: Die Sperre wird auf Betriebssystem-Ebene am Dateihandle gehalten und beim Prozessende automatisch vom Kernel freigegeben.

4. **Dynamisches Kontextmenü**
   - **Status & Modi:** Live-Übersicht über den aktuellen Modus (`SAFE` / `FULL`) und Denkmodus (`THINK`).
   - **Slot-Steuerung:** Interaktive Auswahl von Modell, Backend, Turn-Limits und Sicherheitsmodus für Chat-, Always-On- und Connector-Slots.
   - **Dynamische Worker:** Hintergrund-Worker einsehen, starten, pausieren, fortsetzen und löschen.
   - **Ressourcen-Vorrang (Fackel):** Schnelles Umschalten der Priorität zwischen lokalem Modell (Ollama) und Rechenjobs (Compute).
   - **Dienst-Status:** Live-Indikatoren für GUI Dashboard (:8000), Control API (:8081) und Ollama (:11434).
   - **Prompt-Starter:** Nahtlose Integration mit PromptBoard-Bibliotheken und nativen JSON-Prompt-Sammlungen mit Zwischenablage-Kopieren oder direktem Senden.

---

## Installation

```bash
pip install -e .
```

Abhängigkeiten: `pystray>=0.19.5`, `Pillow>=10.0.0`.

---

## CLI-Verwendung

Start mit Standard-ELLMOS-Branding:
```bash
ellmos-tray
```

Start mit BACH-Branding („Bach B"):
```bash
ellmos-tray --brand bach
```

Start mit Open-Ocean-Branding:
```bash
ellmos-tray --brand ocean
```

Diagnose-Smoketest für PromptBoard-Erkennung:
```bash
ellmos-tray --smoke-promptboard
```

---

## Python-Integration

```python
from ellmos_tray import TrayApp, TrayBranding

# 1. Mit vorgefertigtem Branding starten
app = TrayApp(branding=TrayBranding.bach())

# 2. Oder mit eigenem Branding
custom = TrayBranding(
    app_id="mein-assistent",
    app_title="Mein KI Assistent",
    icon_char="A",
    notification_title="Assistent",
)
app = TrayApp(branding=custom, host="127.0.0.1", port=8081)

# System-Tray starten
app.run()
```

---

## Tests

```bash
pytest
ruff check .
```

---

## Lizenz

MIT License. Copyright (c) 2026 Lukas Geiger.
