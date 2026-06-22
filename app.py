import eventlet
eventlet.monkey_patch()

from flask import Flask
from extensions import db, socketio
import config


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:?check_same_thread=False"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PORT"] = config.PORT
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    if test_config:
        app.config.update(test_config)

    async_mode = "threading" if app.config.get("TESTING") else "eventlet"
    db.init_app(app)
    socketio.init_app(app, async_mode=async_mode, cors_allowed_origins="*")

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

    import arduino
    arduino.init()

    return app
