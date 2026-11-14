# Pre-Release & Maintenance TODO: ellmos-tray

**Last Checked:** 2026-11-14
**Target Repo:** `ellmos-ai/ellmos-tray`
**Current Package Version:** `0.1.2`

---

## BLOCKER

> Resolved for public release readiness.

- [x] **Secrets:** No API keys, tokens, or passwords in tracked files
- [x] **Private Data:** No personal PII emails or author secrets leaked in tracked files
- [x] **Hardcoded Paths:** No personal user home paths hardcoded in tracked files
- [x] **Database Files:** No `.db` files tracked
- [x] **.env Files:** No `.env` files tracked
- [x] **BACH Internals:** No internal BACH-only architecture docs in public repo
- [x] **.gitignore:** Standard entries present (`__pycache__`, `*.pyc`, `.env`, `*.db`, `.venv/`, `.idea/`, `.vscode/`, `data/`)
- [x] **LICENSE:** MIT license file present
- [x] **README.md:** English README present and complete

---

## HIGH PRIORITY

- [x] Package metadata & PEP 561 `py.typed` marker included
- [x] Canonical `ellmos-module.v2.json` tracked in Git repository root
- [x] `SECURITY.md` and `CHANGELOG.md` added
- [ ] Keep `README_de.md` synchronized with English `README.md` (`--smoke-promptboard` and `#510`/`#511` claim boundaries)
- [ ] Add GitHub Actions CI workflow (`.github/workflows/ci.yml`) for `pytest`, `ruff`, `store_readiness.py`, and `final_gate_check.py`

---

## MEDIUM PRIORITY

- [ ] MSIX packaging, Authenticode certificate signing, and WACK binary verification (external release gates documented in `tools/store_readiness.py`)
- [ ] Add `CONTRIBUTING.md`
- [ ] Optional PyPI release automation

---

## STATUS

| Category | Status | Notes |
|----------|--------|-------|
| Secrets | :green_circle: PASS | Verified by `final_gate_check.py` |
| Private Data (PII) | :green_circle: PASS | Verified by `final_gate_check.py` |
| .gitignore | :green_circle: PASS | Hardened (`*.pyc`, `*.db`, `data/`, `.env.*`, key/cert patterns) |
| Language (English) | :green_circle: PASS | `README.md` in English; `README_de.md` companion provided |
| BACH Internals | :green_circle: PASS | No internal BACH docs tracked |
| Database Files | :green_circle: PASS | No `.db` files tracked |
| README.md | :green_circle: PASS | Present with usage & `#510`/`#511` security boundaries |
| LICENSE | :green_circle: PASS | MIT License |
| **Overall** | **READY** | **All 10 release gates passing** |

**Audit Date:** 2026-11-14
**Gate Check Exit Code:** `0`
