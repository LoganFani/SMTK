import os
import threading
import webbrowser
import uvicorn
from pystray import Icon, Menu, MenuItem
from PIL import Image

SMKT_LOGO = Image.open(os.path.join(os.path.dirname(__file__), "media", "simmy.png"))


def run_server():
    uvicorn.run("src.app:app", host="127.0.0.1", port=8000, log_level="info")


def open_browser(icon, item):
    webbrowser.open("http://127.0.0.1:8000")


def on_exit(icon, item):
    icon.stop()
    os._exit(0)


def setup_tray():
    icon = Icon("SMTK", SMKT_LOGO, menu=Menu(
        MenuItem("Open SMTK", open_browser),
        MenuItem("Exit", on_exit)
    ))
    

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    icon.run()

if __name__ == "__main__":
    setup_tray()