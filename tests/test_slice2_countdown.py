"""Slice 2 — Countdown auto-start no desktop."""
import importlib
import os


# ── Cycle 1: AUTO_START_SECONDS in config ──────────────────────────────────

def test_auto_start_seconds_default():
    import config
    assert hasattr(config, "AUTO_START_SECONDS")
    assert config.AUTO_START_SECONDS == 30


def test_auto_start_seconds_from_env(monkeypatch):
    monkeypatch.setenv("AUTO_START_SECONDS", "45")
    import config
    importlib.reload(config)
    assert config.AUTO_START_SECONDS == 45
    # restore default for subsequent tests
    monkeypatch.delenv("AUTO_START_SECONDS", raising=False)
    importlib.reload(config)


# ── Cycle 2: template exposes AUTO_START_SECONDS as JS global ──────────────

def test_desktop_lobby_exposes_js_global(client):
    response = client.get("/desktop")
    assert response.status_code == 200
    body = response.data.decode()
    assert "AUTO_START_SECONDS" in body
    assert "30" in body


def test_desktop_lobby_js_global_contains_value(client, monkeypatch):
    """Value from config is embedded in the page."""
    monkeypatch.setenv("AUTO_START_SECONDS", "60")
    import config
    importlib.reload(config)
    response = client.get("/desktop")
    body = response.data.decode()
    assert "60" in body
    # restore
    monkeypatch.delenv("AUTO_START_SECONDS", raising=False)
    importlib.reload(config)


# ── Cycle 3: countdown JS is present in the lobby template ─────────────────

def test_desktop_lobby_includes_countdown_container(client):
    """The lobby HTML includes a countdown display element."""
    response = client.get("/desktop")
    body = response.data.decode()
    assert 'id="countdown-display"' in body


def test_desktop_js_has_countdown_logic():
    """desktop.js contains the countdown auto-start implementation."""
    path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "desktop.js")
    with open(path) as f:
        js = f.read()
    assert "countdown" in js.lower()
    assert "AUTO_START_SECONDS" in js
    assert "admin/start" in js
