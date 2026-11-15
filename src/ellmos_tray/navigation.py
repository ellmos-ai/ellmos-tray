"""Shared GUI destinations for all tray brands; Control API URLs stay separate."""
from __future__ import annotations

from urllib.parse import urlsplit

GUI_DESTINATIONS = (
    ("💬 Chat", "/chat"),
    ("🎙️ ELLMOS Talk (Live-Stimme)", "/talk"),
    ("📋 Aufgaben", "/tasks"),
    ("⚡ Agenten · Running und Verlauf", "/agenten/running"),
    ("📚 Agenten-Bibliothek · Vorlagen", "/agenten/blueprints"),
    ("📥 Posteingang", "/inbox"),
    ("🔁 Routinen", "/routinen"),
    ("⚙️ Einstellungen", "/settings"),
    ("🗂️ Sitzungen", "/agenten/sessions"),
    ("📖 Hilfe & Claim-Doku", "/help?topic=claiming"),
)


def _has_control_chars(value: str) -> bool:
    return any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in value)


def is_safe_http_url(value: str) -> bool:
    """Return True only for well-formed http/https URLs without ASCII control characters."""
    if not isinstance(value, str) or _has_control_chars(value):
        return False
    clean = value.strip()
    if not clean:
        return False
    parts = urlsplit(clean)
    return parts.scheme.lower() in {"http", "https"} and bool(parts.hostname)


def normalize_gui_url(value: str) -> str:
    """Keep the configured GUI host and base path without trailing slashes."""
    if _has_control_chars(value):
        raise ValueError("GUI-Adresse darf keine Steuerzeichen enthalten.")
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
