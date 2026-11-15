# Security Policy / Sicherheitsrichtlinie

---

## English

### Scope & Threat Model

`ellmos-tray` is a local-first system tray client and quick-control companion for local AI runtimes (`ELLMOS`, `BACH`, `OCEAN`). By design:

- **Loopback by default:** Without explicit user flags (`--host`, `--gui-url`), all HTTP connections target `127.0.0.1` (`localhost`).
- **Zero telemetry or tracking:** The tray client bundles no analytics SDKs, crash uploaders, or remote telemetry endpoints.
- **Control API bearer token, header & redirect boundary (`#510`):**
  - When authenticating against the local Control API (`BACH_CONTROL_API_TOKEN`, `CONTROL_API_AUTH_HEADER`, `BACH_CONTROL_API_TOKEN_FILE`, or a local user credential file), `Authorization` headers are attached strictly to requests targeting the configured `base_url`.
  - Header values containing `CR`/`LF`/`NUL` control characters are rejected fail-closed (`CWE-113`), and HTTP responses are bounded to `4 MiB` (`MAX_API_RESPONSE_BYTES`, `CWE-400`).
  - Authenticated requests disable HTTP redirect following via `_NoControlRedirect` and verify same-origin URLs so bearer credentials are never forwarded across origins.
- **HTTP(S)-only browser launch & CLI argument guards:** Companion browser links (`gui_url`, `telegram_url`, quick links) enforce explicit `http`/`https` schemes (`is_safe_http_url`) before calling `webbrowser.open`, preventing local `file://`, SMB, or custom protocol handler execution. Legacy auto-commit calls pass `--` to `git add` (`CWE-88`) and URL-encode dynamic query/path identifiers.
- **Single-instance OS lock:** Single-instance enforcement uses OS-level byte-range (`msvcrt` on Windows) or `flock` (POSIX) file locking in the user's home directory without exposing network listeners.
- **Store preflight & LGPLv3 weak-copyleft boundary (`#511`):** `tools/store_readiness.py` (`--store-preflight`) validates source-tree manifest metadata, icon dimensions, and policy disclosures only (`claim_boundary: source_and_metadata_preflight_only`). It does not substitute for MSIX binary packaging, Authenticode certificate signing, or Windows App Certification Kit (WACK) verification. Note that runtime dependency `pystray` is licensed under `LGPL-3.0-or-later` and imported dynamically at runtime; standalone frozen MSIX binaries must satisfy LGPLv3 §4 notice/relinking obligations (see `THIRD_PARTY_LICENSES.md`).

### Supported Versions

| Version | Supported |
|---------|-----------|
| `0.1.x` (`0.1.2`) | Yes (`master`) |
| `< 0.1.0` | No |

### Reporting a Vulnerability & Response SLAs (`INV-SLA-09` / `INV-SLA-10`)

Please **do not** report unpatched security vulnerabilities through public GitHub issues, pull requests, or discussions.

Report vulnerabilities privately via **GitHub Private Vulnerability Reporting**:
- **Advisory Portal:** <https://github.com/ellmos-ai/ellmos-tray/security/advisories/new>

Include affected version, platform, minimal reproduction steps, and impact assessment. Never include live production tokens or personal credentials in reports.

Our binding response and remediation targets (`INV-SLA-09` & `INV-SLA-10`):
- **Acknowledgement:** within **48 hours**
- **Initial triage & severity assessment:** within **5 business days**
- **Remediation SLA (patch or documented mitigation for confirmed vulnerabilities):** within **30 calendar days**

---

## Deutsch (Sicherheitsrichtlinie)

### Geltungsbereich & Bedrohungsmodell

`ellmos-tray` ist ein nach dem Local-First-Prinzip entwickelter System-Tray-Client und Desktop-Schnellsteuerungs-Begleiter für lokale KI-Laufzeitumgebungen (`ELLMOS`, `BACH`, `OCEAN`):

