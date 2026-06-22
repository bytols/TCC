"""
Slice 5 — arduino.send_led(player_id, "WHITE") is called on successful vote submit.
Tests use patch("arduino.send_led") so no serial hardware is needed.
"""
import json
import pytest
from unittest.mock import patch
from app import create_app
from extensions import db as _db
import session_state
from models import Player, Session, RoundPool


@pytest.fixture()
def app():
    application = create_app({"TESTING": True})
    with application.app_context():
        _db.drop_all()
        _db.create_all()
        session_state.get_or_create_session()
        yield application
        _db.session.remove()
        _db.drop_all()


def _add_player(app, name="P1"):
    with app.app_context():
        sess = Session.query.first()
        p = Player(
            name=name,
            character_json=json.dumps({}),
            avatar_path="/static/img/avatars/test.png",
            session_id=sess.id,
        )
        _db.session.add(p)
        _db.session.commit()
        return p.id


def _set_state(app, state):
    with app.app_context():
        sess = Session.query.first()
        sess.state = state
        _db.session.commit()


def _client_for_player(app, player_id):
    c = app.test_client()
    c.set_cookie("player_id", str(player_id))
    return c


# ── Round 1 tracer bullet ──────────────────────────────────────────────────────

ROUND1_MOVIES = [
    "acao__die_hard",
    "acao__mad_max",
    "acao__john_wick",
    "acao__mission_fallout",
    "acao__speed",
]


def test_round1_submit_calls_send_led_white(app):
    pid = _add_player(app)
    _set_state(app, "ROUND_1")
    client = _client_for_player(app, pid)

    with patch("arduino.send_led") as mock_led:
        resp = client.post(
            "/round/1/submit",
            data={"movie_ids": ROUND1_MOVIES},
            follow_redirects=False,
        )

    assert resp.status_code == 302
    mock_led.assert_called_once_with(pid, "WHITE")


# ── Round 2 ───────────────────────────────────────────────────────────────────

ROUND2_MOVIES = ["acao__die_hard", "acao__mad_max", "acao__john_wick"]


def _seed_round_pool(app, round_number, movie_ids):
    with app.app_context():
        for mid in movie_ids:
            _db.session.add(RoundPool(
                round_number=round_number,
                movie_id=mid,
                movie_title=mid,
                category="acao",
            ))
        _db.session.commit()


def test_round2_submit_calls_send_led_white(app):
    pid = _add_player(app)
    _set_state(app, "ROUND_2")
    _seed_round_pool(app, 2, ROUND2_MOVIES)
    client = _client_for_player(app, pid)

    with patch("arduino.send_led") as mock_led:
        resp = client.post(
            "/round/2/submit",
            data={"movie_ids": ROUND2_MOVIES},
            follow_redirects=False,
        )

    assert resp.status_code == 302
    mock_led.assert_called_once_with(pid, "WHITE")


# ── Round 3 ───────────────────────────────────────────────────────────────────

ROUND3_MOVIES = ["acao__die_hard", "acao__mad_max", "acao__john_wick"]


def test_round3_submit_calls_send_led_white(app):
    pid = _add_player(app)
    _set_state(app, "ROUND_3")
    _seed_round_pool(app, 3, ROUND3_MOVIES)
    client = _client_for_player(app, pid)

    with patch("arduino.send_led") as mock_led:
        resp = client.post(
            "/round/3/submit",
            data={"movie_ids": ROUND3_MOVIES},
            follow_redirects=False,
        )

    assert resp.status_code == 302
    # WHITE is sent on submit; GREEN follows when advance_state() reaches FINAL.
    mock_led.assert_any_call(pid, "WHITE")


# ── Validation failure: send_led must NOT be called ───────────────────────────

def test_round1_submit_wrong_count_does_not_call_send_led(app):
    pid = _add_player(app)
    _set_state(app, "ROUND_1")
    client = _client_for_player(app, pid)

    with patch("arduino.send_led") as mock_led:
        resp = client.post(
            "/round/1/submit",
            data={"movie_ids": ROUND1_MOVIES[:3]},  # only 3 instead of 5
            follow_redirects=False,
        )

    assert resp.status_code == 400
    mock_led.assert_not_called()
