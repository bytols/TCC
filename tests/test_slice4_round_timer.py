import pytest
from unittest.mock import patch, call
from extensions import db, socketio
from models import Session, Player, Vote
from session_state import advance_state, _round_timer_task


# ---------------------------------------------------------------------------
# Cycle 1 — advance_state starts a background task for each ROUND_X
# ---------------------------------------------------------------------------

def test_advance_to_round1_starts_background_task(app, add_player):
    add_player("P1")
    add_player("P2")
    with patch("arduino.send_led"), \
         patch.object(socketio, "start_background_task") as mock_task:
        advance_state()
    mock_task.assert_called_once()
    args = mock_task.call_args[0]
    assert args[0] is _round_timer_task
    assert args[2] == 1  # round_number


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _add_vote(app, player_id, round_number):
    with app.app_context():
        db.session.add(Vote(
            player_id=player_id,
            round_number=round_number,
            movie_id="m1",
            movie_title="Movie 1",
            category="acao",
        ))
        db.session.commit()


# ---------------------------------------------------------------------------
# Cycle 2 — PINK only to non-submitted after first sleep
# ---------------------------------------------------------------------------

def test_timer_sends_pink_only_to_non_submitted(app, add_player):
    p1_id = add_player("P1")
    p2_id = add_player("P2")
    _add_vote(app, p1_id, 1)  # P1 already submitted round 1

    with patch("arduino.send_led") as mock_led, \
         patch("eventlet.sleep"):
        _round_timer_task(app, 1)

    pink_calls = [c for c in mock_led.call_args_list if c == call(p2_id, "PINK")]
    no_pink_p1 = all(c != call(p1_id, "PINK") for c in mock_led.call_args_list)
    assert len(pink_calls) == 1, "PINK should be sent exactly once to non-submitted player"
    assert no_pink_p1, "P1 (submitted) should NOT receive PINK"


# ---------------------------------------------------------------------------
# Cycle 3 — ORANGE only to non-submitted after second sleep
# ---------------------------------------------------------------------------

def test_timer_sends_orange_only_to_non_submitted(app, add_player):
    p1_id = add_player("P1")
    p2_id = add_player("P2")
    _add_vote(app, p1_id, 1)  # P1 submitted before ORANGE fires

    with patch("arduino.send_led") as mock_led, \
         patch("eventlet.sleep"):
        _round_timer_task(app, 1)

    orange_calls = [c for c in mock_led.call_args_list if c == call(p2_id, "ORANGE")]
    no_orange_p1 = all(c != call(p1_id, "ORANGE") for c in mock_led.call_args_list)
    assert len(orange_calls) == 1, "ORANGE should be sent exactly once to non-submitted player"
    assert no_orange_p1, "P1 (submitted) should NOT receive ORANGE"


# ---------------------------------------------------------------------------
# Cycle 4 — no command sent if all players already submitted
# ---------------------------------------------------------------------------

def test_timer_sends_nothing_when_all_submitted(app, add_player):
    p1_id = add_player("P1")
    p2_id = add_player("P2")
    _add_vote(app, p1_id, 1)
    _add_vote(app, p2_id, 1)  # both submitted

    with patch("arduino.send_led") as mock_led, \
         patch("eventlet.sleep"):
        _round_timer_task(app, 1)

    assert mock_led.call_count == 0, "No LED command should be sent when all submitted"


# ---------------------------------------------------------------------------
# Cycle 5 — ROUND_2 and ROUND_3 also start the background timer
# ---------------------------------------------------------------------------

def test_advance_to_round2_starts_background_task(app, add_player):
    add_player("P1")
    add_player("P2")
    session = Session.query.first()
    session.state = "SHOW_1"
    db.session.commit()

    with patch("arduino.send_led"), \
         patch.object(socketio, "start_background_task") as mock_task:
        advance_state()

    mock_task.assert_called_once()
    args = mock_task.call_args[0]
    assert args[0] is _round_timer_task
    assert args[2] == 2  # round_number


def test_advance_to_round3_starts_background_task(app, add_player):
    add_player("P1")
    add_player("P2")
    session = Session.query.first()
    session.state = "SHOW_2"
    db.session.commit()

    with patch("arduino.send_led"), \
         patch.object(socketio, "start_background_task") as mock_task:
        advance_state()

    mock_task.assert_called_once()
    args = mock_task.call_args[0]
    assert args[0] is _round_timer_task
    assert args[2] == 3  # round_number
