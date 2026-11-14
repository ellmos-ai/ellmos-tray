# Security Policy

## Scope & Threat Model

`ellmos-tray` is a local-first system tray client and quick-control companion for local AI runtimes (ELLMOS, BACH, OCEAN). By design:

- **Loopback by default:** Without explicit user flags (`--host`, `--gui-url`), all HTTP connections target `127.0.0.1` (`localhost`).
- **No telemetry or tracking:** The tray client does not bundle analytics SDKs, crash uploaders, or remote telemetry endpoints.
- **Control API bearer token & redirect boundary (#510):** When authenticating against the local Control API (`BACH_CONTROL_API_TOKEN` or a user-configured token), `Authorization` headers are attached strictly to requests targeting the configured `base_url`. Authenticated requests disable redirect following via `_NoControlRedirect`, rejecting redirects fail-closed so bearer credentials are never forwarded across origins.
- **Single-instance OS lock:** Single-instance enforcement uses OS-level byte-range file locking in the user's home/temp directory without exposing network listeners.
- **Store preflight claim boundary (#511):** `tools/store_readiness.py` (`--store-preflight`) validates source-tree manifest metadata, icon asset dimensions, and policy documentation only (`claim_boundary: source_and_metadata_preflight_only`). It does not substitute for Authenticode signing, MSIX packaging, or Windows App Certification Kit (WACK) verification.

## Supported Versions

| Version | Supported |
|---------|-----------|
| `0.1.x` | Yes (`master`) |

## Reporting a Vulnerability

Please report security issues privately via GitHub Security Advisories on `https://github.com/ellmos-ai/ellmos-tray/security/advisories` or contact the maintainers via `https://github.com/ellmos-ai/ellmos-tray/issues` (without posting sensitive secrets or exploit payloads publicly).

We aim to acknowledge reports within 7 days and ship a fix or mitigation guidance promptly once reproduced.
