"""
Prompt management and PromptBoard integration for ellmos-tray.
Supports loading native prompt definitions, PromptBoard libraries, and system clipboard operations.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

DEFAULT_PROMPTS = {
    "Aufgaben": {
        "Offene Tasks zeigen": "Zeige alle offenen Tasks sortiert nach Priorität",
        "Tagesplan erstellen": "Erstelle einen Tagesplan basierend auf meinen offenen Tasks und Prioritäten",
        "Nächste Aufgabe": "Was ist die wichtigste Aufgabe die ich als nächstes erledigen sollte?",
    },
    "System": {
        "Systemstatus": "Gib einen Überblick über den aktuellen Systemstatus",
        "Wartungscheck": "Führe einen Wartungscheck durch: DB-Größe, Logs, offene Issues",
        "Übersetzungen prüfen": "Prüfe die Qualität der Übersetzungen in der Datenbank und berichte Probleme",
    },
    "Wissen": {
        "Memory durchsuchen": "Durchsuche mein Memory nach: ",
        "Zusammenfassung": "Fasse die letzten Aktivitäten und Änderungen zusammen",
        "Facts abrufen": "Zeige alle gespeicherten Facts",
    },
}

ENV_LIBRARY_KEYS = ("ELLMOS_PROMPTBOARD_LIBRARY", "BACH_PROMPTBOARD_LIBRARY")
ENV_APP_KEYS = ("ELLMOS_PROMPTBOARD_APP", "BACH_PROMPTBOARD_APP")


class PromptManager:
    """Discovers, loads, and manages prompts and PromptBoard application integration."""

    def __init__(self, custom_library_path: Path | None = None):
        self.custom_library_path = custom_library_path
        self.prompt_source: str = "defaults"
        self.prompts: dict[str, dict[str, str]] = self.load_prompts()

    def _coerce_prompt_mapping(self, payload: Any) -> dict[str, dict[str, str]]:
        if not isinstance(payload, dict):
            return {}

        # Native mapping: {"Category": {"Name": "Text"}}
        native: dict[str, dict[str, str]] = {}
        for category, items in payload.items():
            if not isinstance(items, dict):
                continue
            clean_prompts = {
                str(name): str(text)
                for name, text in items.items()
                if str(name).strip() and str(text).strip()
            }
            if clean_prompts:
                native[str(category) or "Prompts"] = clean_prompts
        if native:
            return native

        # PromptBoard items format: {"items": [{name, content, category, item_type}]}
        items_list = payload.get("items")
        if not isinstance(items_list, list):
            return {}

        imported: dict[str, dict[str, str]] = {}
        for item in items_list:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "").strip()
            content = str(item.get("content") or "").strip()
            if not name or not content:
                continue
            cat = str(item.get("category") or item.get("item_type") or "PromptBoard").strip()
            imported.setdefault(cat or "PromptBoard", {})[name] = content
        return imported

    def _read_prompt_file(self, path: Path) -> dict[str, dict[str, str]]:
        try:
            with open(path, encoding="utf-8") as f:
                return self._coerce_prompt_mapping(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

    def _promptboard_project_dir(self) -> Path | None:
        user_profile = os.environ.get("USERPROFILE")
        if not user_profile:
            return None
        project_dir = (
            Path(user_profile)
            / "OneDrive"
            / ".TOPICS"
            / ".SOFTWARE"
            / "LLM"
            / "REL-PUB_PromptBoard"
        )
        return project_dir if project_dir.exists() else None

    def get_library_candidates(self) -> list[Path]:
        candidates: list[Path] = []
        if self.custom_library_path:
            candidates.append(self.custom_library_path)

        for env_k in ENV_LIBRARY_KEYS:
            env_val = os.environ.get(env_k)
            if env_val:
                candidates.append(Path(env_val).expanduser())

        candidates.append(Path.home() / ".config" / "ellmos" / "prompts.json")
        candidates.append(Path.home() / ".config" / "bach" / "prompts.json")
        candidates.append(Path.home() / ".promptboard" / "library.json")

        appdata = os.environ.get("APPDATA")
        if appdata:
            candidates.append(Path(appdata) / "PromptBoard" / "library.json")

        project_dir = self._promptboard_project_dir()
        if project_dir:
            candidates.extend([
                project_dir / "library.json",
                project_dir / "data" / "library.json",
            ])

        return candidates

    def get_app_candidates(self) -> list[Path]:
        candidates: list[Path] = []
        for env_k in ENV_APP_KEYS:
            env_val = os.environ.get(env_k)
            if env_val:
                candidates.append(Path(env_val).expanduser())

        project_dir = self._promptboard_project_dir()
        if project_dir:
            dist_dir = project_dir / "dist"
            if dist_dir.exists():
                candidates.extend(
                    sorted(
                        dist_dir.glob("PromptBoard-*-win64.exe"),
                        key=lambda p: p.stat().st_mtime,
                        reverse=True,
                    )
                )
            candidates.extend([
                project_dir / "start.bat",
                project_dir / "releases" / "PromptBoard.msix",
            ])
        return candidates

    def find_app_path(self) -> Path | None:
        for candidate in self.get_app_candidates():
            if candidate.exists():
                return candidate
        return None

    def load_prompts(self) -> dict[str, dict[str, str]]:
        for candidate in self.get_library_candidates():
            if candidate.exists():
                prompts = self._read_prompt_file(candidate)
                if prompts:
                    self.prompt_source = str(candidate)
                    return prompts

        self.prompt_source = "defaults"
        return DEFAULT_PROMPTS

    def smoke_snapshot(self) -> dict[str, Any]:
        """Returns snapshot diagnostics matching test suite contracts."""
        app_path = self.find_app_path()
        candidates_info = [
            {"path": str(cand), "exists": cand.exists()}
            for cand in self.get_library_candidates()
        ]
        prompt_count = sum(len(p) for p in self.prompts.values())
        return {
            "app_path": str(app_path) if app_path else None,
            "app_found": app_path is not None,
            "library_candidates": candidates_info,
            "library_found": any(item["exists"] for item in candidates_info),
            "menu_has_open_app": app_path is not None,
            "prompt_source": self.prompt_source,
            "using_default_prompts": self.prompt_source == "defaults",
            "prompt_categories": list(self.prompts.keys()),
            "prompt_count": prompt_count,
        }

    @staticmethod
    def copy_to_clipboard(text: str) -> bool:
        """Copies text to the system clipboard across platforms."""
        try:
            if sys.platform == "darwin":
                subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=False)
                return True
            elif sys.platform == "win32":
                subprocess.run(["clip"], input=text.encode("utf-16le"), check=False)
                return True
            else:
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=text.encode("utf-8"),
                    check=False,
                )
                return True
        except (FileNotFoundError, OSError):
            return False
