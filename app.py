import eventlet
eventlet.monkey_patch()

from flask import Flask
from extensions import db, socketio
import config


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:?check_same_thread=False"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PORT"] = config.PORT

    db.init_app(app)
    socketio.init_app(app, async_mode="eventlet", cors_allowed_origins="*")

    with app.app_context():
        from models import create_tables
        create_tables()

    from routes.desktop import desktop_bp
    from routes.join import join_bp
    from routes.game import game_bp
    app.register_blueprint(desktop_bp)
    app.register_blueprint(join_bp)
    app.register_blueprint(game_bp)

    import sockets.events  # noqa: F401 — registers handlers

    return app
