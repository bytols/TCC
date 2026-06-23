"""
Slice LED 3 — Guard de geração: LED concluído permanece branco.

Behaviors under test:
  1. Session.timer_gen starts at 0
  2. advance_state() to ROUND_x increments timer_gen
  3. _round_timer_task with stale generation does NOT send LED or emit round_phase
  4. _round_timer_task with stale state (not ROUND_x) does NOT send LED or emit round_phase
  5. Bug scenario: last player's WHITE is not overridden by a stale timer phase
"""
import pytest
from unittest.mock import patch, call
from extensions import db, socketio
from models import Session, Player, Vote
from session_state import advance_state, _round_timer_task


# ---------------------------------------------------------------------------
# Cycle 1 — Session.timer_gen starts at 0
# ---------------------------------------------------------------------------

def test_session_timer_gen_starts_at_zero(app):
    s = Session.query.first()
    assert s.timer_gen == 0


# ---------------------------------------------------------------------------
# Cycle 2 — advance_state() to ROUND_x increments timer_gen
# ---------------------------------------------------------------------------

def test_advance_to_round1_increments_timer_gen(app, add_player):
    add_player("P1")
    add_player("P2")
    s = Session.query.first()
    assert s.timer_gen == 0

    with patch("arduino.send_led"), \
         patch.object(socketio, "start_background_task"), \
         patch.object(socketio, "emit"):
        advance_state()

    s = Session.query.first()
    assert s.timer_gen == 1


def test_each_round_entry_increments_timer_gen(app, add_player):
    add_player("P1")
    add_player("P2")

    with patch("arduino.send_led"), \
         patch.object(socketio, "start_background_task"), \
         patch.object(socketio, "emit"):
        advance_state()  # LOBBY → ROUND_1

    s = Session.query.first()
    assert s.timer_gen == 1

    # Manually advance to SHOW_1, then ROUND_2 to check gen increments again
    s.state = "SHOW_1"
    db.session.commit()

    with patch("arduino.send_led"), \
         patch.object(socketio, "start_background_task"), \
         patch.object(socketio, "emit"):
        advance_state()  # SHOW_1 → ROUND_2

    s = Session.query.first()
    assert s.timer_gen == 2


# ---------------------------------------------------------------------------
# Cycle 3 — stale generation: timer task does NOT send LED or emit round_phase
# ---------------------------------------------------------------------------

def test_stale_gen_timer_does_not_send_led(app, add_player):
    add_player("P1")
    add_player("P2")
    with app.app_context():
        s = Session.query.first()
        s.state = "ROUND_1"
        s.timer_gen = 2  # current gen
        db.session.commit()

    with patch("arduino.send_led") as mock_led, \
         patch("eventlet.sleep"), \
         patch.object(socketio, "emit") as mock_emit:
        _round_timer_task(app, 1, gen=1)  # gen=1 is stale

    mock_led.assert_not_called()


def test_stale_gen_timer_does_not_emit_round_phase(app, add_player):
    add_player("P1")
    add_player("P2")
    with app.app_context():
        s = Session.query.first()
        s.state = "ROUND_1"
        s.timer_gen = 2
        db.session.commit()

    with patch("arduino.send_led"), \
         patch("eventlet.sleep"), \
         patch.object(socketio, "emit") as mock_emit:
        _round_timer_task(app, 1, gen=1)

    phase_calls = [c for c in mock_emit.call_args_list if c.args[0] == "round_phase"]
    assert phase_calls == [], "stale gen must not emit round_phase"


# ---------------------------------------------------------------------------
# Cycle 4 — stale state: timer task does NOT send LED or emit round_phase
# ---------------------------------------------------------------------------

def test_stale_state_final_timer_does_not_send_led(app, add_player):
    add_player("P1")
    add_player("P2")
    with app.app_context():
        s = Session.query.first()
        s.state = "FINAL"   # round already ended
        s.timer_gen = 1
        db.session.commit()

    with patch("arduino.send_led") as mock_led, \
         patch("eventlet.sleep"), \
         patch.object(socketio, "emit") as mock_emit:
        _round_timer_task(app, 1, gen=1)  # same gen but state is FINAL

    mock_led.assert_not_called()


def test_stale_state_show_timer_does_not_emit_round_phase(app, add_player):
    add_player("P1")
    add_player("P2")
    with app.app_context():
        s = Session.query.first()
        s.state = "SHOW_1"  # round finished, now in show phase
        s.timer_gen = 1
        db.session.commit()

    with patch("arduino.send_led"), \
         patch("eventlet.sleep"), \
         patch.object(socketio, "emit") as mock_emit:
        _round_timer_task(app, 1, gen=1)

    phase_calls = [c for c in mock_emit.call_args_list if c.args[0] == "round_phase"]
    assert phase_calls == [], "stale state (SHOW_1) must not emit round_phase"


# ---------------------------------------------------------------------------
# Cycle 5 — bug scenario: last player's WHITE is NOT overridden by stale timer
# ---------------------------------------------------------------------------

def test_submitted_player_white_not_overridden_by_stale_timer(app, add_player):
    """
    The bug: last player submits → WHITE; a stale timer phase fires → PINK/ORANGE.
    With the guard, the stale task must send nothing to any player.
    """
    p1_id = add_player("P1")
    p2_id = add_player("P2")

    # Simulate: round ended (state advanced, timer_gen bumped to 2).
    # The old background task (gen=1) is still sleeping.
    with app.app_context():
        s = Session.query.first()
        s.state = "SHOW_1"   # round ended
        s.timer_gen = 2      # gen bumped when ROUND_2 would start
        db.session.commit()

    led_calls = []
    with patch("arduino.send_led", side_effect=lambda pid, color: led_calls.append((pid, color))), \
         patch("eventlet.sleep"), \
         patch.object(socketio, "emit"):
        _round_timer_task(app, 1, gen=1)  # stale task from the finished round

    overrides = [(pid, color) for pid, color in led_calls if color in ("PINK", "ORANGE")]
    assert overrides == [], (
        "stale timer must not send PINK/ORANGE to any player — "
        f"got: {overrides}"
    )
