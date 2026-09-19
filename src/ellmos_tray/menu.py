"""
Menu builder for ellmos-tray.
Constructs dynamic pystray menus reflecting status, model slots, dynamic workers, services, and prompts.
"""
from __future__ import annotations

import webbrowser
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    import pystray
    from ellmos_tray.app import TrayApp


class MenuBuilder:
    """Builds and updates the desktop system tray context menu."""

    def __init__(self, app: TrayApp):
        self.app = app

    def build_menu(self) -> pystray.Menu:
        import pystray

        items: list[Any] = []
        branding = self.app.branding
        state = self.app.state

        # ── 1. Status & Slots ──
        if state.get("connected"):
            mode_str = (state.get("mode") or "safe").upper()
            think_str = "AN" if state.get("think") else "AUS"
            items.append(pystray.MenuItem(
                f"Modus: {mode_str} | Denken: {think_str}", None, enabled=False
            ))
            items.append(pystray.Menu.SEPARATOR)

            # Slots configuration
            self._append_slots(items)

            # Dynamic workers
            self._append_dynamic_workers(items)

            items.append(pystray.Menu.SEPARATOR)

            # Fackel / Resource allocation
            self._append_fackel(items)

            # Activity monitor link
            items.append(pystray.MenuItem(
                f"📊 {branding.activity_label} öffnen...",
                lambda *_: webbrowser.open(f"{self.app.client.base_url}/activity"),
            ))

            # Tool activity
            ct = state.get("current_tool", "")
            lt = state.get("last_tools", [])
            if ct:
                items.append(pystray.MenuItem(
                    f"Tool: {ct} (Runde {state.get('tool_round', 0)})", None, enabled=False
                ))
            elif lt:
                items.append(pystray.MenuItem(
                    f"Letzte Tools: {', '.join(lt)}", None, enabled=False
                ))
        else:
            items.append(pystray.MenuItem("Nicht verbunden", None, enabled=False))
            items.append(pystray.MenuItem(f"Versuche: {self.app.client.base_url}", None, enabled=False))

        items.append(pystray.Menu.SEPARATOR)

        # ── 2. Services ──
        self._append_services(items)

        # ── 3. PromptBoard / Prompts ──
        self._append_prompts(items)

        items.append(pystray.Menu.SEPARATOR)

        # ── 4. Idle / Worker status ──
        self._append_idle_worker(items)

        items.append(pystray.Menu.SEPARATOR)

        # ── 5. Quick links ──
        items.append(pystray.MenuItem(
            branding.gui_label,
            lambda *_: webbrowser.open(self.app.client.gui_url),
        ))
        items.append(pystray.MenuItem(
            branding.chat_label,
            lambda *_: webbrowser.open(f"{self.app.client.gui_url}/chat"),
        ))
        items.append(pystray.MenuItem(
            branding.activity_label,
            lambda *_: webbrowser.open(f"{self.app.client.base_url}/activity"),
        ))
        items.append(pystray.MenuItem(
            branding.messenger_label,
            lambda *_: webbrowser.open(self.app.client.telegram_url),
        ))

        items.append(pystray.Menu.SEPARATOR)
        items.append(pystray.MenuItem("Beenden", lambda *_: self.app.stop()))

        return pystray.Menu(*items)

    def _append_slots(self, items: list[Any]) -> None:
        import pystray

        branding = self.app.branding
        slots = self.app.slots
        models = self.app.models
        backends = self.app.backends

        # Chat Slot
        chat_slot = slots.get("buddha_chat", {})
        chat_label = branding.slot_labels.get("buddha_chat", "💬 Chat")
        chat_model = chat_slot.get("model") or self.app.state.get("model", "?")
        chat_backend = chat_slot.get("backend") or "ollama"
        chat_rounds = chat_slot.get("max_tool_rounds", 12)
        chat_mode = chat_slot.get("mode", "safe")
        chat_think = chat_slot.get("think", True)

        chat_subitems: list[Any] = []
        if models:
            chat_model_items = [
                pystray.MenuItem(
                    m,
                    self._make_slot_action("buddha_chat", {"model": m}),
                    checked=lambda item, m=m, s=chat_model: m == s,
                )
                for m in models[:15]
            ]
            chat_subitems.append(pystray.MenuItem(f"Modell: {chat_model}", pystray.Menu(*chat_model_items)))

        chat_backend_items = [
            pystray.MenuItem(
                name.capitalize(),
                self._make_slot_action("buddha_chat", {"backend": name}),
                checked=lambda item, n=name, b=chat_backend: n.lower() == b.lower(),
            )
            for name in backends.keys()
        ]
        if chat_backend_items:
            chat_subitems.append(pystray.MenuItem(f"Backend: {chat_backend}", pystray.Menu(*chat_backend_items)))

        chat_round_items = [
            pystray.MenuItem(
                "Unbegrenzt" if v == 0 else f"{v} Turns",
                self._make_slot_action("buddha_chat", {"max_tool_rounds": v}),
                checked=lambda item, v=v, cr=chat_rounds: cr == v,
            )
            for v in [5, 10, 12, 15, 20, 0]
        ]
        chat_subitems.append(pystray.MenuItem(
            f"Max Turns: {'Unbegrenzt' if chat_rounds == 0 else chat_rounds}",
            pystray.Menu(*chat_round_items),
        ))
        chat_subitems.append(pystray.MenuItem(
            "Safe-Modus",
            self._make_slot_action("buddha_chat", {"mode": "safe"}),
            checked=lambda item, cm=chat_mode: cm == "safe",
        ))
        chat_subitems.append(pystray.MenuItem(
            "Full-Modus",
            self._make_slot_action("buddha_chat", {"mode": "full"}),
            checked=lambda item, cm=chat_mode: cm == "full",
        ))
        chat_subitems.append(pystray.MenuItem(
            "Denkmodus",
            lambda *_: self._toggle_slot_think("buddha_chat"),
            checked=lambda item, ct=chat_think: ct,
        ))
        items.append(pystray.MenuItem(f"{chat_label}: {chat_model}", pystray.Menu(*chat_subitems)))

        # Always-On Slot
        always_slot = slots.get("buddha_always_on", {})
        always_label = branding.slot_labels.get("buddha_always_on", "⚡ Always-On")
        always_model = always_slot.get("model") or "qwen3.8:27b-mlx"
        always_backend = always_slot.get("backend") or "ollama"
        always_rounds = always_slot.get("max_tool_rounds", 25)
        always_mode = always_slot.get("mode", "full")
        always_enabled = always_slot.get("enabled", True) and self.app.runner.is_enabled
        always_status_str = "Aktiv" if always_enabled else "Pausiert"

        always_subitems: list[Any] = []
        always_subitems.append(pystray.MenuItem(
            "Always-On aktivieren",
            lambda *_: self._toggle_slot_enabled("buddha_always_on"),
            checked=lambda item, en=always_enabled: en,
        ))
        if models:
            always_model_items = [
                pystray.MenuItem(
                    m,
                    self._make_slot_action("buddha_always_on", {"model": m}),
                    checked=lambda item, m=m, s=always_model: m == s,
                )
                for m in models[:15]
            ]
            always_subitems.append(pystray.MenuItem(f"Modell: {always_model}", pystray.Menu(*always_model_items)))

        always_backend_items = [
            pystray.MenuItem(
                name.capitalize(),
                self._make_slot_action("buddha_always_on", {"backend": name}),
                checked=lambda item, n=name, b=always_backend: n.lower() == b.lower(),
            )
            for name in backends.keys()
        ]
        if always_backend_items:
            always_subitems.append(pystray.MenuItem(f"Backend: {always_backend}", pystray.Menu(*always_backend_items)))

        always_round_items = [
            pystray.MenuItem(
                "Unbegrenzt" if v == 0 else f"{v} Turns",
                self._make_slot_action("buddha_always_on", {"max_tool_rounds": v}),
                checked=lambda item, v=v, ar=always_rounds: ar == v,
            )
            for v in [10, 20, 25, 30, 50, 0]
        ]
        always_subitems.append(pystray.MenuItem(
            f"Max Turns: {'Unbegrenzt' if always_rounds == 0 else always_rounds}",
            pystray.Menu(*always_round_items),
        ))
        always_subitems.append(pystray.MenuItem(
            "Full-Modus (Schreibrechte)",
            self._make_slot_action("buddha_always_on", {"mode": "full"}),
            checked=lambda item, am=always_mode: am == "full",
        ))
        always_subitems.append(pystray.MenuItem(
            "Safe-Modus",
            self._make_slot_action("buddha_always_on", {"mode": "safe"}),
            checked=lambda item, am=always_mode: am == "safe",
        ))
        act_text = (
            self.app.runner.get_current_task_name()
            or always_slot.get("current_activity")
            or "Wartet auf Leerlauf"
        )
        always_subitems.append(pystray.MenuItem(f"Aktivität: {act_text[:35]}", None, enabled=False))
        items.append(pystray.MenuItem(
            f"{always_label} [{always_status_str}]: {always_model}",
            pystray.Menu(*always_subitems),
        ))

        # Connector Slot
        conn_slot = slots.get("buddha_connector", {})
        conn_label = branding.slot_labels.get("buddha_connector", "📱 Connector")
        conn_model = conn_slot.get("model") or "qwen3.8:27b-mlx"
        conn_backend = conn_slot.get("backend") or "ollama"
        conn_rounds = conn_slot.get("max_tool_rounds", 10)

        conn_subitems: list[Any] = []
        if models:
            conn_model_items = [
                pystray.MenuItem(
                    m,
                    self._make_slot_action("buddha_connector", {"model": m}),
                    checked=lambda item, m=m, s=conn_model: m == s,
                )
                for m in models[:15]
            ]
            conn_subitems.append(pystray.MenuItem(f"Modell: {conn_model}", pystray.Menu(*conn_model_items)))

        conn_backend_items = [
            pystray.MenuItem(
                name.capitalize(),
                self._make_slot_action("buddha_connector", {"backend": name}),
                checked=lambda item, n=name, b=conn_backend: n.lower() == b.lower(),
            )
            for name in backends.keys()
        ]
        if conn_backend_items:
            conn_subitems.append(pystray.MenuItem(f"Backend: {conn_backend}", pystray.Menu(*conn_backend_items)))

        conn_round_items = [
            pystray.MenuItem(
                f"{v} Turns",
                self._make_slot_action("buddha_connector", {"max_tool_rounds": v}),
                checked=lambda item, v=v, cr=conn_rounds: cr == v,
            )
            for v in [5, 10, 15, 20]
        ]
        conn_subitems.append(pystray.MenuItem(f"Max Turns: {conn_rounds}", pystray.Menu(*conn_round_items)))
        conn_subitems.append(pystray.MenuItem(
            f"{branding.messenger_label} öffnen",
            lambda *_: webbrowser.open(self.app.client.telegram_url),
        ))
        items.append(pystray.MenuItem(f"{conn_label}: {conn_model}", pystray.Menu(*conn_subitems)))

    def _append_dynamic_workers(self, items: list[Any]) -> None:
        import pystray

        workers_subitems: list[Any] = []
        for w in self.app.dynamic_workers:
            wid = w.get("id", "worker")
            wname = w.get("name", wid)
            wstatus = w.get("status", "idle")
            wmodel = w.get("model", "?")
            wturns = w.get("max_tool_rounds", 20)
            wact = w.get("current_activity", "Bereit")
            wrole = w.get("role", "General")

            start_item = (
                pystray.MenuItem("⏳ Läuft...", None, enabled=False)
                if wstatus == "running"
                else pystray.MenuItem("▶ Starten", self._run_worker_action(wid))
            )

            w_actions = [
                pystray.MenuItem(f"Rolle: {wrole} | {wturns} Turns", None, enabled=False),
                pystray.MenuItem(f"Aktivität: {wact[:35]}", None, enabled=False),
                start_item,
                pystray.MenuItem(
                    "▶ Fortsetzen" if wstatus == "paused" else "⏸ Pausieren",
                    self._toggle_worker_action(wid, wstatus),
                ),
                pystray.MenuItem("🗑 Worker löschen", self._delete_worker_action(wid)),
            ]
            workers_subitems.append(pystray.MenuItem(f"{wname} [{wstatus}] ({wmodel})", pystray.Menu(*w_actions)))

        if workers_subitems:
            workers_subitems.append(pystray.Menu.SEPARATOR)
        workers_subitems.append(pystray.MenuItem(
            "+ Neuer Worker... (Web GUI)",
            lambda *_: webbrowser.open(f"{self.app.client.base_url}/activity"),
        ))
        items.append(pystray.MenuItem(
            f"🛠 Dynamische Worker ({len(self.app.dynamic_workers)})",
            pystray.Menu(*workers_subitems),
        ))

    def _append_fackel(self, items: list[Any]) -> None:
        import pystray

        current_fackel = self.app.state.get("fackel_preference", "compute")
        fackel_label = "Fackel: Ollama" if current_fackel == "ollama" else "Fackel: Rechenjobs"
        fackel_items = [
            pystray.MenuItem(
                "Ollama / Chat & Worker bevorzugen",
                lambda *_: self._set_fackel("ollama"),
                checked=lambda item: self.app.state.get("fackel_preference", "compute") == "ollama",
            ),
            pystray.MenuItem(
                "Rechenjobs bevorzugen (Compute)",
                lambda *_: self._set_fackel("compute"),
                checked=lambda item: self.app.state.get("fackel_preference", "compute") == "compute",
            ),
        ]
        items.append(pystray.MenuItem(fackel_label, pystray.Menu(*fackel_items)))

    def _append_services(self, items: list[Any]) -> None:
        import pystray

        svc_items: list[Any] = []
        for key, label in self.app.branding.service_labels.items():
            status_icon = "✅" if self.app.services.get(key) else "❌"
            svc_items.append(pystray.MenuItem(f"{status_icon} {label}", None, enabled=False))
        items.append(pystray.MenuItem("Services", pystray.Menu(*svc_items)))

    def _append_prompts(self, items: list[Any]) -> None:
        import pystray

        prompt_items: list[Any] = []
        app_path = self.app.prompt_manager.find_app_path()
        if app_path:
            prompt_items.append(pystray.MenuItem(
                "PromptBoard App öffnen",
                lambda *_: self.app.open_promptboard(),
            ))
            prompt_items.append(pystray.Menu.SEPARATOR)

        for category, prompts in self.app.prompt_manager.prompts.items():
            cat_items: list[Any] = []
            for name, text in prompts.items():
                cat_items.append(pystray.MenuItem(
                    f"📋 {name}",
                    self._make_prompt_copy_action(text),
                ))
                cat_items.append(pystray.MenuItem(
                    f"▶ Senden: {name}",
                    self._make_prompt_send_action(text),
                ))
            prompt_items.append(pystray.MenuItem(category, pystray.Menu(*cat_items)))

        if prompt_items:
            items.append(pystray.MenuItem("PromptBoard", pystray.Menu(*prompt_items)))

    def _append_idle_worker(self, items: list[Any]) -> None:
        import pystray

        is_proc = self.app.runner.is_processing()
        is_en = self.app.runner.is_enabled
        task_name = self.app.runner.get_current_task_name()

        idle_label = "Idle-Modus"
        if is_proc:
            idle_label += f": {task_name or 'Arbeitet...'}"
        elif is_en:
            idle_label += ": Bereit"
        else:
            idle_label += ": AUS"

        idle_items = [
            pystray.MenuItem(
                "Idle-Modus aktivieren",
                lambda *_: self.app.toggle_idle(),
                checked=lambda item: self.app.runner.is_enabled,
            ),
        ]
        if is_proc:
            idle_items.append(pystray.MenuItem(f"Bearbeitet: {task_name or '?'}", None, enabled=False))
        idle_items.append(pystray.MenuItem(
            f"Schwelle: {12 * self.app.poll_interval}s Leerlauf", None, enabled=False
        ))
        items.append(pystray.MenuItem(idle_label, pystray.Menu(*idle_items)))

    def _make_slot_action(self, slot_id: str, updates: dict[str, Any]) -> Callable[..., None]:
        def action(*_):
            res = self.app.client.update_slot(slot_id, updates)
            if res is None or res.get("error"):
                self.app.notify(f"{slot_id} Update fehlgeschlagen", self.app.branding.notification_title)
            self.app.refresh()
            self.app.update_ui()
        return action

    def _toggle_slot_think(self, slot_id: str) -> None:
        slot = self.app.slots.get(slot_id, {})
        new_think = not slot.get("think", True)
        self.app.client.update_slot(slot_id, {"think": new_think})
        self.app.refresh()
        self.app.update_ui()

    def _toggle_slot_enabled(self, slot_id: str) -> None:
        slot = self.app.slots.get(slot_id, {})
        new_enabled = not slot.get("enabled", True)
        self.app.client.update_slot(slot_id, {"enabled": new_enabled})
        self.app.refresh()
        self.app.update_ui()

    def _set_fackel(self, pref: str) -> None:
        result = self.app.client.set_fackel(pref)
        if result is None:
            self.app.notify(f"Fackel → {pref} fehlgeschlagen", self.app.branding.notification_title)
        else:
            self.app.state["fackel_preference"] = pref
            label = "Ollama (Chat & Worker)" if pref == "ollama" else "Rechenjobs (Compute)"
            self.app.notify(f"Fackel: {label} bevorzugt", self.app.branding.notification_title)
        self.app.refresh()
        self.app.update_ui()

    def _run_worker_action(self, worker_id: str) -> Callable[..., None]:
        def action(*_):
            res = self.app.client.run_worker(worker_id)
            if res is None or res.get("error"):
                self.app.notify(f"Worker {worker_id} Start fehlgeschlagen", self.app.branding.notification_title)
            else:
                self.app.notify(f"Worker {worker_id} gestartet", self.app.branding.notification_title)
            self.app.refresh()
            self.app.update_ui()
        return action

    def _toggle_worker_action(self, worker_id: str, current_status: str) -> Callable[..., None]:
        def action(*_):
            new_status = "idle" if current_status == "paused" else "paused"
            self.app.client.toggle_worker(worker_id, new_status)
            self.app.refresh()
            self.app.update_ui()
        return action

    def _delete_worker_action(self, worker_id: str) -> Callable[..., None]:
        def action(*_):
            self.app.client.delete_worker(worker_id)
            self.app.notify(f"Worker {worker_id} gelöscht", self.app.branding.notification_title)
            self.app.refresh()
            self.app.update_ui()
        return action

    def _make_prompt_copy_action(self, text: str) -> Callable[..., None]:
        def action(*_):
            if self.app.prompt_manager.copy_to_clipboard(text):
                self.app.notify("In Zwischenablage kopiert", f"{self.app.branding.notification_title} Prompt")
        return action

    def _make_prompt_send_action(self, text: str) -> Callable[..., None]:
        def action(*_):
            import threading
            threading.Thread(target=self._send_prompt_async, args=(text,), daemon=True).start()
        return action

    def _send_prompt_async(self, prompt: str) -> None:
        result = self.app.client.send_chat(prompt, chat_id="tray-prompt", timeout=300)
        answer = (result or {}).get("answer", "")[:120]
        if result and result.get("ok"):
            self.app.notify(answer, f"{self.app.branding.notification_title} Antwort")
        else:
            self.app.notify(answer or "Senden fehlgeschlagen", f"{self.app.branding.notification_title} Fehler")
