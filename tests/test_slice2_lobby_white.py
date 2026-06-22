"""
Slice 2 — Presença no lobby: WHITE ao entrar.

Verifica o comportamento público observável:
- POST /join bem-sucedido → arduino.send_led(player_id, "WHITE") chamado
- POST /join com dados inválidos → send_led NÃO chamado
- POST /join com lobby cheio → send_led NÃO chamado
- create_app() → arduino.init() chamado
"""

from unittest.mock import patch

_JOIN_DATA = {
    "name": "TestPlayer",
    "rosto": "1",
    "cabelo": "1",
    "pele": "1",
    "cor_cabelo": "1",
    "acessorio": "none",
    "fundo": "1",
}


# ── Tracer bullet ─────────────────────────────────────────────────────────────

def test_successful_join_calls_send_led_white(app, client):
    with patch("arduino.send_led") as mock_send:
        resp = client.post("/join", data=_JOIN_DATA, follow_redirects=False)
    assert resp.status_code == 302
    mock_send.assert_called_once()
    args = mock_send.call_args[0]
    assert isinstance(args[0], int), "primeiro argumento deve ser o player_id (int)"
    assert args[1] == "WHITE"


# ── Falhas de validação não disparam LED ──────────────────────────────────────

def test_invalid_name_does_not_call_send_led(app, client):
    with patch("arduino.send_led") as mock_send:
        resp = client.post("/join", data={**_JOIN_DATA, "name": ""})
    assert resp.status_code == 400
    mock_send.assert_not_called()


def test_full_lobby_does_not_call_send_led(app, client, add_player):
    for i in range(4):
        add_player(name=f"P{i + 1}")
    with patch("arduino.send_led") as mock_send:
        resp = client.post("/join", data=_JOIN_DATA)
    assert resp.status_code == 403
    mock_send.assert_not_called()


# ── arduino.init() chamado no startup da aplicação ────────────────────────────

def test_arduino_init_called_on_create_app():
    from app import create_app
    with patch("arduino.init") as mock_init:
        create_app({"TESTING": True})
    mock_init.assert_called_once()
