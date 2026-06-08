import eventlet
eventlet.monkey_patch()

from app import create_app
from extensions import socketio
import config

app = create_app()

if __name__ == "__main__":
    print(f"\n{'='*50}")
    print("  Movie Night Party App")
    print(f"  Desktop: http://localhost:{config.PORT}/desktop")
    print(f"  Mobile:  http://<IP_LOCAL>:{config.PORT}/join")
    print(f"{'='*50}\n")
    socketio.run(app, host="0.0.0.0", port=config.PORT, debug=False)
