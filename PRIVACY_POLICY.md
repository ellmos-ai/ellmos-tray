# Privacy Policy / Datenschutzerklärung

**Last updated:** October 31, 2026  
**Product:** ELLMOS Tray / Open Ocean Desktop Control Client  
**Publisher:** ELLMOS AI Open Source  

---

## English Summary

`ellmos-tray` is a local-first system tray utility and desktop control client designed with complete privacy and data sovereignty in mind.

### 1. 100% Local-First Operation
All interactions, prompts, tasks, and system monitoring remain entirely on your local machine. No prompt text, system statistics, or logs are transmitted to external servers or telemetry collectors.

### 2. Local Loopback Network Communication
The application communicates strictly over the local loopback interface (`127.0.0.1` / `localhost`) to interface with your locally running services:
- **Control API** (`127.0.0.1:8081`): Service status, model switching, slot configuration.
- **GUI Dashboard** (`127.0.0.1:8000`): Web-based control panel and task viewer.
- **Local LLM Engine** (`127.0.0.1:11434` / Ollama): Local inference engine.

This traffic never leaves your local network adapter.

### 3. Zero Telemetry & Zero Tracking
`ellmos-tray` does not include analytics SDKs, advertising frameworks, crash-reporting uploaders, or tracking beacons. We do not collect or store:
- User identities or IP addresses
- System usage patterns
- LLM interaction history or generated text

### 4. Optional External Cloud Bridges
If you explicitly choose to connect cloud providers (such as Anthropic Claude or OpenAI) via the local Control API, your queries are transmitted directly to the respective provider using your own user-supplied API keys. The tray client itself neither captures nor proxies these credentials.

---

## Deutsche Datenschutzerklärung

`ellmos-tray` ist eine lokale Desktop-System-Tray-Anwendung, die nach dem Prinzip maximaler Privatsphäre („Local-First“) arbeitet.

### 1. Rein lokaler Betrieb
Alle Abfragen, Prompts, Hintergrundaufgaben und Systemzustände verbleiben ausschließlich auf Ihrem lokalen Rechner. Es findet keine Übertragung von Daten an externe Analyse- oder Werbedienste statt.

### 2. Lokale Loopback-Netzwerkkommunikation
Die Anwendung kommuniziert ausschließlich über die interne Loopback-Schnittstelle (`127.0.0.1` / `localhost`) mit Ihren lokal installierten Diensten:
- **Control API** (`127.0.0.1:8081`): Statusabfragen, Agenten-Konfiguration.
- **GUI-Oberfläche** (`127.0.0.1:8000`): Lokale Verwaltungsoberfläche.
- **Lokale KI-Modelle** (`127.0.0.1:11434` / Ollama): Ausführung lokaler LLMs.

Diese Netzwerkkommunikation verlässt zu keinem Zeitpunkt Ihren lokalen Computer.

### 3. Keine Telemetrie und keine Datenerfassung
Die Software enthält keinerlei Telemetrie- oder Tracking-Komponenten. Es werden keine Nutzungsstatistiken, Absturzberichte oder persönliche Daten erfasst, gespeichert oder an Dritte weitergegeben.

### 4. Optionale Cloud-Brücken
Falls Sie in Ihrer lokalen Backend-Konfiguration externe Cloud-Modelle (z. B. OpenAI oder Anthropic) aktivieren, erfolgt die Kommunikation mit diesen Anbietern ausschließlich über Ihre eigenen API-Schlüssel. Der Tray-Client speichert keine Zugangsdaten und liest keine geheimen Schlüssel aus.


---

## 5. Configurable Host, Credential & Redirect Boundary (#510 / #511)

- **Default Loopback vs. Explicit `--host`:** By default, `ellmos-tray` connects exclusively to `127.0.0.1` (`localhost`). If a user explicitly supplies `--host` or `--gui-url` (for example, to monitor a personal home-server over LAN or Tailscale), requests are sent only to that user-specified endpoint.
- **Control API Bearer Token & Redirect Protection:** When authenticating to the Control API (`BACH_CONTROL_API_TOKEN` / local credential file), the `Authorization` header is attached strictly to requests targeting `base_url`. Authenticated Control API requests disable HTTP redirect following (`_NoControlRedirect`), and cross-origin redirect responses are rejected fail-closed so credentials are never forwarded across origins.
- **Scope of `--store-preflight`:** The built-in `tools/store_readiness.py` (`--store-preflight`) verifies source-tree manifest metadata, asset dimensions, and documentation disclosures (`claim_boundary: source_and_metadata_preflight_only`). Final MSIX binary packaging, Authenticode signing, WACK binary execution, and Microsoft Partner Center submission remain explicit release gates.
