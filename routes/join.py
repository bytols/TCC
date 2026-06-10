import json
from flask import Blueprint, render_template, request, redirect, url_for, make_response
from extensions import db, socketio
from models import Player
import session_state
from data.character_options import CHAR_OPTIONS, CHAR_DEFAULTS
import config

join_bp = Blueprint("join", __name__)


def get_current_player() -> Player | None:
    player_id = request.cookies.get("player_id")
    if player_id and player_id.isdigit():
        return Player.query.get(int(player_id))
    return None


@join_bp.route("/")
def index():
    return redirect(url_for("join.join_page"))


@join_bp.route("/join", methods=["GET"])
def join_page():
    game_session = session_state.get_or_create_session()

    if game_session.state != "LOBBY":
        return render_template("mobile/session_active.html")

    if Player.query.count() >= config.MAX_PLAYERS:
        return render_template("mobile/session_full.html")

    existing = get_current_player()
    if existing:
        return redirect(url_for("game.waiting"))

    return render_template("mobile/join.html", char_options=CHAR_OPTIONS)


@join_bp.route("/join", methods=["POST"])
def join_submit():
    game_session = session_state.get_or_create_session()

    if game_session.state != "LOBBY":
        return render_template("mobile/session_active.html"), 403

    if Player.query.count() >= config.MAX_PLAYERS:
        return render_template("mobile/session_full.html"), 403

    name = request.form.get("name", "").strip()
    if not name or len(name) > 50:
        return render_template("mobile/join.html", char_options=CHAR_OPTIONS,
                               error="Nome inválido (máx 50 caracteres)"), 400

    if Player.query.filter_by(name=name).first():
        return render_template("mobile/join.html", char_options=CHAR_OPTIONS,
                               error="Este nome já está em uso"), 400

    character = {
        "rosto":      request.form.get("rosto",      CHAR_DEFAULTS["rosto"]),
        "cabelo":     request.form.get("cabelo",     CHAR_DEFAULTS["cabelo"]),
        "pele":       request.form.get("pele",       CHAR_DEFAULTS["pele"]),
        "cor_cabelo": request.form.get("cor_cabelo", CHAR_DEFAULTS["cor_cabelo"]),
        "acessorio":  request.form.get("acessorio",  CHAR_DEFAULTS["acessorio"]),
        "fundo":      request.form.get("fundo",      CHAR_DEFAULTS["fundo"]),
    }

    player = Player(
        name=name,
        character_json=json.dumps(character),
        session_id=game_session.id,
    )
    db.session.add(player)
    db.session.flush()

    from avatar import generate_avatar
    avatar_path = generate_avatar(character, player.id)
    player.avatar_path = avatar_path
    db.session.commit()

    all_players = Player.query.all()
    socketio.emit("player_joined", {
        "name": name,
        "avatar_path": avatar_path,
        "player_count": len(all_players),
        "players": [{"id": p.id, "name": p.name, "avatar_path": p.avatar_path} for p in all_players],
    }, room="game_room")

    resp = make_response(redirect(url_for("game.waiting")))
    resp.set_cookie("player_id", str(player.id), httponly=True, samesite="Lax")
    return resp
