import socket
import io
import qrcode

_cached_qr: bytes | None = None
_cached_url: str | None = None


def _is_wsl() -> bool:
    try:
        with open("/proc/version") as f:
            return "microsoft" in f.read().lower()
    except OSError:
        return False


def _windows_lan_ip() -> str | None:
    """Get the real Windows LAN IP via ipconfig.exe (available in WSL2)."""
    import subprocess
    import re
    try:
        result = subprocess.run(
            ["ipconfig.exe"], capture_output=True, text=True, timeout=4
        )
        # Prefer 192.168.x.x (Wi-Fi/Ethernet), then 10.x.x.x
        for pattern in (r"192\.168\.\d+\.\d+", r"10\.\d+\.\d+\.\d+"):
            match = re.search(pattern, result.stdout)
            if match:
                return match.group(0)
    except Exception:
        pass
    return None


def get_local_ip() -> str:
    if _is_wsl():
        win_ip = _windows_lan_ip()
        if win_ip:
            return win_ip

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def get_join_url(port: int = 5000) -> str:
    return f"http://{get_local_ip()}:{port}/join"


def generate_qr_png(port: int = 5000) -> bytes:
    global _cached_qr, _cached_url
    url = get_join_url(port)
    if _cached_qr and _cached_url == url:
        return _cached_qr

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#000000", back_color="#FFFFFF")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    _cached_qr = buf.getvalue()
    _cached_url = url
    return _cached_qr


def reset_cache() -> None:
    global _cached_qr, _cached_url
    _cached_qr = None
    _cached_url = None
