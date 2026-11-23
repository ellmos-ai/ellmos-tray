# Pre-Release & Maintenance TODO: ellmos-tray

**Last Checked:** 2026-11-23
**Target Repo:** `ellmos-ai/ellmos-tray`
**Current Package Version:** `0.1.2`

---

## BLOCKER

> Resolved for public release readiness.

- [x] **Secrets:** No API keys, tokens, or passwords in tracked files
- [x] **Private Data:** No personal PII emails or author secrets leaked in tracked files
- [x] **Hardcoded Paths:** No personal user home paths hardcoded in tracked files (`Path.home()` used across Windows, macOS, Linux)
- [x] **Database Files:** No `.db` files tracked
- [x] **.env Files:** No `.env` files tracked
- [x] **BACH Internals:** No internal BACH-only architecture docs in public repo
- [x] **.gitignore:** Standard and security entries present (`__pycache__`, `*.pyc`, `.env`, `*.db`, `.venv/`, `.idea/`, `.vscode/`, `data/`, SSH/key/cert/token wildcards, sync/lock exclusions)
- [x] **LICENSE & SBOM:** MIT `LICENSE` and `THIRD_PARTY_LICENSES.md` (Level-1 SBOM with `pystray` LGPLv3 dynamic-import boundary) present
- [x] **README.md:** English `README.md` and synchronized German `README_de.md` present and complete

---

## HIGH PRIORITY

- [x] Package metadata, PEP 639 `license-files`, `[project.urls]` & PEP 561 `py.typed` marker included
- [x] Canonical `ellmos-module.v2.json` tracked in Git repository root
- [x] Bilingual `SECURITY.md` (`48h` ack / `5d` triage / `30d` remediation SLA), `THIRD_PARTY_LICENSES.md`, and `CHANGELOG.md` added
- [x] Keep `README_de.md` synchronized with English `README.md` (`--smoke-promptboard` and `#510`/`#511` claim boundaries)
- [x] Add GitHub Actions CI workflow (`.github/workflows/ci.yml`) and Dependabot supply-chain monitoring (`.github/dependabot.yml`)

---

## MEDIUM PRIORITY

- [ ] MSIX packaging, Authenticode certificate signing, and WACK binary verification (external release gates documented in `tools/store_readiness.py` & LGPLv3 §4 notice in `THIRD_PARTY_LICENSES.md`)
- [x] Add `CONTRIBUTING.md` (`CODE_OF_CONDUCT.md`, `SKILL.md`, `llms.txt`, `llm.txt`, `MANIFEST.in`, `.github/ISSUE_TEMPLATE/*`)
- [ ] Optional PyPI release automation

---

## STATUS

| Category | Status | Notes |
|----------|--------|-------|
| Secrets | :green_circle: PASS | Verified by `final_gate_check.py` & contract tests |
| Private Data (PII) | :green_circle: PASS | Verified by `final_gate_check.py` & zero-personal-path tests |
| .gitignore | :green_circle: PASS | Hardened (`*.pyc`, `*.db`, `data/`, `.env.*`, SSH/key/cert/token/sync patterns) |
| Language (English) | :green_circle: PASS | `README.md` in English; synchronized `README_de.md` companion provided |
| BACH Internals | :green_circle: PASS | No internal BACH docs tracked |
| Database Files | :green_circle: PASS | No `.db` files tracked |
| README.md | :green_circle: PASS | Present with usage, SBOM link & `#510`/`#511` security boundaries |
| LICENSE | :green_circle: PASS | MIT License + `THIRD_PARTY_LICENSES.md` (Level-1 SBOM) |
| **Overall** | **READY** | **All 10 release gates passing** |

**Audit Date:** 2026-11-15
**Gate Check Exit Code:** `0`
