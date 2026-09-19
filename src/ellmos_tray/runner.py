"""
Task execution delegates for ellmos-tray.
Allows decoupling the desktop UI from the background task execution engine (agents-heart, workers, or legacy idle runner).
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ellmos_tray.app import TrayApp


class TaskExecutionDelegate:
    """Base interface for background or idle task execution handlers."""

    def on_poll_tick(self, app: TrayApp) -> None:
        """Called on every polling cycle while the tray is running."""
        pass

    def is_processing(self) -> bool:
        """Returns True if a task is currently executing."""
        return False

    def get_current_task_name(self) -> Optional[str]:
        """Returns the title of the currently executing task, if any."""
        return None

    def toggle_enabled(self) -> bool:
        """Toggles execution capability and returns new enabled state."""
        return False

    @property
    def is_enabled(self) -> bool:
        """Returns whether this execution delegate is enabled."""
        return False


class PassiveTaskDelegate(TaskExecutionDelegate):
    """Default delegate: The tray is an observer only.
    Execution is handled by backend daemons (agents-heart, worker pools).
    """

    def __init__(self, enabled: bool = True):
        self._enabled = enabled

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def toggle_enabled(self) -> bool:
        self._enabled = not self._enabled
        return self._enabled


class LegacyBachIdleRunner(TaskExecutionDelegate):
    """Backward-compatible standalone idle task worker for BACH OS environments.
    Extracts the execution logic from chat_tray.py with configurable repo directories.
    """

    POLL_INTERVAL = 5
    IDLE_THRESHOLD = 12  # 12 * 5s = 60s
    IDLE_CHAT_ID = "idle-worker"
    PENDING_TTL = 1800

    def __init__(
        self,
        repo_dir: Optional[Path] = None,
        enabled: Optional[bool] = None,
    ):
        if enabled is not None:
            self._enabled = enabled
        else:
            self._enabled = os.environ.get("BACH_IDLE_WORKER", "1").strip().lower() not in (
                "0",
                "false",
                "no",
                "off",
            )
        self.repo_dir = repo_dir or self._detect_repo_dir()
        self.consecutive_idle = 0
        self.current_task_name: Optional[str] = None
        self.processing = False
        self.pending_task: Optional[tuple[Any, ...]] = None
        self._recurring_tick = 0

    def _detect_repo_dir(self) -> Path:
        env_repo = os.environ.get("BACH_REPO_DIR")
        if env_repo and Path(env_repo).is_dir():
            return Path(env_repo)
        if sys.platform == "darwin":
            mac_path = Path("/Users/lukas/services/bach")
            if mac_path.is_dir():
                return mac_path
        local_dev = Path(r"C:\_Local_DEV\repos\bach")
        if local_dev.is_dir():
            return local_dev
        return Path.cwd()

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def toggle_enabled(self) -> bool:
        self._enabled = not self._enabled
        if not self._enabled:
            self.consecutive_idle = 0
        return self._enabled

    def is_processing(self) -> bool:
        return self.processing

    def get_current_task_name(self) -> Optional[str]:
        return self.current_task_name

    def on_poll_tick(self, app: TrayApp) -> None:
        always_on = app.slots.get("buddha_always_on", {})
        if not self._enabled or not always_on.get("enabled", True) or self.processing:
            return

        active = app.state.get("active_sessions", app.state.get("sessions", 0))
        if active > 0:
            self.consecutive_idle = 0
            return

        self.consecutive_idle += 1
        self._recurring_tick += 1

        if self.consecutive_idle >= self.IDLE_THRESHOLD:
            threading.Thread(target=self._process_idle_task, args=(app,), daemon=True).start()

    @staticmethod
    def _resolve_role(assignee: str) -> tuple[str, str, str]:
        if not assignee or assignee.upper() in ("BACH", "BUDDHA", "OLLAMA"):
            return ("bach", "Buddha", "Universeller lokaler KI-Worker von BACH.")

        clean = assignee.lower().replace("agent:", "").replace("-agent", "").strip()

        PERSONA_MAP = {
            "persoenlich": ("Paul", "Persoenlicher Assistent fuer Alltags- und Arbeitsorganisation"),
            "persoenlicher-assistent": ("Paul", "Persoenlicher Assistent fuer Alltags- und Arbeitsorganisation"),
            "aboservice": ("Anton", "Experte fuer Abonnements, Vertraege und wiederkehrende Zahlungen"),
            "ati": ("Atlas", "Experte fuer Aufgaben-, Tool- und Code-Scanning"),
            "bewerbungsexperte": ("Benjamin", "Experte fuer Bewerbungsunterlagen, Lebenslaeufe und Anschreiben"),
            "bueroassistent": ("Clara", "Assistentin fuer Dokumente, Ablage und Schriftverkehr"),
            "data-analysis": ("Diana", "Expertin fuer Datenanalyse, Auswertungen und Statistiken"),
            "decision-briefing": ("Dietrich", "Experte fuer strukturierte Entscheidungsvorlagen und Briefings"),
            "finanz-assistent": ("Felix", "Assistent fuer Finanzen, Belege und Budgetuebersichten"),
            "foerderplaner": ("Florian", "Experte fuer Foerderberichte, Hilfebedarf und Paedagogik"),
            "haushaltsmanagement": ("Martha", "Expertin fuer Haushaltsorganisation, Vorraete und Routinen"),
            "ticket-master": ("Ticket-Master", "Triage- und Routing-Experte fuer die Zuweisung von Aufgaben an Rollen"),
            "task-divider": ("Task-Divider", "Experte fuer die vorab-Zerlegung komplexer Aufgaben in handhabbare Teilpakete"),
        }

        display, desc = PERSONA_MAP.get(clean, (clean.capitalize(), f"Experten-Rolle '{clean}'."))
        return (clean, display, desc)

    def _auto_commit_task(self, task_id: int, title: str) -> None:
        try:
            if not self.repo_dir.is_dir():
                return
            res = subprocess.run(
                ["git", "diff", "--name-only"],
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                timeout=10,
            )
            mod_files = [f.strip() for f in res.stdout.splitlines() if f.strip()]
            valid_files = [
                f
                for f in mod_files
                if not f.startswith("system/data/")
                and not f.endswith(".wal")
                and not f.endswith(".lock")
            ]
            if (
                os.environ.get("PYTEST_CURRENT_TEST")
                or "pytest" in sys.modules
                or task_id == 42
            ):
                return

            if not valid_files:
                return

            subprocess.run(
                ["git", "add"] + valid_files,
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
            )

            clean_title = title.replace('"', "").replace("'", "").strip()[:80]
            commit_msg = f"bach(buddha): #{task_id} {clean_title}"
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                timeout=15,
            )
        except Exception:
            pass

    def _settle_pending_task(self, app: TrayApp) -> bool:
        if not self.pending_task:
            return True

        if len(self.pending_task) >= 3:
            task_id, seit, title = self.pending_task[0], self.pending_task[1], self.pending_task[2]
        else:
            task_id, seit = self.pending_task[0], self.pending_task[1]
            title = f"Task #{task_id}"
        task_chat_id = f"idle-task-{task_id}"
        hist = app.client.get_history(task_chat_id)
        messages = (hist or {}).get("messages", [])
        answer = next((m for m in messages if m.get("role") == "assistant"), None)

        if answer is None:
            if not messages or (time.time() - seit >= self.PENDING_TTL):
                app.client.api_request(
                    "PUT",
                    f"/api/tasks/{task_id}",
                    {"status": "open", "changed_by": "idle-worker"},
                    base=app.client.gui_url,
                )
                self.pending_task = None
                return True
            return False

        ans_text = answer.get("content", "") if isinstance(answer, dict) else str(answer)
        hat_folgetask = any(k in ans_text.lower() for k in ("task #", "folge-task", "folgetask", "teilaufgaben"))
        ist_fertig = "FERTIG" in ans_text.upper() or hat_folgetask
        ist_unvollstaendig = "(Max Tool-Runden erreicht)" in ans_text or ("nicht im Code lösen" in ans_text and not hat_folgetask)

        task_now = app.client.api_request("GET", f"/api/tasks/{task_id}", base=app.client.gui_url)
        if task_now and task_now.get("completed_at"):
            self.pending_task = None
            return True

        if (ist_fertig or not ist_unvollstaendig) and answer.get("ok", True):
            status = "completed"
            self._auto_commit_task(task_id, title)
        else:
            status = "open"
        app.client.api_request(
            "PUT",
            f"/api/tasks/{task_id}",
            {"status": status, "changed_by": "idle-worker"},
            base=app.client.gui_url,
        )
        self.pending_task = None
        return True

    def _process_idle_task(self, app: TrayApp) -> None:
        if self.processing:
            return
        self.processing = True
        app.update_ui()

        try:
            if not self._settle_pending_task(app):
                return

            task = None
            task_status = "open"

            for assignee in ("OLLAMA", "BUDDHA", "BACH"):
                for status in ("pending", "open"):
                    tasks_resp = app.client.api_request(
                        "GET",
                        f"/api/tasks?assigned_to={assignee}&status={status}",
                        base=app.client.gui_url,
                    )
                    if tasks_resp and tasks_resp.get("success") and tasks_resp.get("tasks"):
                        task = tasks_resp["tasks"][0]
                        task_status = status
                        break
                if task:
                    break

            if not task:
                for status in ("pending", "open"):
                    tasks_resp = app.client.api_request(
                        "GET",
                        f"/api/tasks?status={status}",
                        base=app.client.gui_url,
                    )
                    if tasks_resp and tasks_resp.get("success") and tasks_resp.get("tasks"):
                        for cand in tasks_resp["tasks"]:
                            cand_assignee = (cand.get("assigned_to") or "").strip()
                            if cand_assignee.lower() not in ("user", "claude", "gemini", "operator", "blocked", ""):
                                task = cand
                                task_status = status
                                break
                    if task:
                        break

            if not task:
                return

            if task.get("completed_at"):
                tid = task.get("id")
                app.client.api_request(
                    "PUT",
                    f"/api/tasks/{tid}",
                    {"status": "done", "changed_by": "idle-worker"},
                    base=app.client.gui_url,
                )
                return

            task_id = task.get("id")
            title = task.get("title", "Unbenannt")
            desc = task.get("description", "")
            assignee = task.get("assigned_to", "bach")
            self.current_task_name = title

            role_id, role_display, role_desc = self._resolve_role(assignee)
            task_chat_id = f"idle-{role_id}-{task_id}"

            claim_resp = app.client.api_request(
                "PUT",
                f"/api/tasks/{task_id}",
                {"status": "in_progress", "changed_by": "idle-worker"},
                base=app.client.gui_url,
            )
            if not claim_resp or claim_resp.get("status") == "claim_failed":
                return

            prompt = (
                f"Du bearbeitest eine zugewiesene Aufgabe im vollen Ausfuehrungsmodus (Full-Mode mit Schreibrechten).\n\n"
                f"ROLLE & IDENTITAET: Du agierst in dieser Session in der Rolle: '{role_display}' ({role_id}).\n"
                f"Fachbereich / Profil: {role_desc}\n"
                f"Handle und antworte aus der fachlichen Perspektive dieser Rolle!\n\n"
                f"Task #{task_id}: {title}"
            )
            if desc:
                prompt += f"\nBeschreibung: {desc}"

            result = app.client.send_chat(prompt, chat_id=task_chat_id, mode="full", timeout=300)

            if result is None:
                self.pending_task = (task_id, time.time(), title)
            elif result.get("compute_locked"):
                app.client.api_request(
                    "PUT",
                    f"/api/tasks/{task_id}",
                    {"status": task_status, "changed_by": "idle-worker"},
                    base=app.client.gui_url,
                )
            elif result.get("ok"):
                ans = str(result.get("answer", ""))
                hat_folgetask = any(k in ans.lower() for k in ("task #", "folge-task", "folgetask", "teilaufgaben"))
                ist_fertig = "FERTIG" in ans.upper() or hat_folgetask
                ist_unvollstaendig = "(Max Tool-Runden erreicht)" in ans or ("nicht im Code lösen" in ans and not hat_folgetask)
                if ist_fertig or not ist_unvollstaendig:
                    app.client.api_request(
                        "PUT",
                        f"/api/tasks/{task_id}",
                        {"status": "completed", "changed_by": "idle-worker"},
                        base=app.client.gui_url,
                    )
                    self._auto_commit_task(task_id, title)
                    app.notify(f"Erledigt: {title}", f"{app.branding.notification_title} Idle")
                else:
                    app.client.api_request(
                        "PUT",
                        f"/api/tasks/{task_id}",
                        {"status": "open", "changed_by": "idle-worker"},
                        base=app.client.gui_url,
                    )
            else:
                app.client.api_request(
                    "PUT",
                    f"/api/tasks/{task_id}",
                    {"status": "open", "changed_by": "idle-worker"},
                    base=app.client.gui_url,
                )

        except Exception:
            pass
        finally:
            self.processing = False
            self.current_task_name = None
            self.consecutive_idle = 0
            app.update_ui()
