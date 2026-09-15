"""
FileCore System Tray App
Requires pystray and Pillow.
Run: python filecore/tray/tray_app.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import threading
import subprocess
from PIL import Image, ImageDraw

try:
    import pystray
    from pystray import MenuItem as item
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("[Tray] pystray not installed. Install with: pip install pystray Pillow")


def create_icon_image(color=(0, 168, 107)):
    """Create a simple green shield icon."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([8, 8, 56, 56], fill=color)
    draw.text((22, 22), "FC", fill="white")
    return img


def on_open(icon, item):
    subprocess.Popen(["python", "-m", "filecore.cli.vault"], 
                     cwd=os.path.join(os.path.dirname(__file__), "../.."))


def on_status(icon, item):
    subprocess.Popen(["python", "-m", "filecore.cli.vault", "status"],
                     cwd=os.path.join(os.path.dirname(__file__), "../.."))


def on_quit(icon, item):
    icon.stop()


def run_tray():
    if not TRAY_AVAILABLE:
        print("Tray not available. Run the CLI directly with: python -m filecore.cli.vault")
        return

    icon_image = create_icon_image()
    menu = pystray.Menu(
        item("FileCore", on_open, default=True),
        item("Status", on_status),
        pystray.Menu.SEPARATOR,
        item("OFFLINE / LOCAL MODE", lambda i, it: None, enabled=False),
        pystray.Menu.SEPARATOR,
        item("Quit FileCore", on_quit)
    )
    icon = pystray.Icon("FileCore", icon_image, "FileCore — Local File Intelligence", menu)
    icon.run()


if __name__ == "__main__":
    run_tray()
