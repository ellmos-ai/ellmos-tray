# Third-Party Licenses & Level-1 SBOM (`ellmos-tray`)

- **Package:** `ellmos-tray` (`0.1.2`)
- **Project License:** `MIT` (see [LICENSE](LICENSE))
- **Repository:** <https://github.com/ellmos-ai/ellmos-tray>
- **Re-Audit:** `2026-11-15`

---

## 1. Direct Runtime Dependencies (`[project.dependencies]`)

| Package | Version Constraint | Audited Version | SPDX License | Upstream | Linkage & Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `pystray` | `>=0.19.5` | `0.19.5` | `LGPL-3.0-or-later` | <https://github.com/moses-palmer/pystray> | Dynamic Python runtime import (`import pystray`) for taskbar/notification area integration; unmodified PyPI package, neither vendored nor statically linked. |
| `Pillow` | `>=10.0.0` | `12.3.0` | `MIT-CMU` (HPND) | <https://github.com/python-pillow/Pillow> | Dynamic Python runtime import (`from PIL import Image, ImageDraw, ImageFont`) for RGBA status icon rendering and Store asset checks. |

---

## 2. Transitive & Platform-Conditional Runtime Packages

| Package | Condition / Origin | Audited Version | SPDX License | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `six` | via `pystray` (all platforms) | `1.17.0` | `MIT` | Pure-Python compatibility helper imported dynamically by `pystray`. |
| `pyobjc-framework-Quartz` | `sys_platform == "darwin"` (via `pystray`) | `>=7.0` | `MIT` | macOS AppKit/Quartz bridge used by `pystray` on macOS only. |
| `python-xlib` | `sys_platform == "linux"` (via `pystray`) | `>=0.17` | `LGPL-2.1-or-later` | X11 protocol client used by `pystray` on Linux Xorg environments only (unmodified runtime import). |

---

## 3. Development & Quality-Gate Dependencies (`[project.optional-dependencies].dev`)

Development dependencies are used exclusively for testing and static analysis and are **not** required or distributed at runtime:

| Package | Version Constraint | Audited Version | SPDX License | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `pytest` | `>=8.0` | `9.1.1` | `MIT` | Automated unit, integration, and metadata contract test runner. |
| `ruff` | `>=0.11` | `0.15.18` | `MIT` | Static Python linter and import sorter. |

---

## 4. Weak-Copyleft Boundary Note (`E08` / LGPLv3 §4 Compliance)

1. **Source & Wheel Distribution (`pip install ellmos-tray`):**
   `ellmos-tray` itself is licensed under the permissive **MIT License**. It declares `pystray>=0.19.5` (`LGPL-3.0-or-later`) as an external PyPI dependency in `pyproject.toml` and loads it unmodified at runtime via Python's standard module import mechanism. No `pystray` or `python-xlib` code is copied, modified, or statically linked in this repository.
2. **Frozen Binary / MSIX Packaging Notice (`#511`):**
   If a downstream distributor packages `ellmos-tray` together with `pystray` (or `python-xlib` on Linux) into a frozen single-executable or MSIX bundle, the distributor must preserve the `LGPL-3.0-or-later` license text and copyright notices for `pystray` and satisfy LGPLv3 §4 user-relinking / replaceable-module requirements alongside the external Store release gates documented in `tools/store_readiness.py`.

---

## 5. Supply-Chain & Security Governance Invariants

| Invariant | Status | Verification & Policy |
| :--- | :--- | :--- |
| `INV-LIC-01` (Project License & PEP 639) | `PASS` | `MIT` in `LICENSE` and `pyproject.toml` (`license-files = ["LICENSE", "THIRD_PARTY_LICENSES.md"]`). |
| `INV-SBOM-02` (Dependency Integrity) | `PASS` | `pip check` clean (`0` broken requirements); automated weekly monitoring via `.github/dependabot.yml` (`pip` & `github-actions`). |
| `INV-E08-03` (Copyleft Boundary) | `PASS` | `0` AGPL/GPL strong-copyleft dependencies; `pystray` (`LGPL-3.0-or-later`) isolated as unmodified dynamic runtime import with explicit MSIX freeze notice. |
| `INV-PRIV-04` (Zero Telemetry & Loopback) | `PASS` | `127.0.0.1` default, `_NoControlRedirect` bearer protection (`#510`), HTTP(S)-only browser guard, `0` hardcoded personal paths. |
| `INV-SLA-09` (Acknowledgement & Triage SLA) | `PASS` | **48 hours** acknowledgement (`48 Stunden` Bestätigung) and **5 business days** initial triage (`5 Werktage` Ersteinschätzung) in `SECURITY.md`. |
| `INV-SLA-10` (Remediation SLA) | `PASS` | Binding **30 calendar days** remediation SLA (`30 Kalendertage` Behebungszusage) for confirmed vulnerabilities in `SECURITY.md`. |
