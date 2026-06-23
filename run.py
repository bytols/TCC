import eventlet
eventlet.monkey_patch()

import socket
from app import create_app
from extensions import socketio
import config

app = create_app()

def _local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

if __name__ == "__main__":
    ip = _local_ip()
    print(f"\n{'='*50}")
    print("  Movie Night Party App")
    print(f"  Desktop: http://localhost:{config.PORT}/desktop")
    print(f"  Mobile:  http://{ip}:{config.PORT}/join")
    print(f"{'='*50}\n")
    socketio.run(app, host="0.0.0.0", port=config.PORT, debug=False)
