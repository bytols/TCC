import pytest
from unittest.mock import patch
from models import Session, Player
from extensions import db
from session_state import advance_state


def test_session_has_round_started_at_none_by_default(app):
    session = Session.query.first()
    assert session.round_started_at is None


def test_advance_to_round1_sets_round_started_at(app, add_player):
    add_player("P1")
    add_player("P2")
    with patch("arduino.send_led"):
        advance_state()
    session = Session.query.first()
    assert session.round_started_at is not None


def test_advance_to_round1_sends_blue_to_all_active_players(app, add_player):
    p1_id = add_player("P1")
    p2_id = add_player("P2")
    with patch("arduino.send_led") as mock_led:
        advance_state()
    assert mock_led.call_count == 2
    mock_led.assert_any_call(p1_id, "BLUE")
    mock_led.assert_any_call(p2_id, "BLUE")


def test_advance_to_round1_with_no_players_does_not_call_send_led(app):
    with patch("arduino.send_led") as mock_led:
        advance_state()
    mock_led.assert_not_called()


def test_advance_to_round2_sets_round_started_at_and_sends_blue(app, add_player):
    p1_id = add_player("P1")
    p2_id = add_player("P2")
    session = Session.query.first()
    session.state = "SHOW_1"
    db.session.commit()
    with patch("arduino.send_led") as mock_led:
        advance_state()
    refreshed = Session.query.first()
    assert refreshed.round_started_at is not None
    assert mock_led.call_count == 2
    mock_led.assert_any_call(p1_id, "BLUE")
    mock_led.assert_any_call(p2_id, "BLUE")


def test_advance_to_round3_sets_round_started_at_and_sends_blue(app, add_player):
    p1_id = add_player("P1")
    p2_id = add_player("P2")
    session = Session.query.first()
    session.state = "SHOW_2"
    db.session.commit()
    with patch("arduino.send_led") as mock_led:
        advance_state()
    refreshed = Session.query.first()
    assert refreshed.round_started_at is not None
    assert mock_led.call_count == 2
    mock_led.assert_any_call(p1_id, "BLUE")
    mock_led.assert_any_call(p2_id, "BLUE")
