"""
Windows Store & MSIX Readiness Preflight Check.
Validates package metadata, publisher/identity placeholders, icon assets,
WACK certification criteria, offline & loopback exceptions, and produces a
machine-readable readiness report for Microsoft Store certification.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def check_msix_manifest(project_root: Path) -> tuple[bool, list[str], list[str]]:
    """Validates MSIX manifest and store package metadata configuration."""
    errors: list[str] = []
    warnings: list[str] = []

    package_file = project_root / "store_package.json"
    if not package_file.exists():
        errors.append("store_package.json is missing in project root.")
        return False, errors, warnings

    try:
        data = json.loads(package_file.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"store_package.json is invalid JSON: {exc}")
        return False, errors, warnings

    required_fields = [
        "app_name",
        "publisher",
        "publisher_display",
        "identity_name",
        "version",
        "description",
        "executable",
        "capabilities",
        "category",
        "age_rating",
        "privacy_url",
        "support_url",
    ]

    for field in required_fields:
        val = data.get(field)
        if not val or (isinstance(val, str) and not val.strip()):
            errors.append(f"store_package.json field '{field}' is missing or empty.")

    # Capabilities check: Desktop Bridge applications requires runFullTrust
    caps = data.get("capabilities", [])
    if isinstance(caps, list):
        if "runFullTrust" not in caps:
            warnings.append(
                "Capability 'runFullTrust' not declared in store_package.json; required for Desktop Bridge MSIX packaging."
            )
    else:
        errors.append("store_package.json 'capabilities' must be a list of strings.")

    # Version format check (e.g. 1.0.0.0)
    version = data.get("version", "")
    if version and not re.match(r"^\d+\.\d+\.\d+(\.\d+)?$", version):
        errors.append(f"store_package.json version '{version}' does not match MSIX 4-part quad format (e.g. 0.1.1.0).")

    return len(errors) == 0, errors, warnings


def check_publisher_placeholders(project_root: Path) -> tuple[bool, list[str], list[str]]:
    """Verifies publisher and identity fields do not contain dummy placeholders."""
    errors: list[str] = []
    warnings: list[str] = []

    package_file = project_root / "store_package.json"
    if not package_file.exists():
        return False, ["store_package.json is missing."], warnings

    try:
        data = json.loads(package_file.read_text(encoding="utf-8"))
    except Exception:
        return False, ["Invalid store_package.json."], warnings

    pub = str(data.get("publisher", "")).strip()
    placeholder_patterns = [
        r"^CN=YourPublisher",
        r"^CN=Placeholder",
        r"^CN=TODO",
        r"^CN=MyCompany",
        r"example\.com",
        r"your-company",
    ]
    for pattern in placeholder_patterns:
        if re.search(pattern, pub, re.IGNORECASE):
            errors.append(f"Publisher identity contains placeholder: '{pub}'. Must be real certificate CN.")

    identity = str(data.get("identity_name", "")).strip()
    if " " in identity:
        errors.append(f"Identity name '{identity}' contains illegal spaces.")
    if not re.match(r"^[A-Za-z0-9\.\-]+$", identity):
        errors.append(f"Identity name '{identity}' contains illegal characters.")

    return len(errors) == 0, errors, warnings


def check_assets_and_icons(project_root: Path) -> tuple[bool, list[str], list[str]]:
    """Checks required Windows Store icon assets and dimensions."""
    errors: list[str] = []
    warnings: list[str] = []

    asset_dir = project_root / "store_assets"
    if not asset_dir.exists():
        errors.append("Directory 'store_assets/' is missing in project root.")
        return False, errors, warnings

    expected_assets = {
        "Square44x44Logo.png": (44, 44),
        "Square150x150Logo.png": (150, 150),
        "Wide310x150Logo.png": (310, 150),
        "Square310x310Logo.png": (310, 310),
        "StoreLogo.png": (50, 50),
    }

    try:
        from PIL import Image
        pil_available = True
    except ImportError:
        pil_available = False
        warnings.append("Pillow (PIL) not installed; image dimensions will not be verified.")

    for filename, (req_w, req_h) in expected_assets.items():
        file_path = asset_dir / filename
        if not file_path.exists():
            errors.append(f"Store asset '{filename}' is missing in store_assets/.")
            continue

        size = file_path.stat().st_size
        if size < 100:
            errors.append(f"Store asset '{filename}' is suspiciously small ({size} bytes).")
            continue

        if pil_available:
            try:
                with Image.open(file_path) as img:
                    if img.size != (req_w, req_h):
                        warnings.append(
                            f"Asset '{filename}' has dimensions {img.size}; recommended: ({req_w}, {req_h})."
                        )
                    if img.format != "PNG":
                        errors.append(f"Asset '{filename}' must be in PNG format (found: {img.format}).")
            except Exception as exc:
                errors.append(f"Asset '{filename}' cannot be parsed as valid image: {exc}")

    return len(errors) == 0, errors, warnings


def generate_store_assets(project_root: Path, branding_char: str = "E") -> list[Path]:
    """Generates standard Windows Store icon assets in store_assets/ if missing."""
    from PIL import Image, ImageDraw, ImageFont

    asset_dir = project_root / "store_assets"
    asset_dir.mkdir(parents=True, exist_ok=True)

    expected_assets = {
        "Square44x44Logo.png": (44, 44),
        "Square150x150Logo.png": (150, 150),
        "Wide310x150Logo.png": (310, 150),
        "Square310x310Logo.png": (310, 310),
        "StoreLogo.png": (50, 50),
    }

    # Brand palette (Dark slate blue with vibrant emerald accent)
    bg_color = (24, 32, 47, 255)
    accent_color = (0, 200, 100, 255)

    created: list[Path] = []
    for filename, (w, h) in expected_assets.items():
        target = asset_dir / filename
        if target.exists() and target.stat().st_size > 100:
            continue

        img = Image.new("RGBA", (w, h), bg_color)
        draw = ImageDraw.Draw(img)

        # Rounded inner card
        pad = max(2, int(min(w, h) * 0.08))
        radius = max(3, int(min(w, h) * 0.15))
        draw.rounded_rectangle([pad, pad, w - pad, h - pad], radius=radius, fill=accent_color)

        # Draw glyph
        font_size = max(12, int(min(w, h) * 0.5))
        font = None
        try:
            if sys.platform == "win32":
                font = ImageFont.truetype("arial", font_size)
            else:
                font = ImageFont.load_default()
        except Exception:
            font = None

        text = branding_char
        if font:
            try:
                bbox = font.getbbox(text)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
                draw.text(((w - tw) / 2, (h - th) / 2 - 2), text, fill="white", font=font)
            except Exception:
                draw.text((w // 3, h // 4), text, fill="white", font=font)
        else:
            draw.text((w // 3, h // 4), text, fill="white")

        img.save(target, format="PNG")
        created.append(target)

    return created


def check_wack_criteria(project_root: Path) -> tuple[bool, list[str], list[str]]:
    """Verifies Windows App Certification Kit (WACK) compliance criteria."""
    errors: list[str] = []
    warnings: list[str] = []

    package_file = project_root / "store_package.json"
    if not package_file.exists():
        return False, ["store_package.json missing."], warnings

    try:
        data = json.loads(package_file.read_text(encoding="utf-8"))
    except Exception:
        return False, ["store_package.json invalid."], warnings

    # Executable specified
    exe = data.get("executable", "")
    if not exe:
        errors.append("WACK: No executable entrypoint defined in store_package.json.")
    elif not (exe.endswith(".exe") or exe.endswith(".cmd") or exe.endswith(".bat")):
        warnings.append(f"Executable '{exe}' does not have standard Windows binary extension.")

    # Category validity
    category = data.get("category", "")
    valid_categories = [
        "DeveloperTools", "Productivity", "Utilities", "UtilitiesAndTools", "Education"
    ]
    if category and category not in valid_categories:
        warnings.append(f"Category '{category}' is non-standard for Microsoft Store.")

    return len(errors) == 0, errors, warnings


def check_offline_and_loopback(project_root: Path) -> tuple[bool, list[str], list[str]]:
    """Checks Microsoft Store offline and loopback policy documentation requirements."""
    errors: list[str] = []
    warnings: list[str] = []

    listing_file = project_root / "STORE_LISTING.md"
    if not listing_file.exists():
        errors.append("STORE_LISTING.md is missing in project root.")
        return False, errors, warnings

    content = listing_file.read_text(encoding="utf-8", errors="replace")

    # Store certification requires loopback / localhost communication disclosure
    loopback_keywords = ["loopback", "127.0.0.1", "localhost", "local server"]
    found_loopback = any(kw.lower() in content.lower() for kw in loopback_keywords)
    if not found_loopback:
        errors.append(
            "STORE_LISTING.md must contain explicit disclosure of local loopback network communication "
            "(127.0.0.1) for Microsoft Store Certification reviewers."
        )

    # Reviewer notes check
    if "Prüferhinweise" not in content and "Certification Notes" not in content:
        warnings.append(
            "STORE_LISTING.md should contain a 'Certification Notes' / 'Prüferhinweise' section for testers."
        )

    # Privacy policy check
    privacy_file = project_root / "PRIVACY_POLICY.md"
    if not privacy_file.exists():
        errors.append("PRIVACY_POLICY.md is missing in project root.")
    else:
        priv_text = privacy_file.read_text(encoding="utf-8", errors="replace")
        if "local" not in priv_text.lower() and "lokal" not in priv_text.lower():
            warnings.append("PRIVACY_POLICY.md should emphasize local-first data processing.")

    return len(errors) == 0, errors, warnings


def check_documentation_files(project_root: Path) -> tuple[bool, list[str], list[str]]:
    """Validates presence and completeness of all required documentation files."""
    errors: list[str] = []
    warnings: list[str] = []

    required_docs = [
        ("STORE_LISTING.md", 200),
        ("PRIVACY_POLICY.md", 200),
        ("README.md", 100),
        ("LICENSE", 50),
    ]

    for filename, min_len in required_docs:
        path = project_root / filename
        if not path.exists():
            errors.append(f"Required document '{filename}' is missing.")
        elif path.stat().st_size < min_len:
            errors.append(f"Required document '{filename}' is suspiciously short ({path.stat().st_size} bytes).")

    return len(errors) == 0, errors, warnings


def run_store_readiness_check(
    project_root: Path | None = None,
) -> tuple[bool, dict[str, Any]]:
    """Runs the complete suite of Windows Store readiness checks and returns report."""
    root = project_root or PROJECT_ROOT
    checks: dict[str, dict[str, Any]] = {}
    all_errors: list[str] = []
    all_warnings: list[str] = []

    check_functions = [
        ("msix_manifest", check_msix_manifest),
        ("publisher_identity", check_publisher_placeholders),
        ("assets_icons", check_assets_and_icons),
        ("wack_criteria", check_wack_criteria),
        ("offline_loopback", check_offline_and_loopback),
        ("documentation", check_documentation_files),
    ]

    for check_name, func in check_functions:
        ok, errs, warns = func(root)
        checks[check_name] = {
            "status": "PASS" if ok else "FAIL",
            "errors": errs,
            "warnings": warns,
        }
        all_errors.extend(errs)
        all_warnings.extend(warns)

    passed = len(all_errors) == 0
    total_checks = len(check_functions)
    passed_checks = sum(1 for c in checks.values() if c["status"] == "PASS")

    report: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "project_root": str(root),
        "overall_status": "READY" if passed else "FAILED",
        "passed": passed,
        "summary": {
            "total_checks": total_checks,
            "passed": passed_checks,
            "failed": total_checks - passed_checks,
            "errors_count": len(all_errors),
            "warnings_count": len(all_warnings),
        },
        "checks": checks,
        "errors": all_errors,
        "warnings": all_warnings,
    }

    return passed, report


def main() -> None:
    parser = argparse.ArgumentParser(description="Windows Store & MSIX Readiness Preflight Check")
    parser.add_argument(
        "--root",
        type=Path,
        default=PROJECT_ROOT,
        help=f"Project root directory (default: {PROJECT_ROOT})",
    )
    parser.add_argument("--json", action="store_true", help="Output results in machine-readable JSON format")
    parser.add_argument("--output", type=Path, default=None, help="Save JSON report to file")
    parser.add_argument(
        "--generate-assets",
        action="store_true",
        help="Generate missing standard Windows Store icons in store_assets/",
    )
    parser.add_argument(
        "--brand-char",
        default="E",
        help="Branding character for generated icons (default: E)",
    )

    args = parser.parse_args()

    if args.generate_assets:
        created = generate_store_assets(args.root, branding_char=args.brand_char)
        if not args.json:
            print(f"Generated {len(created)} store assets in {args.root / 'store_assets'}")

    passed, report = run_store_readiness_check(args.root)

    if args.output:
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("\n========================================================")
        print("Windows Store Readiness Preflight Check")
        print(f"Root: {args.root}")
        print(f"Status: {report['overall_status']}")
        print("========================================================\n")
        for cname, cdata in report["checks"].items():
            status_symbol = "PASS" if cdata["status"] == "PASS" else "FAIL"
            print(f"  [{status_symbol}] {cname}")
            for err in cdata["errors"]:
                print(f"      - ERROR: {err}")
            for warn in cdata["warnings"]:
                print(f"      - WARNING: {warn}")

        print(f"\nSummary: {report['summary']['passed']}/{report['summary']['total_checks']} checks passed. "
              f"({report['summary']['errors_count']} errors, {report['summary']['warnings_count']} warnings)")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
