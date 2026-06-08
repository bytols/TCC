import functools
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from extensions import db
from models import Player, Vote, RoundPool
import session_state
from data.movies import MOVIES, MOVIE_LOOKUP
from match import calculate_match
import config

game_bp = Blueprint("game", __name__)


def get_current_player() -> Player | None:
    from flask import request
    player_id = request.cookies.get("player_id")
    if player_id and player_id.isdigit():
        return Player.query.get(int(player_id))
    return None


def require_player(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if get_current_player() is None:
            return redirect(url_for("join.join_page"))
        return f(*args, **kwargs)
    return decorated


def already_voted(player_id: int, round_number: int) -> bool:
    return Vote.query.filter_by(player_id=player_id, round_number=round_number).first() is not None


@game_bp.route("/waiting")
@require_player
def waiting():
    session = session_state.get_or_create_session()
    player = get_current_player()
    state = session.state

    redirect_map = {
        "ROUND_1": "game.round1",
        "SHOW_1":  "game.results",
        "ROUND_2": "game.round2",
        "SHOW_2":  "game.results",
        "ROUND_3": "game.round3",
        "FINAL":   "game.results",
    }

    if state in redirect_map:
        if state.startswith("ROUND_"):
            round_num = int(state[-1])
            if not already_voted(player.id, round_num):
                return redirect(url_for(redirect_map[state]))
        elif state.startswith("SHOW_") or state == "FINAL":
            return redirect(url_for(redirect_map[state]))

    return render_template("mobile/waiting.html", player=player, state=state)


@game_bp.route("/round/1")
@require_player
def round1():
    session = session_state.get_session()
    if session is None or session.state != "ROUND_1":
        return redirect(url_for("game.waiting"))

    player = get_current_player()
    if already_voted(player.id, 1):
        return redirect(url_for("game.waiting"))

    return render_template("mobile/round1.html", player=player, movies=MOVIES,
                           picks_required=config.ROUND1_PICKS)


@game_bp.route("/round/1/submit", methods=["POST"])
@require_player
def round1_submit():
    session = session_state.get_session()
    if session is None or session.state != "ROUND_1":
        return redirect(url_for("game.waiting"))

    player = get_current_player()
    if already_voted(player.id, 1):
        return redirect(url_for("game.waiting"))

    movie_ids = request.form.getlist("movie_ids")
    if len(movie_ids) != config.ROUND1_PICKS:
        return render_template("mobile/round1.html", player=player, movies=MOVIES,
                               picks_required=config.ROUND1_PICKS,
                               error=f"Selecione exatamente {config.ROUND1_PICKS} filmes"), 400

    for movie_id in movie_ids:
        data = MOVIE_LOOKUP.get(movie_id)
        if not data:
            continue
        db.session.add(Vote(
            player_id=player.id,
            round_number=1,
            movie_id=movie_id,
            movie_title=data["title"],
            category=data["category"],
        ))
    db.session.commit()

    if session_state.check_round_complete(1):
        session_state.advance_state()

    return redirect(url_for("game.waiting"))


@game_bp.route("/round/2")
@require_player
def round2():
    session = session_state.get_session()
    if session is None or session.state != "ROUND_2":
        return redirect(url_for("game.waiting"))

    player = get_current_player()
    if already_voted(player.id, 2):
        return redirect(url_for("game.waiting"))

    pool = RoundPool.query.filter_by(round_number=2).all()
    return render_template("mobile/round2.html", player=player, pool=pool,
                           picks_required=config.ROUND2_PICKS)


@game_bp.route("/round/2/submit", methods=["POST"])
@require_player
def round2_submit():
    session = session_state.get_session()
    if session is None or session.state != "ROUND_2":
        return redirect(url_for("game.waiting"))

    player = get_current_player()
    if already_voted(player.id, 2):
        return redirect(url_for("game.waiting"))

    pool = RoundPool.query.filter_by(round_number=2).all()
    pool_ids = {p.movie_id for p in pool}

    movie_ids = [mid for mid in request.form.getlist("movie_ids") if mid in pool_ids]
    if len(movie_ids) != config.ROUND2_PICKS:
        return render_template("mobile/round2.html", player=player, pool=pool,
                               picks_required=config.ROUND2_PICKS,
                               error=f"Selecione exatamente {config.ROUND2_PICKS} filmes"), 400

    for movie_id in movie_ids:
        entry = next((p for p in pool if p.movie_id == movie_id), None)
        if not entry:
            continue
        db.session.add(Vote(
            player_id=player.id,
            round_number=2,
            movie_id=movie_id,
            movie_title=entry.movie_title,
            category=entry.category,
        ))
    db.session.commit()

    if session_state.check_round_complete(2):
        session_state.advance_state()

    return redirect(url_for("game.waiting"))


@game_bp.route("/round/3")
@require_player
def round3():
    session = session_state.get_session()
    if session is None or session.state != "ROUND_3":
        return redirect(url_for("game.waiting"))

    player = get_current_player()
    if already_voted(player.id, 3):
        return redirect(url_for("game.waiting"))

    pool = RoundPool.query.filter_by(round_number=3).all()
    return render_template("mobile/round3.html", player=player, pool=pool,
                           picks_required=config.ROUND3_PICKS)


@game_bp.route("/round/3/submit", methods=["POST"])
@require_player
def round3_submit():
    session = session_state.get_session()
    if session is None or session.state != "ROUND_3":
        return redirect(url_for("game.waiting"))

    player = get_current_player()
    if already_voted(player.id, 3):
        return redirect(url_for("game.waiting"))

    pool = RoundPool.query.filter_by(round_number=3).all()
    pool_ids = {p.movie_id for p in pool}

    movie_ids = [mid for mid in request.form.getlist("movie_ids") if mid in pool_ids]
    if len(movie_ids) != config.ROUND3_PICKS:
        return render_template("mobile/round3.html", player=player, pool=pool,
                               picks_required=config.ROUND3_PICKS,
                               error=f"Selecione exatamente {config.ROUND3_PICKS} filmes"), 400

    for movie_id in movie_ids:
        entry = next((p for p in pool if p.movie_id == movie_id), None)
        if not entry:
            continue
        db.session.add(Vote(
            player_id=player.id,
            round_number=3,
            movie_id=movie_id,
            movie_title=entry.movie_title,
            category=entry.category,
        ))
    db.session.commit()

    if session_state.check_round_complete(3):
        session_state.advance_state()

    return redirect(url_for("game.waiting"))


@game_bp.route("/results")
@require_player
def results():
    session = session_state.get_session()
    if session is None:
        return redirect(url_for("join.join_page"))

    state = session.state
    player = get_current_player()

    if state == "SHOW_1":
        round_num = 1
    elif state == "SHOW_2":
        round_num = 2
    elif state == "FINAL":
        round_num = 3
    else:
        return redirect(url_for("game.waiting"))

    votes = session_state.get_round_votes(round_num)
    match_data = calculate_match(votes)

    player_votes = [v for v in votes if v["player_id"] == player.id]

    return render_template("mobile/results.html",
                           player=player,
                           match_data=match_data,
                           player_votes=player_votes,
                           round_num=round_num,
                           is_final=(state == "FINAL"),
                           state=state)
