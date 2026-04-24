import ctypes
import os
import sys
import time
import threading
import urllib.request
import webview
from app import create_app

# ── Tell Windows this process is DPI-aware ──
# Prevents icon and UI scaling issues on high-res screens
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()   # Fallback for older Windows
    except Exception:
        pass

flask_app = create_app()

FLASK_URL = "http://127.0.0.1:5000"


def get_icon_path() -> str:
    """
    Resolves icon path whether running as .py or
    bundled .exe via PyInstaller (sys._MEIPASS).
    """
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base, "app", "static", "icons", "renttrace.ico")


def start_flask():
    flask_app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
    )


def wait_for_flask(timeout: int = 10) -> bool:
    """
    Polls Flask every 100ms until it responds or timeout is reached.
    Prevents PyWebView from opening a blank window before Flask is ready.
    """
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(FLASK_URL)
            return True
        except Exception:
            time.sleep(0.1)
    return False


def main():
    # ── Start Flask in background thread ──
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # ── Wait until Flask is ready ──
    ready = wait_for_flask(timeout=10)
    if not ready:
        print("ERROR: Flask did not start in time.")
        sys.exit(1)

    # ── Resolve icon ──
    icon_path = get_icon_path()
    icon      = icon_path if os.path.exists(icon_path) else None

    # ── Open PyWebView window ──
    webview.create_window(
        title="RentTrace",
        url=FLASK_URL,
        width=1280,
        height=800,
        min_size=(1024, 600),
        resizable=True,
    )
    webview.start(icon=icon)


if __name__ == "__main__":
    main()