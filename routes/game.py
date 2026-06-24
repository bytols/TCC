import functools
import json
import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, make_response
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


def round_picks(round_number: int) -> int:
    """Quantidade de filmes a escolher na rodada.

    Rodada 1 explora o catálogo cheio (ROUND1_PICKS). Da rodada 2 em diante o
    pool afunila, e as escolhas afunilam JUNTO: sempre menos do que o tamanho do
    pool, para garantir que o pool continue encolhendo até o consenso. Mínimo 1.
    """
    if round_number <= 1:
        return config.ROUND1_PICKS
    pool_size = RoundPool.query.filter_by(round_number=round_number).count()
    return max(1, min(config.ROUND2_PICKS, pool_size - 1))


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


@game_bp.route("/heartbeat", methods=["POST"])
def heartbeat():
    """Sinal periódico do celular: mantém o jogador vivo para a varredura."""
    player = get_current_player()
    if player is None:
        return ("", 204)
    session_state.touch_player(player.id)
    return ("", 204)


@game_bp.route("/leave", methods=["POST"])
def leave():
    """Saída voluntária pelo botão "Sair": descarta a participação e limpa o cookie."""
    player = get_current_player()
    if player is not None:
        session_state.remove_player(player.id)
    resp = make_response(jsonify({"status": "left"}))
    resp.delete_cookie("player_id")
    return resp


@game_bp.route("/waiting")
@require_player
def waiting():
    session = session_state.get_or_create_session()
    player = get_current_player()
    state = session.state

    if state.startswith("ROUND_"):
        round_num = int(state.split("_")[1])
        if not already_voted(player.id, round_num):
            return redirect(url_for("game.round_view", n=round_num))
    elif state.startswith("SHOW_") or state == "FINAL":
        return redirect(url_for("game.results"))

    return render_template("mobile/waiting.html", player=player, state=state,
                           auto_start_seconds=config.AUTO_START_SECONDS)


def _render_round(player, n, *, error=None, status=200):
    """Renderiza a tela da rodada n. Rodada 1 = catálogo cheio + grade de
    gêneros; rodadas ≥2 = deck direto sobre o pool afunilado."""
    if n <= 1:
        movies = _filtered_movies(MOVIES)
        show_genres = True
    else:
        movies = pool_grouped(n)
        show_genres = False
    html = render_template("mobile/round.html", player=player, movies=movies,
                           picks_required=round_picks(n), round_num=n,
                           show_genres=show_genres, error=error)
    return (html, status) if status != 200 else html


@game_bp.route("/round/<int:n>")
@require_player
def round_view(n):
    session = session_state.get_session()
    if session is None or session.state != f"ROUND_{n}":
        return redirect(url_for("game.waiting"))

    player = get_current_player()
    if already_voted(player.id, n):
        return redirect(url_for("game.waiting"))

    return _render_round(player, n)


@game_bp.route("/round/<int:n>/submit", methods=["POST"])
@require_player
def round_submit(n):
    session = session_state.get_session()
    if session is None or session.state != f"ROUND_{n}":
        return redirect(url_for("game.waiting"))

    player = get_current_player()
    if already_voted(player.id, n):
        return redirect(url_for("game.waiting"))

    picks = round_picks(n)

    # Rodada 1 vota sobre o catálogo; rodadas ≥2 votam sobre o pool da anterior.
    if n <= 1:
        candidates = request.form.getlist("movie_ids")
        movie_ids = [mid for mid in candidates if mid in MOVIE_LOOKUP]
        meta_for = lambda mid: MOVIE_LOOKUP.get(mid)
        title_of = lambda m: m["title"]
        cat_of = lambda m: m["category"]
    else:
        pool = RoundPool.query.filter_by(round_number=n).all()
        pool_by_id = {p.movie_id: p for p in pool}
        movie_ids = [mid for mid in request.form.getlist("movie_ids") if mid in pool_by_id]
        meta_for = lambda mid: pool_by_id.get(mid)
        title_of = lambda m: m.movie_title
        cat_of = lambda m: m.category

    if len(movie_ids) != picks:
        return _render_round(player, n,
                             error=f"Selecione exatamente {picks} filmes", status=400)

    for movie_id in movie_ids:
        meta = meta_for(movie_id)
        if not meta:
            continue
        db.session.add(Vote(
            player_id=player.id,
            round_number=n,
            movie_id=movie_id,
            movie_title=title_of(meta),
            category=cat_of(meta),
        ))
    db.session.commit()
    arduino.send_led(player.id, "WHITE")

    if session_state.check_round_complete(n):
        session_state.advance_state()
    else:
        session_state.notify_progress(n)

    return redirect(url_for("game.waiting"))


@game_bp.route("/results")
@require_player
def results():
    session = session_state.get_session()
    if session is None:
        return redirect(url_for("join.join_page"))

    state = session.state
    player = get_current_player()

    if state.startswith("SHOW_"):
        round_num = int(state.split("_")[1])
    elif state == "FINAL":
        round_num = session.result_round or 1
    else:
        return redirect(url_for("game.waiting"))

    votes = session_state.get_round_votes(round_num)
    match_data = enrich_match_movies(calculate_match(votes, Player.query.count()))

    player_votes = [v for v in votes if v["player_id"] == player.id]

    return render_template("mobile/results.html",
                           player=player,
                           match_data=match_data,
                           player_votes=player_votes,
                           round_num=round_num,
                           is_final=(state == "FINAL"),
                           result_seconds=session.result_seconds,
                           state=state)
