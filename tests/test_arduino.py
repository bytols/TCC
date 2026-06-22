from unittest.mock import MagicMock, patch
import arduino


def _setup_ports():
    """Inject mock ports directly into the module state."""
    mock_a = MagicMock()
    mock_b = MagicMock()
    arduino._port_a = mock_a
    arduino._port_b = mock_b
    return mock_a, mock_b


def test_send_led_player1_routes_to_port_a_slot1():
    mock_a, mock_b = _setup_ports()
    arduino.send_led(1, "BLUE")
    mock_a.write.assert_called_once_with(b"S1:BLUE\n")
    mock_b.write.assert_not_called()


def test_send_led_player2_routes_to_port_a_slot2():
    mock_a, mock_b = _setup_ports()
    arduino.send_led(2, "GREEN")
    mock_a.write.assert_called_once_with(b"S2:GREEN\n")
    mock_b.write.assert_not_called()


def test_send_led_player3_routes_to_port_b_slot1():
    mock_a, mock_b = _setup_ports()
    arduino.send_led(3, "ORANGE")
    mock_b.write.assert_called_once_with(b"S1:ORANGE\n")
    mock_a.write.assert_not_called()


def test_send_led_player4_routes_to_port_b_slot2():
    mock_a, mock_b = _setup_ports()
    arduino.send_led(4, "WHITE")
    mock_b.write.assert_called_once_with(b"S2:WHITE\n")
    mock_a.write.assert_not_called()


def test_send_led_port_none_does_not_raise():
    arduino._port_a = None
    arduino._port_b = None
    arduino.send_led(1, "BLUE")   # port A is None
    arduino.send_led(3, "PINK")   # port B is None


def test_init_opens_serial_ports_from_config(monkeypatch):
    mock_instance_a = MagicMock()
    mock_instance_b = MagicMock()

    monkeypatch.setattr("config.ARDUINO_A_PORT", "/dev/ttyA0")
    monkeypatch.setattr("config.ARDUINO_B_PORT", "/dev/ttyB0")
    monkeypatch.setattr("config.ARDUINO_BAUD", 9600)

    with patch("arduino.serial.Serial", side_effect=[mock_instance_a, mock_instance_b]) as mock_cls:
        arduino._port_a = None
        arduino._port_b = None
        arduino.init()

    mock_cls.assert_any_call("/dev/ttyA0", 9600)
    mock_cls.assert_any_call("/dev/ttyB0", 9600)
    assert arduino._port_a is mock_instance_a
    assert arduino._port_b is mock_instance_b
