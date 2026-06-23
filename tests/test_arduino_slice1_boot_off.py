from unittest.mock import MagicMock, patch
import arduino


def _mock_init(monkeypatch, mock_a, mock_b):
    """Patch config and serial.Serial so init() uses mock ports."""
    monkeypatch.setattr("config.ARDUINO_A_PORT", "/dev/ttyA0")
    monkeypatch.setattr("config.ARDUINO_B_PORT", "/dev/ttyB0")
    monkeypatch.setattr("config.ARDUINO_BAUD", 9600)
    arduino._port_a = None
    arduino._port_b = None
    with patch("arduino.serial.Serial", side_effect=[mock_a, mock_b]):
        arduino.init()


# --- Tracer bullet ---

def test_init_sends_off_to_arduino_a_slot1(monkeypatch):
    mock_a, mock_b = MagicMock(), MagicMock()
    _mock_init(monkeypatch, mock_a, mock_b)
    mock_a.write.assert_any_call(b"S1:OFF\n")


# --- Remaining Arduino A / B slots ---

def test_init_sends_off_to_arduino_a_slot2(monkeypatch):
    mock_a, mock_b = MagicMock(), MagicMock()
    _mock_init(monkeypatch, mock_a, mock_b)
    mock_a.write.assert_any_call(b"S2:OFF\n")


def test_init_sends_off_to_arduino_b_slot1(monkeypatch):
    mock_a, mock_b = MagicMock(), MagicMock()
    _mock_init(monkeypatch, mock_a, mock_b)
    mock_b.write.assert_any_call(b"S1:OFF\n")


def test_init_sends_off_to_arduino_b_slot2(monkeypatch):
    mock_a, mock_b = MagicMock(), MagicMock()
    _mock_init(monkeypatch, mock_a, mock_b)
    mock_b.write.assert_any_call(b"S2:OFF\n")


# --- Robustness ---

def test_init_with_no_ports_configured_does_not_raise(monkeypatch):
    monkeypatch.setattr("config.ARDUINO_A_PORT", "")
    monkeypatch.setattr("config.ARDUINO_B_PORT", "")
    arduino._port_a = None
    arduino._port_b = None
    arduino.init()  # Must not raise


def test_send_led_off_writes_correct_bytes_arduino_a(monkeypatch):
    mock_a = MagicMock()
    arduino._port_a = mock_a
    arduino._port_b = None
    arduino.send_led(1, "OFF")
    mock_a.write.assert_called_once_with(b"S1:OFF\n")


def test_send_led_off_writes_correct_bytes_arduino_b(monkeypatch):
    mock_b = MagicMock()
    arduino._port_a = None
    arduino._port_b = mock_b
    arduino.send_led(3, "OFF")
    mock_b.write.assert_called_once_with(b"S1:OFF\n")
