"""
Unit tests for MenuBuilder and menu signature generation.
"""
from ellmos_tray.app import TrayApp
from ellmos_tray.branding import TrayBranding
from ellmos_tray.menu import MenuBuilder


def test_build_menu_disconnected(mock_pystray):
    app = TrayApp(branding=TrayBranding.ellmos())
    app.state["connected"] = False

    builder = MenuBuilder(app)
    menu = builder.build_menu()

    item_texts = [item.text for item in menu.items if hasattr(item, "text")]
    assert any("Nicht verbunden" in t for t in item_texts)
    assert any("Services" in t for t in item_texts)
    assert any("Beenden" in t for t in item_texts)


def test_build_menu_connected(mock_pystray):
    app = TrayApp(branding=TrayBranding.bach())
    app.state["connected"] = True
    app.state["mode"] = "full"
    app.state["think"] = True
    app.models = ["qwen3.8:27b-mlx", "llama3.3:70b"]
    app.slots = {
        "buddha_chat": {"model": "qwen3.8:27b-mlx", "backend": "ollama", "mode": "safe"},
    }
    app.dynamic_workers = [
        {"id": "w1", "name": "Reviewer", "status": "idle", "model": "qwen3.8:27b-mlx"},
    ]

    builder = MenuBuilder(app)
    menu = builder.build_menu()

    item_texts = [item.text for item in menu.items if hasattr(item, "text")]
    assert any("Modus: FULL | Denken: AN" in t for t in item_texts)
    assert any("Deine Agenten (Modell-Bindung & Claim)" in t for t in item_texts)
    assert any("Buddha Chat" in t for t in item_texts)
    assert any("Hintergrundagenten" in t for t in item_texts)
    assert any("RAM-Distributor (Fackelpriorität:" in t for t in item_texts)
    assert any("BACH öffnen" in t for t in item_texts)
    assert any("Agenten · Running und Verlauf" in t for t in item_texts)
    assert not any("/activity" in t or "Aktivitätsanzeige" in t for t in item_texts)


def test_menu_signature_reacts_to_changes(mock_pystray):
    app = TrayApp(branding=TrayBranding.ellmos())
    sig1 = app.menu_signature()

    app.state["connected"] = True
    sig2 = app.menu_signature()
    assert sig1 != sig2

    app.state["mode"] = "full"
    sig3 = app.menu_signature()
    assert sig2 != sig3

    # Identical state produces identical signature
    assert app.menu_signature() == sig3


def test_permissions_sub_flyout_and_talk_link(mock_pystray):
    app = TrayApp(branding=TrayBranding.bach())
    builder = MenuBuilder(app)
    menu = builder.build_menu()
    item_texts = [item.text for item in menu.items if hasattr(item, "text")]
    assert any("Berechtigungen (Permissions)" in t for t in item_texts)
    assert any("ELLMOS Talk" in t for t in item_texts)
    sig_before = app.menu_signature()
    app.permissions["camera"] = True
    assert app.menu_signature() != sig_before
