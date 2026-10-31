# Windows Store Listing: ELLMOS Tray / Open Ocean Desktop Control

**Application Title:** ELLMOS Tray & Desktop Control  
**Short Title:** ELLMOS Tray  
**Category:** Developer Tools / Utilities & Tools  
**Default Language:** English (United States), German (Germany)  

---

## 1. Store Metadata & Descriptions

### Short Description (Max 100 characters)
**English:**  
Quick system tray control and real-time status monitor for local AI models and agents.

**Deutsch:**  
Schnelle System-Tray-Steuerung und Status-Monitor für lokale KI-Modelle und Agenten.

---

### Detailed Description (English)

**ELLMOS Tray** is the lightweight, privacy-respecting system tray companion and control center for local artificial intelligence environments, including **ELLMOS**, **BACH OS**, and **Open Ocean**.

Designed for developers, researchers, and power users running local LLMs (Large Language Models), ELLMOS Tray provides immediate, single-click visibility and rapid control over active inference engines, background agent workers, and prompt libraries—directly from your Windows Taskbar notification area.

#### Core Features:
- **Taskbar System Tray Presence:** Displays real-time status icons indicating connectivity, active reasoning mode (Safe vs Full Write permissions), and active compute workloads.
- **Model Slot Management:** Switch local models, adjust max tool turns, and toggle thinking/reasoning modes for Chat, Always-On workers, and Connector bridges with zero latency.
- **Dynamic Worker Pool:** Inspect active background agent tasks, start, pause, resume, or terminate long-running autonomous workflows.
- **Resource Prioritization (Fackel):** Dynamically allocate GPU/CPU resources between interactive local chat inference (Ollama) and heavy background compilation/compute jobs.
- **PromptBoard Launcher:** Quick access to structured prompt templates with one-click clipboard copying and direct command execution.
- **Process Ownership & Reconnect:** Seamlessly attaches to existing local backends or manages child service processes, featuring exponential backoff reconnect and sleep/wake recovery.
- **Device Environment Acceptance:** Built-in self-diagnostic preflight check verifying loopback network stacks, local ports, and filesystem permissions.

---

### Ausführliche Beschreibung (Deutsch)

**ELLMOS Tray** ist das schlanke, datenschutzorientierte Taskleisten-Kontrollzentrum für lokale KI-Umgebungen wie **ELLMOS**, **BACH OS** und **Open Ocean**.

Speziell für Entwickler, Forscher und Anwender konzipiert, die lokale Sprachmodelle (LLMs) betreiben, bietet ELLMOS Tray sofortige Statusübersicht und Schnellsteuerung über aktive Inferenz-Engines, autonome Hintergrundagenten und Prompt-Bibliotheken—direkt aus dem Windows-Infobereich (System Tray).

#### Funktionsumfang:
- **Echtzeit-Status in der Taskleiste:** Farbcodierte Icons zeigen Verbindungsstatus, Ausführungsmodus (Safe Mode vs. Schreibberechtigung) und aktive Berechnungsphasen an.
- **Modell-Slots konfigurieren:** Schneller Wechsel von LLM-Modellen, Begrenzung von Werkzeugrunden und Umschalten des Denkmodus für Chat, Always-On-Agenten und Schnittstellen.
- **Dynamische Hintergrundagenten:** Anzeige laufender Hintergrundprozesse mit Optionen zum Starten, Pausieren, Fortsetzen und Beenden autonomer Aufgaben.
- **Ressourcen-Priorisierung (Fackel):** Flexible Aufteilung der Systemressourcen zwischen interaktiver Inferenz (Ollama) und rechenintensiven Hintergrund-Workloads.
- **PromptBoard-Schnellzugriff:** Schneller Zugriff auf strukturierte Prompts mit 1-Klick-Kopieren in die Zwischenablage oder direkter Ausführung.
- **Prozessbesitz & Reconnect-Automatik:** Unterscheidet sauber zwischen bereits laufenden Hintergrunddiensten und selbst gestarteten Kindprozessen mit intelligenter Wiederverbindung nach Standby/Ruhezustand.
- **Integrierte Geräteabnahme:** Prüft eigenständig Loopback-Netzwerk, Service-Ports und Schreibberechtigungen.

---

## 2. Privacy & Data Protection / Datenschutzangaben

### 100% Local-First Operation (Rein lokaler Betrieb)
ELLMOS Tray operates strictly local-first. All monitoring, status evaluations, prompt library lookups, and task management run entirely on the user's personal device.
- **Zero Telemetry:** No user data, keystrokes, prompt contents, or usage analytics are transmitted to remote servers.
- **Loopback Communication Only:** The tray application connects strictly via loopback (`127.0.0.1` / `localhost`) to interface with local services (`:8081` Control API, `:8000` GUI, `:11434` Ollama).
- **Optional Cloud Bridges:** If the user explicitly configures third-party cloud API models (e.g. Anthropic Claude, OpenAI), communication with those providers is initiated exclusively through the local backend using the user's own API keys. The tray client never accesses or exfiltrates user credentials.

---

## 3. Microsoft Store Certification Reviewer Notes (Prüferhinweise)

> **Information for Microsoft Store Application Certification Testers**

### Architecture & Loopback Usage Justification
ELLMOS Tray is a desktop bridge application designed to monitor and manage local AI background processes running on the user's computer.
- **Local Loopback Access (`127.0.0.1`):** The application communicates with local endpoints (`http://127.0.0.1:8081` and `http://127.0.0.1:8000`). This communication is entirely internal to the machine and complies with Microsoft Store policies for developer and local-management tools.
- **Capability `runFullTrust`:** Declared in the MSIX manifest to enable taskbar system tray integration (`pystray`), process monitoring, and launching local companion browser views.

### Testing Without Backend Installed (Offline / Standalone Mode)
The certification tester does not need to install Ollama or a local LLM backend to certify this application:
1. **Launch the application:** Start `ellmos-tray.exe`.
2. **Taskbar Icon:** An icon will appear in the Windows taskbar notification area. If no local Control API is running, the icon displays a red/amber disconnected indicator.
3. **Context Menu:** Right-click the tray icon to open the context menu. You will observe:
   - Status: *"Nicht verbunden / Versuche: http://127.0.0.1:8081"* (or reconnect state).
   - Menu items: *"Services"*, *"Geräteabnahme prüfen"*, *"Beenden"*.
4. **Self-Diagnostic Test:** Click *"Geräteabnahme prüfen"* in the context menu. A Windows desktop notification will appear confirming the device acceptance check (verifying loopback sockets, storage permissions, and graphics).
5. **Clean Exit:** Click *"Beenden"* to cleanly close the application and release the OS single-instance lock.

### Automated Smoke Tests (Command Line)
Testers may also verify the application from PowerShell / CMD:
- `ellmos-tray.exe --check-device` : Runs device acceptance check and returns exit code 0 with JSON diagnostics.
- `ellmos-tray.exe --smoke-promptboard` : Outputs prompt library smoke test JSON without opening GUI.
- `ellmos-tray.exe --store-preflight` : Runs the Store readiness validation tool.

### Support & Contact
- Repository: https://github.com/ellmos-ai/ellmos-tray
- Issues & Support: https://github.com/ellmos-ai/ellmos-tray/issues
- License: MIT License
