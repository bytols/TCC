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


def advance_state() -> str | None:
    session = get_session()
    if session is None:
        return None
    next_state = VALID_TRANSITIONS.get(session.state)
    if next_state is None:
        return session.state

    if next_state in ("SHOW_1", "SHOW_2", "FINAL"):
        from_round = {"SHOW_1": 1, "SHOW_2": 2, "FINAL": 3}[next_state]
        build_round_pool(from_round)

    session.state = next_state
    db.session.commit()

    players = _players_payload()
    socketio.emit("state_change", {
        "state": next_state,
        "player_count": len(players),
        "players": players,
    }, room="game_room")

    return next_state


def check_round_complete(round_number: int) -> bool:
    player_count = Player.query.count()
    if player_count == 0:
        return False
    submitted = (
        db.session.query(func.count(distinct(Vote.player_id)))
        .filter(Vote.round_number == round_number)
        .scalar()
    )
    return submitted >= player_count


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
