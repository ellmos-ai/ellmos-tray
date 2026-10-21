"""Shared GUI destinations for all tray brands; Control API URLs stay separate."""
from __future__ import annotations

from urllib.parse import urlsplit


GUI_DESTINATIONS = (
    ("Chat", "/chat"),
    ("Aufgaben", "/tasks"),
    ("Agenten · Running und Verlauf", "/agenten/running"),
    ("Werkstatt · Vorlagen", "/agenten/blueprints"),
    ("Posteingang", "/inbox"),
    ("Routinen", "/routinen"),
    ("Einstellungen", "/settings"),
    ("Sitzungen", "/agenten/sessions"),
)


def normalize_gui_url(value: str) -> str:
    """Keep the configured GUI host and base path without trailing slashes."""
    value = value.strip().rstrip("/")
    parts = urlsplit(value)
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        raise ValueError("GUI-Adresse muss eine vollständige HTTP(S)-Adresse sein.")
    if parts.query or parts.fragment:
        raise ValueError("GUI-Basisadresse darf keine Suchparameter oder Sprungmarke enthalten.")
    return value


def gui_destinations(gui_url: str) -> tuple[tuple[str, str], ...]:
    base = normalize_gui_url(gui_url)
    return tuple((label, base + path) for label, path in GUI_DESTINATIONS)
