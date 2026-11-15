# Privacy Policy / Datenschutzerklärung

- **Last updated:** November 15, 2026
- **Product:** ELLMOS Tray / Open Ocean Desktop Control Client
- **Publisher:** ELLMOS AI Open Source

---

## English Summary

`ellmos-tray` is a local-first system tray utility and desktop control client designed with complete privacy and data sovereignty in mind.

### 1. 100% Local-First Operation
All interactions, prompts, tasks, and system monitoring remain entirely on your local machine. No prompt text, system statistics, or logs are transmitted to external servers or telemetry collectors.

### 2. Local Loopback Network Communication
The application communicates by default over the local loopback interface (`127.0.0.1` / `localhost`) to interface with your locally running services:
- **Control API** (`127.0.0.1:8081`): Service status, model switching, slot configuration.
- **GUI Dashboard** (`127.0.0.1:8000`): Web-based control panel and task viewer.
- **Local LLM Engine** (`127.0.0.1:11434` / Ollama): Local inference engine.

By default, this traffic never leaves your local network adapter.

### 3. Zero Telemetry & Zero Tracking
`ellmos-tray` does not include analytics SDKs, advertising frameworks, crash-reporting uploaders, or tracking beacons. We do not collect or store:
- User identities or IP addresses
- System usage patterns
- LLM interaction history or generated text

### 4. Optional External Cloud Bridges
If you explicitly choose to connect cloud providers (such as Anthropic Claude or OpenAI) via the local Control API, your queries are transmitted directly by that backend to the respective provider using your own user-supplied API keys. The tray client itself neither captures nor proxies external cloud provider API keys.

---

## Deutsche Datenschutzerklärung

`ellmos-tray` ist eine lokale Desktop-System-Tray-Anwendung, die nach dem Prinzip maximaler Privatsphäre („Local-First“) arbeitet.

### 1. Rein lokaler Betrieb
Alle Abfragen, Prompts, Hintergrundaufgaben und Systemzustände verbleiben ausschließlich auf Ihrem lokalen Rechner. Es findet keine Übertragung von Daten an externe Analyse- oder Werbedienste statt.

### 2. Lokale Loopback-Netzwerkkommunikation
Die Anwendung kommuniziert standardmäßig ausschließlich über die interne Loopback-Schnittstelle (`127.0.0.1` / `localhost`) mit Ihren lokal installierten Diensten:
- **Control API** (`127.0.0.1:8081`): Statusabfragen, Agenten-Konfiguration.
- **GUI-Oberfläche** (`127.0.0.1:8000`): Lokale Verwaltungsoberfläche.
- **Lokale KI-Modelle** (`127.0.0.1:11434` / Ollama): Ausführung lokaler LLMs.

Diese Netzwerkkommunikation verlässt standardmäßig zu keinem Zeitpunkt Ihren lokalen Computer.

### 3. Keine Telemetrie und keine Datenerfassung
Die Software enthält keinerlei Telemetrie- oder Tracking-Komponenten. Es werden keine Nutzungsstatistiken, Absturzberichte oder persönliche Daten erfasst, gespeichert oder an Dritte weitergegeben.

### 4. Optionale Cloud-Brücken
Falls Sie in Ihrer lokalen Backend-Konfiguration externe Cloud-Modelle (z. B. OpenAI oder Anthropic) aktivieren, erfolgt die Kommunikation mit diesen Anbietern durch das lokale Backend ausschließlich über Ihre eigenen API-Schlüssel. Der Tray-Client speichert keine externen Cloud-Zugangsdaten und liest keine fremden Cloud-API-Schlüssel aus.

---

## 5. Configurable Host, Credential & Redirect Boundary (`#510` / `#511`)

- **Default Loopback vs. Explicit `--host`:** By default, `ellmos-tray` connects exclusively to `127.0.0.1` (`localhost`). If a user explicitly supplies `--host` or `--gui-url` (for example, to monitor a personal home-server over LAN or Tailscale), requests are sent only to that user-specified endpoint.
- **Control API Bearer Token & Redirect Protection (`#510`):** When authenticating to the local Control API (`BACH_CONTROL_API_TOKEN`, `BACH_CONTROL_API_TOKEN_FILE`, or local user credential file), the `Authorization` header is attached strictly to requests targeting `base_url`, control characters (`CR`/`LF`/`NUL`) are rejected fail-closed, HTTP redirect following is disabled (`_NoControlRedirect`), and cross-origin redirect responses are rejected so credentials are never forwarded across origins.
- **Scope of `--store-preflight` (`#511`):** The built-in `tools/store_readiness.py` (`--store-preflight`) verifies source-tree manifest metadata, asset dimensions, and documentation disclosures (`claim_boundary: source_and_metadata_preflight_only`). Final MSIX binary packaging, Authenticode signing, WACK binary execution, and Microsoft Partner Center submission remain explicit external release gates.

### Konfigurierbare Host-, Token- & Preflight-Grenzen (`#510` / `#511` — Deutsch)
- **Standard-Loopback vs. explizites `--host`:** Ohne explizite Angabe von `--host` oder `--gui-url` verbindet sich `ellmos-tray` ausschließlich mit `127.0.0.1`. Nur bei bewusster Nutzerkonfiguration (etwa für einen eigenen Heimserver im LAN/Tailscale) wird der angegebene Endpunkt angesprochen.
- **Control-API-Token- & Weiterleitungsschutz (`#510`):** Ein lokales Control-API-Bearer-Token (`BACH_CONTROL_API_TOKEN` bzw. lokale Token-Datei) wird ausschließlich an `base_url` gesendet; Steuerzeichen in Headern werden abgewiesen und HTTP-Weiterleitungen über `_NoControlRedirect` strikt blockiert, damit Token niemals an fremde Ursprünge abfließen.
- **Prüfumfang von `--store-preflight` (`#511`):** `tools/store_readiness.py` prüft ausschließlich Quellbaum-Metadaten, Icon-Abmessungen und Richtliniendokumente (`source_and_metadata_preflight_only`). MSIX-Paketierung, Authenticode-Signatur, WACK-Lauf und Store-Einreichung bleiben eigenständige externe Freigabeschritte.
