import threading
import webview
from app import create_app

flask_app = create_app()

def start_flask():
    flask_app.run()


def main():
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    webview.create_window(
        title="RentTrace",
        url="http://127.0.0.1:5000",
        width=1280,
        height=800,
        min_size=(1024, 600),
        resizable=True,
    )
    webview.start()


if __name__ == "__main__":
    main()