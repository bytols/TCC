from flask import Blueprint, render_template, redirect, url_for, Response, jsonify, current_app
from extensions import db
from models import Player, Vote, RoundPool
import session_state
import qr as qr_module
from match import calculate_match
from routes.game import enrich_match_movies
import config

desktop_bp = Blueprint("desktop", __name__)


@desktop_bp.route("/desktop")
def desktop():
    session = session_state.get_or_create_session()
    players = Player.query.all()
    join_url = qr_module.get_join_url(current_app.config.get("PORT", 5000))
    context = {
        "session": session,
        "players": players,
        "join_url": join_url,
        "player_count": len(players),
        "elapsed": session_state.elapsed_seconds(),
        "auto_start_seconds": config.AUTO_START_SECONDS,
    }

    state = session.state
    if state.startswith("SHOW_") or state == "FINAL":
        round_num = (session.result_round or 1) if state == "FINAL" else int(state.split("_")[1])
        context["consensus"] = (state == "FINAL")
        context["result_seconds"] = session.result_seconds
        votes = session_state.get_round_votes(round_num)
        match_data = enrich_match_movies(calculate_match(votes, len(players)))
        context["match_data"] = match_data
        if state == "FINAL":
            context["consensus_movies"] = [m for m in match_data["movies"] if m["is_match"]]
        context["round_num"] = round_num

    elif state.startswith("ROUND_"):
        round_num = int(state.split("_")[1])
        context["round_num"] = round_num
        context["submitted_count"] = session_state.count_submitted(round_num)
        context["submitted_ids"] = session_state.submitted_player_ids(round_num)
        if round_num >= 2:
            context["pool"] = RoundPool.query.filter_by(round_number=round_num).all()

    return render_template("desktop/lobby.html", **context)


@desktop_bp.route("/qr.png")
def qr_code():
    port = current_app.config.get("PORT", 5000)
    png = qr_module.generate_qr_png(port)
    return Response(png, mimetype="image/png")


@desktop_bp.route("/admin/start", methods=["POST"])
def admin_start():
    session = session_state.get_session()
    if session is None or session.state != "LOBBY":
        return jsonify({"error": "Estado inválido"}), 400
    if Player.query.count() < 2:
        return jsonify({"error": "Precisa de pelo menos 2 jogadores"}), 400
    new_state = session_state.advance_state()
    return jsonify({"state": new_state})


@desktop_bp.route("/admin/advance", methods=["POST"])
def admin_advance():
    session = session_state.get_session()
    if session is None:
        return jsonify({"error": "Nenhuma sessão ativa"}), 400
    new_state = session_state.advance_state()
    return jsonify({"state": new_state})


@desktop_bp.route("/api/lobby_state")
def api_lobby_state():
    session = session_state.get_or_create_session()
    players = Player.query.all()
    data = {
        "state": session.state,
        "player_count": len(players),
        "elapsed_seconds": session_state.elapsed_seconds(),
        "consensus": session.state == "FINAL",
        "players": [
            {"id": p.id, "name": p.name, "avatar_path": p.avatar_path}
            for p in players
        ]
    }
    if session.state.startswith("ROUND_"):
        rn = int(session.state.split("_")[1])
        data["progress"] = {
            "round": rn,
            "submitted": session_state.count_submitted(rn),
            "total": len(players),
            "submitted_ids": session_state.submitted_player_ids(rn),
        }
    return jsonify(data)


@desktop_bp.route("/admin/end", methods=["POST"])
def admin_end():
    session_state.clear_session()
    return jsonify({"status": "cleared"})
