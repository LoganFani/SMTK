import os
import sys
import threading
import uvicorn

# IMPORTANT: Do NOT import pystray or PIL at the top level
# This prevents the X11 error in Docker

def run_server():
    # Change host to 0.0.0.0 so you can access it outside the container
    host = "0.0.0.0" if os.environ.get("DOCKER_BUILD") == "true" else "127.0.0.1"
    uvicorn.run("src.app:app", host=host, port=8000, log_level="info")

def setup_tray():
    # Only import these when actually starting the tray
    from pystray import Icon, Menu, MenuItem
    from PIL import Image
    
    # Use resource_path for the icon
    # (Assuming you kept the resource_path function we built earlier)
    icon_path = os.path.join(os.path.dirname(__file__), "media", "simmy.png")
    logo = Image.open(icon_path)

    icon = Icon("SMTK", logo, menu=Menu(
        MenuItem("Open SMTK", lambda: None), # Browser open won't work in Docker
        MenuItem("Exit", lambda i, j: os._exit(0))
    ))
    icon.run()

if __name__ == "__main__":
    # 1. Start the server in a background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # 2. Check if we should skip the tray
    if os.environ.get("DOCKER_BUILD") == "true":
        print("Docker detected. Server is running at http://localhost:8000")
        # Keep the main thread alive since there's no tray to hold it
        server_thread.join()
    else:
        # Run the tray icon (this holds the main thread on Windows/Mac)
        setup_tray()