"""
Pytest fixtures and environment configuration for ellmos-tray tests.
"""
from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_pystray(monkeypatch):
    """Mocks pystray module for headless test environments."""
    mock = MagicMock()

    class MockMenuItem:
        def __init__(self, text, action=None, checked=None, enabled=True, default=False):
            self.text = text
            self.action = action
            self.checked = checked
            self.enabled = enabled
            self.default = default

        def __repr__(self):
            return f"MockMenuItem({self.text!r})"

    class MockMenu:
        SEPARATOR = "SEPARATOR"

        def __init__(self, *items):
            self.items = list(items)

        def __iter__(self):
            return iter(self.items)

    class MockIcon:
        def __init__(self, name, icon=None, title=None, menu=None):
            self.name = name
            self.icon = icon
            self.title = title
            self.menu = menu
            self.visible = False
            self.notifications = []

        def run(self):
            self.visible = True

        def stop(self):
            self.visible = False

        def notify(self, message, title=None):
            self.notifications.append((message, title))

    mock.MenuItem = MockMenuItem
    mock.Menu = MockMenu
    mock.Icon = MockIcon

    monkeypatch.setitem(sys.modules, "pystray", mock)
    return mock
