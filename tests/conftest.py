import json
import pytest
from app import create_app
from extensions import db as _db


@pytest.fixture()
def app():
    application = create_app({"TESTING": True})
    with application.app_context():
        _db.drop_all()
        _db.create_all()
        # Ensure a lobby session exists (get_or_create_session is lazy)
        import session_state
        session_state.get_or_create_session()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def add_player(app):
    """Fixture factory: inserts a player directly into the DB."""
    def _add(name="Player"):
        from models import Player, Session
        with app.app_context():
            session = Session.query.first()
            player = Player(
                name=name,
                character_json=json.dumps({}),
                avatar_path="/static/img/avatars/test.png",
                session_id=session.id,
            )
            _db.session.add(player)
            _db.session.commit()
            return player.id
    return _add
