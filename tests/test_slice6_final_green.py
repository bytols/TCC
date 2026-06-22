import json
import pytest
from unittest.mock import patch
from extensions import db
from models import Session, Player, Vote


def _add_player(session_id, name="P"):
    p = Player(
        name=name,
        character_json=json.dumps({}),
        avatar_path="/static/img/avatars/test.png",
        session_id=session_id,
    )
    db.session.add(p)
    db.session.flush()
    return p


def _add_vote(player_id, round_number, movie_id="m1"):
    db.session.add(Vote(
        player_id=player_id,
        round_number=round_number,
        movie_id=movie_id,
        movie_title="Movie",
        category="acao",
    ))
    db.session.flush()


def test_early_match_sends_green_to_all_players(app):
    """Early match in any round → advance_state() sends GREEN to every active player."""
    s = Session.query.first()
    s.state = "ROUND_1"
    db.session.flush()
    p1 = _add_player(s.id, "Alice")
    p2 = _add_player(s.id, "Bob")
    _add_vote(p1.id, 1, "same_movie")
    _add_vote(p2.id, 1, "same_movie")
    db.session.commit()

    import session_state
    with patch("arduino.send_led") as mock_send:
        result = session_state.advance_state()

    assert result == "FINAL"
    calls = {call.args for call in mock_send.call_args_list}
    assert (p1.id, "GREEN") in calls
    assert (p2.id, "GREEN") in calls


def test_normal_round3_to_final_sends_green(app):
    """Normal ROUND_3 → FINAL (no match) also sends GREEN to all players."""
    s = Session.query.first()
    s.state = "ROUND_3"
    db.session.flush()
    p1 = _add_player(s.id, "Alice")
    p2 = _add_player(s.id, "Bob")
    _add_vote(p1.id, 3, "movie_a")
    _add_vote(p2.id, 3, "movie_b")
    db.session.commit()

    import session_state
    with patch("arduino.send_led") as mock_send:
        result = session_state.advance_state()

    assert result == "FINAL"
    calls = {call.args for call in mock_send.call_args_list}
    assert (p1.id, "GREEN") in calls
    assert (p2.id, "GREEN") in calls


def test_clear_session_sends_white_to_all_players(app):
    """clear_session() sends WHITE to every active player before wiping the DB."""
    s = Session.query.first()
    p1 = _add_player(s.id, "Alice")
    p2 = _add_player(s.id, "Bob")
    db.session.commit()
    p1_id, p2_id = p1.id, p2.id

    import session_state
    with patch("arduino.send_led") as mock_send:
        session_state.clear_session()

    calls = {call.args for call in mock_send.call_args_list}
    assert (p1_id, "WHITE") in calls
    assert (p2_id, "WHITE") in calls


def test_no_players_no_led_calls_on_final(app):
    """If no players exist, no LED commands are sent when reaching FINAL."""
    s = Session.query.first()
    s.state = "ROUND_3"
    db.session.commit()

    import session_state
    with patch("arduino.send_led") as mock_send:
        session_state.advance_state()

    mock_send.assert_not_called()
