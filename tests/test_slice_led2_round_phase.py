"""
Slice LED 2 — round_phase WebSocket event syncs TV color with LED timer.

Behaviors under test:
  1. advance_state() LOBBY→ROUND_x emits round_phase {color: BLUE}
  2. _round_timer_task emits round_phase {color: PINK} at first sleep boundary
  3. _round_timer_task emits round_phase {color: ORANGE} at second sleep boundary
  4. advance_state() reaching FINAL emits round_phase {color: GREEN}
  5. round_phase events fire even when all players have already submitted
     (TV always gets the phase update; LED filtering is separate)
"""
import pytest
from unittest.mock import patch, call
from extensions import db, socketio
from models import Session, Player, Vote
from session_state import advance_state, _round_timer_task


def _add_vote(app, player_id, round_number, movie_id="m1"):
    with app.app_context():
        db.session.add(Vote(
            player_id=player_id,
            round_number=round_number,
            movie_id=movie_id,
            movie_title="Movie",
            category="acao",
        ))
        db.session.commit()


def _phase_calls(mock_emit):
    """Return only the round_phase emit calls."""
    return [c for c in mock_emit.call_args_list if c.args[0] == "round_phase"]


# ---------------------------------------------------------------------------
# Cycle 1 — entering any ROUND_x emits round_phase BLUE
# ---------------------------------------------------------------------------

def test_advance_to_round1_emits_blue_phase(app, add_player):
    add_player("P1")
    add_player("P2")
    with patch("arduino.send_led"), \
         patch.object(socketio, "start_background_task"), \
         patch.object(socketio, "emit") as mock_emit:
        advance_state()
    phases = _phase_calls(mock_emit)
    assert len(phases) == 1, "exactly one round_phase on ROUND_1 entry"
    assert phases[0].args[1] == {"color": "BLUE"}


# ---------------------------------------------------------------------------
# Cycle 2 — _round_timer_task emits round_phase PINK at first sleep boundary
# ---------------------------------------------------------------------------

def test_timer_task_emits_pink_phase(app, add_player):
    add_player("P1")
    add_player("P2")
    s = Session.query.first()
    s.state = "ROUND_1"
    s.timer_gen = 1
    db.session.commit()
    with patch("arduino.send_led"), \
         patch("eventlet.sleep"), \
         patch.object(socketio, "emit") as mock_emit:
        _round_timer_task(app, 1, gen=1)
    phases = _phase_calls(mock_emit)
    assert any(c.args[1] == {"color": "PINK"} for c in phases), \
        "round_phase PINK must be emitted after first sleep"


# ---------------------------------------------------------------------------
# Cycle 3 — _round_timer_task emits round_phase ORANGE at second sleep boundary
# ---------------------------------------------------------------------------

def test_timer_task_emits_orange_phase(app, add_player):
    add_player("P1")
    add_player("P2")
    s = Session.query.first()
    s.state = "ROUND_1"
    s.timer_gen = 1
    db.session.commit()
    with patch("arduino.send_led"), \
         patch("eventlet.sleep"), \
         patch.object(socketio, "emit") as mock_emit:
        _round_timer_task(app, 1, gen=1)
    phases = _phase_calls(mock_emit)
    assert any(c.args[1] == {"color": "ORANGE"} for c in phases), \
        "round_phase ORANGE must be emitted after second sleep"


# ---------------------------------------------------------------------------
# Cycle 4 — reaching FINAL (early match) emits round_phase GREEN
# ---------------------------------------------------------------------------

def test_advance_to_final_via_early_match_emits_green_phase(app):
    s = Session.query.first()
    s.state = "ROUND_1"
    db.session.flush()
    p1 = Player(name="Alice", character_json="{}", avatar_path="/a.png", session_id=s.id)
    p2 = Player(name="Bob", character_json="{}", avatar_path="/b.png", session_id=s.id)
    db.session.add_all([p1, p2])
    db.session.flush()
    # Both vote for same movie → match → FINAL
    for pid in (p1.id, p2.id):
        db.session.add(Vote(player_id=pid, round_number=1, movie_id="same",
                            movie_title="Same", category="acao"))
    db.session.commit()

    with patch("arduino.send_led"), \
         patch.object(socketio, "emit") as mock_emit:
        result = advance_state()

    assert result == "FINAL"
    phases = _phase_calls(mock_emit)
    assert any(c.args[1] == {"color": "GREEN"} for c in phases), \
        "round_phase GREEN must be emitted when reaching FINAL via early match"


# ---------------------------------------------------------------------------
# Cycle 5 — round_phase is still broadcast even when all players submitted
#            (TV always gets the color; LED filtering for non-submitted is separate)
# ---------------------------------------------------------------------------

def test_timer_emits_phases_even_when_all_submitted(app, add_player):
    p1_id = add_player("P1")
    p2_id = add_player("P2")
    _add_vote(app, p1_id, 1)
    _add_vote(app, p2_id, 1)
    s = Session.query.first()
    s.state = "ROUND_1"
    s.timer_gen = 1
    db.session.commit()

    with patch("arduino.send_led") as mock_led, \
         patch("eventlet.sleep"), \
         patch.object(socketio, "emit") as mock_emit:
        _round_timer_task(app, 1, gen=1)

    assert mock_led.call_count == 0, "no LED when all players already submitted"
    phases = _phase_calls(mock_emit)
    assert any(c.args[1] == {"color": "PINK"} for c in phases), \
        "round_phase PINK must still reach TV even when all submitted"
    assert any(c.args[1] == {"color": "ORANGE"} for c in phases), \
        "round_phase ORANGE must still reach TV even when all submitted"