- **Loopback als Standard:** Ohne explizite Nutzerparameter (`--host`, `--gui-url`) richten sich sämtliche HTTP-Verbindungen ausschließlich an `127.0.0.1` (`localhost`).
- **Keine Telemetrie oder Nachverfolgung:** Der Client enthält weder Analyse-SDKs noch Absturz-Uploader oder externe Telemetrie-Endpunkte.
- **Control-API-Bearer-Token-, Header- & Redirect-Grenze (`#510`):**
  - Bei Authentifizierung gegenüber der lokalen Control API (`BACH_CONTROL_API_TOKEN`, `CONTROL_API_AUTH_HEADER`, `BACH_CONTROL_API_TOKEN_FILE` oder lokale Token-Datei) wird der `Authorization`-Header strikt nur an Anfragen gegen die konfigurierte `base_url` angehängt.
  - Header-Werte mit eingebetteten Steuerzeichen (`CR`/`LF`/`NUL`) werden fail-closed abgewiesen (`CWE-113`), und HTTP-Antworten sind auf maximal `4 MiB` (`MAX_API_RESPONSE_BYTES`, `CWE-400`) begrenzt.
  - Authentifizierte Anfragen unterbinden HTTP-Weiterleitungen über `_NoControlRedirect` und prüfen `Same-Origin`, sodass Bearer-Zugangsdaten niemals über Ursprungsgrenzen hinweg weitergeleitet werden.
- **HTTP(S)-Schema-Prüfung & Argument-Schutz:** Alle Browser-Aufrufe (`gui_url`, `telegram_url`, Direktzugriffe) prüfen vor `webbrowser.open` zwingend auf ein explizites `http`-/`https`-Schema (`is_safe_http_url`), um lokale `file://`-, UNC/SMB- oder Protokoll-Handler-Aufrufe auszuschließen. Legacy-Git-Aufrufe übergeben `--` an `git add` (`CWE-88`) und codieren dynamische URL-Parameter.
- **Betriebssystem-basierte Single-Instance-Sperre:** Die Einzelinstanz-Sicherung nutzt dateibasierte Byte-Range-Sperren (`msvcrt` unter Windows bzw. `flock` unter POSIX) im Benutzerverzeichnis ohne offene Netzwerk-Sockets.
- **Store-Preflight- & LGPLv3-Grenze (`#511`):** `tools/store_readiness.py` (`--store-preflight`) prüft ausschließlich Quellbaum-Metadaten, Icon-Abmessungen und Dokumentationspflichten (`claim_boundary: source_and_metadata_preflight_only`) und ersetzt weder MSIX-Paketbau noch Authenticode-Signierung oder WACK-Zertifizierungsläufe. Die Laufzeitabhängigkeit `pystray` steht unter `LGPL-3.0-or-later` (dynamischer Python-Import); bei späterer Binär-Bündelung (MSIX/PyInstaller) gelten die Hinweis- und Austauschpflichten nach LGPLv3 §4 (siehe `THIRD_PARTY_LICENSES.md`).

### Unterstützte Versionen

| Version | Unterstützt |
|---------|-------------|
| `0.1.x` (`0.1.2`) | Ja (`master`) |
| `< 0.1.0` | Nein |

### Sicherheitslücken melden & Reaktionsfristen (`INV-SLA-09` / `INV-SLA-10`)

Bitte melden Sie ungepatchte Sicherheitslücken **niemals** über öffentliche GitHub-Issues, Pull-Requests oder Diskussionen.

Nutzen Sie ausschließlich die vertrauliche Meldung über **GitHub Private Vulnerability Reporting**:
- **Sicherheitsmeldung einreichen:** <https://github.com/ellmos-ai/ellmos-tray/security/advisories/new>

Verbindliche Reaktions- und Behebungsziele (`INV-SLA-09` & `INV-SLA-10`):
- **Eingangsbestätigung:** innerhalb von **48 Stunden**
- **Ersteinschätzung & Schweregrad-Triage:** innerhalb von **5 Werktagen**
- **Behebungszusage (Patch oder dokumentierte Risikominderung für bestätigte Schwachstellen):** innerhalb von **30 Kalendertagen**
