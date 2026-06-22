import serial
import config

_port_a = None
_port_b = None


def init():
    global _port_a, _port_b
    if config.ARDUINO_A_PORT:
        try:
            _port_a = serial.Serial(config.ARDUINO_A_PORT, config.ARDUINO_BAUD)
        except Exception:
            _port_a = None
    if config.ARDUINO_B_PORT:
        try:
            _port_b = serial.Serial(config.ARDUINO_B_PORT, config.ARDUINO_BAUD)
        except Exception:
            _port_b = None


def send_led(player_id, color):
    if player_id in (1, 2):
        port = _port_a
        slot = player_id
    else:
        port = _port_b
        slot = player_id - 2
    if port is None:
        return
    port.write(f"S{slot}:{color}\n".encode())
