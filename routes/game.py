import functools
import json
import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from extensions import db
from models import Player, Vote, RoundPool
import session_state
from data.movies import MOVIES, MOVIE_LOOKUP
from match import calculate_match
import config
import arduino

_MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "posters.json")


def _load_manifest() -> dict:
    try:
        with open(_MANIFEST_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


_manifest: dict = _load_manifest()


def _filtered_movies(movies: dict) -> dict:
    """Return MOVIES filtered to only ids in _manifest, with 'poster' injected."""
    result = {}
    for cat_key, cat in movies.items():
        filtered = [
            {**m, "poster": _manifest[m["id"]]["file"]}
            for m in cat.get("movies", [])
            if m["id"] in _manifest
        ]
        if filtered:
            result[cat_key] = {**cat, "movies": filtered}
    return result


def enrich_match_movies(match_data: dict) -> dict:
    """Add the local poster path and catalog year to each movie in a match result.

    The results/final screens render real posters; `calculate_match` stays pure
    (vote-only) so the manifest lookup lives here, next to the manifest itself.
    Missing posters simply leave `poster` unset — the gradient placeholder covers it.
    """
    for movie in match_data.get("movies", []):
        mid = movie["movie_id"]
        if mid in _manifest:
            movie["poster"] = _manifest[mid]["file"]
        meta = MOVIE_LOOKUP.get(mid, {})
        if meta.get("year"):
            movie["year"] = meta["year"]
        if meta.get("category_label"):
            movie["category_label"] = meta["category_label"]
    return match_data

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


def pool_grouped(round_number: int) -> dict:
    """Build a MOVIES-shaped dict from a round's pool so rounds 2/3 can reuse the
    same genre-grouped carousel component as round 1 (enriched with year/color)."""
    pool = RoundPool.query.filter_by(round_number=round_number).all()
    groups: dict = {}
    for item in pool:
        meta = MOVIE_LOOKUP.get(item.movie_id, {})
        g = groups.setdefault(item.category, {
            "label": meta.get("category_label", item.category.upper()),
            "color": meta.get("category_color", "#888888"),
            "movies": [],
        })
        entry: dict = {
            "id": item.movie_id,
            "title": item.movie_title,
            "year": meta.get("year", ""),
        }
        if item.movie_id in _manifest:
            entry["poster"] = _manifest[item.movie_id]["file"]
        g["movies"].append(entry)
    return groups


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

    return render_template("mobile/waiting.html", player=player, state=state,
                           auto_start_seconds=config.AUTO_START_SECONDS)


@game_bp.route("/round/1")
@require_player
def round1():
    session = session_state.get_session()
    if session is None or session.state != "ROUND_1":
        return redirect(url_for("game.waiting"))

    player = get_current_player()
    if already_voted(player.id, 1):
        return redirect(url_for("game.waiting"))

    return render_template("mobile/round1.html", player=player,
                           movies=_filtered_movies(MOVIES),
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
        return render_template("mobile/round1.html", player=player,
                               movies=_filtered_movies(MOVIES),
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
    arduino.send_led(player.id, "WHITE")

    if session_state.check_round_complete(1):
        session_state.advance_state()
    else:
        session_state.notify_progress(1)

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

    return render_template("mobile/round2.html", player=player,
                           movies=pool_grouped(2), picks_required=config.ROUND2_PICKS)


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
    arduino.send_led(player.id, "WHITE")

    if session_state.check_round_complete(2):
        session_state.advance_state()
    else:
        session_state.notify_progress(2)

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

    return render_template("mobile/round3.html", player=player,
                           movies=pool_grouped(3), picks_required=config.ROUND3_PICKS)


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
    arduino.send_led(player.id, "WHITE")

    if session_state.check_round_complete(3):
        session_state.advance_state()
    else:
        session_state.notify_progress(3)

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
        round_num = session.result_round or 3
    else:
        return redirect(url_for("game.waiting"))

    votes = session_state.get_round_votes(round_num)
    match_data = enrich_match_movies(calculate_match(votes))

    player_votes = [v for v in votes if v["player_id"] == player.id]

    return render_template("mobile/results.html",
                           player=player,
                           match_data=match_data,
                           player_votes=player_votes,
                           round_num=round_num,
                           is_final=(state == "FINAL"),
                           result_seconds=session.result_seconds,
                           state=state)
