from flask_socketio import join_room, emit
from extensions import socketio
from models import Player
import session_state


@socketio.on("connect")
def on_connect():
    pass


@socketio.on("join_room")
def on_join_room(data=None):
    join_room("game_room")
    _emit_current_state()


@socketio.on("desktop_connect")
def on_desktop_connect(data=None):
    join_room("game_room")
    _emit_current_state()


@socketio.on("request_state")
def on_request_state(data=None):
    _emit_current_state()


def _emit_current_state():
    session = session_state.get_session()
    if session is None:
        session = session_state.get_or_create_session()
    players = Player.query.all()
    emit("state_change", {
        "state": session.state,
        "player_count": len(players),
        "players": [{"id": p.id, "name": p.name, "avatar_path": p.avatar_path} for p in players],
    })
