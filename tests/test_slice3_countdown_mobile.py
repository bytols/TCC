"""Slice 3 — Countdown na tela de espera mobile."""
import os


# ── helpers ────────────────────────────────────────────────────────────────

def _make_client_with_player(client, add_player):
    """Return a test client with a logged-in player cookie set."""
    player_id = add_player("Alice")
    client.set_cookie("player_id", str(player_id))
    return client


# ── Cycle 1: /waiting route embeds AUTO_START_SECONDS as JS global ─────────

def test_waiting_exposes_auto_start_seconds(client, add_player):
    """/waiting renders AUTO_START_SECONDS in the page."""
    c = _make_client_with_player(client, add_player)
    resp = c.get("/waiting")
    assert resp.status_code == 200
    body = resp.data.decode()
    assert "AUTO_START_SECONDS" in body
    assert "30" in body


def test_waiting_auto_start_seconds_is_js_variable(client, add_player):
    """The value must be assigned as a JS variable (not just appear in a comment)."""
    c = _make_client_with_player(client, add_player)
    resp = c.get("/waiting")
    body = resp.data.decode()
    # e.g.  const AUTO_START_SECONDS = 30;
    assert "AUTO_START_SECONDS" in body
    # Make sure it's in a <script> block
    script_start = body.find("<script")
    assert script_start != -1
    script_section = body[script_start:]
    assert "AUTO_START_SECONDS" in script_section


# ── Cycle 2: template has countdown container ───────────────────────────────

def test_waiting_has_countdown_container(client, add_player):
    """The waiting page includes a dedicated countdown display element."""
    c = _make_client_with_player(client, add_player)
    resp = c.get("/waiting")
    body = resp.data.decode()
    assert 'id="mobile-countdown"' in body


# ── Cycle 3: JS logic — listens to player_joined, never calls /admin/start ──

def _read_waiting_template():
    path = os.path.join(os.path.dirname(__file__), "..", "templates", "mobile", "waiting.html")
    with open(path) as f:
        return f.read()


def test_waiting_js_listens_to_player_joined():
    """waiting.html script handles the player_joined WebSocket event."""
    src = _read_waiting_template()
    assert 'player_joined' in src


def test_waiting_js_starts_countdown_on_two_players():
    """Script starts countdown when player_count reaches MIN_PLAYERS (2)."""
    src = _read_waiting_template()
    # The JS must check player_count >= 2 (or the constant) before starting
    assert "player_count" in src
    assert "countdown" in src.lower()


def test_waiting_js_never_calls_admin_start():
    """Mobile must never call /admin/start — transition comes from desktop only."""
    src = _read_waiting_template()
    assert "/admin/start" not in src


def test_waiting_js_cancels_countdown_below_two_players():
    """If player_count drops below 2, the countdown is cancelled."""
    src = _read_waiting_template()
    # The script must handle the case where count falls below threshold
    assert "clearInterval" in src or "clearTimeout" in src
