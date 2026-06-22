"""
Tests for player count limit enforcement on the join routes.
All assertions are against observable HTTP behavior (status codes, response content).
"""

_JOIN_DATA = {
    "name": "Player5",
    "rosto": "1",
    "cabelo": "1",
    "pele": "1",
    "cor_cabelo": "1",
    "acessorio": "none",
    "fundo": "1",
}


def _fill_lobby(add_player, count):
    for i in range(count):
        add_player(name=f"Player{i + 1}")


# ── Tracer bullet ──────────────────────────────────────────────────────────────

def test_post_join_returns_403_when_lobby_is_full(app, client, add_player):
    _fill_lobby(add_player, 4)
    resp = client.post("/join", data=_JOIN_DATA)
    assert resp.status_code == 403


# ── GET /join at capacity ──────────────────────────────────────────────────────

def test_get_join_shows_full_page_when_lobby_is_full(app, client, add_player):
    _fill_lobby(add_player, 4)
    resp = client.get("/join")
    assert resp.status_code == 200
    assert b"SESS\xc3\x83O LOTADA" in resp.data


# ── Happy path: 4th player can still join ─────────────────────────────────────

def test_fourth_player_can_join_normally(app, client, add_player):
    _fill_lobby(add_player, 3)
    resp = client.post(
        "/join",
        data={**_JOIN_DATA, "name": "Player4"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/waiting" in resp.headers.get("Location", "")
