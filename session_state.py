from datetime import datetime
from sqlalchemy import func, distinct
from extensions import db, socketio
from models import Session, Player, Vote, RoundPool
from match import calculate_match

VALID_TRANSITIONS = {
    "LOBBY":   "ROUND_1",
    "ROUND_1": "SHOW_1",
    "SHOW_1":  "ROUND_2",
    "ROUND_2": "SHOW_2",
    "SHOW_2":  "ROUND_3",
    "ROUND_3": "FINAL",
}


def get_session() -> Session | None:
    return Session.query.first()


def get_or_create_session() -> Session:
    session = Session.query.first()
    if session is None:
        session = Session(state="LOBBY")
        db.session.add(session)
        db.session.commit()
    return session


def _players_payload() -> list[dict]:
    return [
        {"id": p.id, "name": p.name, "avatar_path": p.avatar_path}
        for p in Player.query.all()
    ]


def _emit_state(state: str) -> None:
    players = _players_payload()
    socketio.emit("state_change", {
        "state": state,
        "player_count": len(players),
        "players": players,
    }, room="game_room")


def has_match(round_number: int) -> bool:
    """True if any movie in the round was chosen by >= 2 players."""
    return calculate_match(get_round_votes(round_number))["matched_count"] > 0


def advance_state() -> str | None:
    session = get_session()
    if session is None:
        return None
    cur = session.state
    next_state = VALID_TRANSITIONS.get(cur)
    if next_state is None:
        return cur

    # Start the experience timer when the game begins (drives time-based colors).
    if cur == "LOBBY":
        session.started_at = datetime.utcnow()

    # A round just finished — if there's a match, end immediately (consensus).
    if cur in ("ROUND_1", "ROUND_2", "ROUND_3"):
        from_round = int(cur[-1])
        if has_match(from_round):
            session.state = "FINAL"
            session.result_round = from_round
            db.session.commit()
            _emit_state("FINAL")
            return "FINAL"
        # No match yet → prepare the next round's pool (if any).
        if from_round < 3:
            build_round_pool(from_round)

    if next_state == "FINAL":
        session.result_round = 3

    session.state = next_state
    db.session.commit()
    _emit_state(next_state)
    return next_state


def elapsed_seconds() -> int:
    """Seconds since the game started (used for time-based desktop colors)."""
    session = get_session()
    if session is None or session.started_at is None:
        return 0
    return max(0, int((datetime.utcnow() - session.started_at).total_seconds()))


def count_submitted(round_number: int) -> int:
    return (
        db.session.query(func.count(distinct(Vote.player_id)))
        .filter(Vote.round_number == round_number)
        .scalar()
    ) or 0


def check_round_complete(round_number: int) -> bool:
    player_count = Player.query.count()
    if player_count == 0:
        return False
    return count_submitted(round_number) >= player_count


def submitted_player_ids(round_number: int) -> list[int]:
    rows = (
        db.session.query(distinct(Vote.player_id))
        .filter(Vote.round_number == round_number)
        .all()
    )
    return [r[0] for r in rows]


def notify_progress(round_number: int) -> None:
    """Emit collective progress so the TV updates without a state change."""
    socketio.emit("progress", {
        "round": round_number,
        "submitted": count_submitted(round_number),
        "total": Player.query.count(),
        "submitted_ids": submitted_player_ids(round_number),
    }, room="game_room")


def build_round_pool(from_round: int) -> None:
    next_round = from_round + 1
    RoundPool.query.filter_by(round_number=next_round).delete()

    votes = (
        db.session.query(Vote)
        .filter(Vote.round_number == from_round)
        .all()
    )
    seen: dict[str, Vote] = {}
    for v in votes:
        if v.movie_id not in seen:
            seen[v.movie_id] = v

    for v in seen.values():
        db.session.add(RoundPool(
            round_number=next_round,
            movie_id=v.movie_id,
            movie_title=v.movie_title,
            category=v.category,
        ))
    db.session.commit()


def get_round_votes(round_number: int) -> list[dict]:
    rows = (
        db.session.query(Vote, Player.name)
        .join(Player, Vote.player_id == Player.id)
        .filter(Vote.round_number == round_number)
        .all()
    )
    return [
        {
            "player_id": v.player_id,
            "player_name": name,
            "movie_id": v.movie_id,
            "movie_title": v.movie_title,
            "category": v.category,
        }
        for v, name in rows
    ]


def clear_session() -> None:
    import os
    import glob

    avatar_pattern = os.path.join(
        os.path.dirname(__file__), "static", "img", "avatars", "*.png"
    )
    for f in glob.glob(avatar_pattern):
        try:
            os.remove(f)
        except OSError:
            pass

    db.drop_all()
    db.create_all()

    import qr as qr_module
    qr_module.reset_cache()

    socketio.emit("session_ended", {}, room="game_room")
