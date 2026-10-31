# ellmos-tray

**Pluggbarer System-Tray und Desktop-Steuerungs-Client für ELLMOS, BACH und OCEAN**

`ellmos-tray` bietet eine plattformübergreifende (Windows, macOS, Linux) System-Tray-Anwendung und Schnellsteuerungs-Schnittstelle für lokale KI-Umgebungen. Es überführt die bewährten Desktop-Tray-Funktionen aus BACH OS in ein sauberes, eigenständiges und entkoppeltes Modul.

---

## Kernfunktionen

1. **Pluggables Branding & Erscheinungsbild**
   - Vorkonfigurierte Presets für **ELLMOS** (`"E"`), **BACH** (`"B"`) und **Open Ocean** (`"O"`).
   - Vollständig anpassbare Anwendungs-IDs, Menübeschriftungen, Benachrichtigungstitel und Lock-Pfade.
   - Dynamische RGBA-Status-Icons, die den Betriebsstatus visualisieren (Safe-Modus = Grün, Full/Schreibrechte = Orange, Aktiv/Arbeitet = Blau, Getrennt = Rot).

2. **Entkoppelte Architektur & Prozessbesitz (v0.1.2)**
   - Saubere Trennung zwischen Anzeige/Bedienung und Hintergrund-Aufgabenausführung.
   - **Start/Attach-Erkennung:** Erkennt automatisch, ob das Backend bereits aktiv war (`ATTACHED`) oder vom Tray als Kindprozess gestartet wurde (`SPAWNED`).
   - **Klarer Prozessbesitz:** Beim Beenden wird nur ein selbst gestarteter Kindprozess beendet; vorbestehende Backends laufen ungestört weiter.
   - Standardmäßig passiver Beobachter-Modus ohne zusätzliche Last.

3. **Robustheit & Wiederverbindung (v0.1.2)**
   - **Intelligente Reconnect-Automatik:** Zustandsautomat (`CONNECTED`, `DISCONNECTED`, `RECONNECTING`) mit exponentiellem Backoff und Wiederverbindungs-Benachrichtigung.
   - **Crash- & Sleep-Recovery:** Erkennt System-Standby/Ruhezustände und aktualisiert Sockets und Zustände ohne Stillstand.
   - **Integrierte Geräteabnahme:** Prüft eigenständig Loopback-Netzwerk-Sockets (`127.0.0.1`), Service-Ports und Dateisystemberechtigungen.

4. **Performance & Caching-Optimierung (v0.1.2)**
   - **Icon- & Thumbnail-Cache:** `IconCache` und `ThumbnailCache` vermeiden redundante PIL-Allokationen, Font-Ladevorgänge und unnötige Repaints.
   - **Adaptives Polling:** Dynamische Abfrageintervalle (2s bei aktiver Aufgabenverarbeitung, 5s im Normalbetrieb, bis zu 30s Backoff bei Verbindungsunterbrechung).

5. **Zuverlässige Single-Instance-Garantie**
   - Fail-closed Single-Instance-Sperre über OS-Byte-Range-Locks (`msvcrt` unter Windows, `fcntl.flock` unter POSIX).
   - Absturzsicher: Die Sperre wird auf Betriebssystem-Ebene am Dateihandle gehalten und beim Prozessende automatisch vom Kernel freigegeben.

6. **Windows Store & MSIX-Vorbereitung (v0.1.2)**
   - Prüfwerkzeug `tools/store_readiness.py` prüft Manifest, Publisher/Identity-Platzhalter, Store-Icons, WACK-Kriterien und Loopback-Deklarationen maschinenlesbar.

---

## Installation

```bash
pip install -e .
```

Abhängigkeiten: `pystray>=0.19.5`, `Pillow>=10.0.0`.

---

## CLI-Nutzung

Standard-Start mit ELLMOS-Branding:
```bash
ellmos-tray
```

Start mit BACH-Branding:
```bash
ellmos-tray --brand bach
```

Start mit Open Ocean-Branding:
```bash
ellmos-tray --brand ocean
```

Geräteabnahme-Check durchführen:
```bash
ellmos-tray --check-device
```

Windows-Store & MSIX Preflight-Check:
```bash
ellmos-tray --store-preflight
# oder direkt:
python tools/store_readiness.py --json
```

---

## Tests

```bash
pytest
ruff check .
python tools/store_readiness.py
```

---

## Lizenz

MIT License. Copyright (c) 2026 Lukas Geiger.
