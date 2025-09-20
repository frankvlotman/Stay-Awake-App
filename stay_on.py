# StayOn — a lightweight tray app that keeps your Windows PC awake.
# - Starts ACTIVE immediately on launch
# - Shows a 2-second confirmation popup ("StayOn Activated")
# - Tray menu: Quit

import time
import threading
import ctypes
import tkinter as tk
from tkinter import ttk
import pystray
from pystray import MenuItem as Item, Menu
from PIL import Image, ImageDraw

APP_NAME = "StayOn"

# --- Windows keep-awake flags ---
ES_CONTINUOUS       = 0x80000000
ES_SYSTEM_REQUIRED  = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

kernel32 = ctypes.windll.kernel32

def apply_keep_awake():
    kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    )

def clear_keep_awake():
    kernel32.SetThreadExecutionState(ES_CONTINUOUS)

# --- Tiny tray icon (monitor) ---
def make_icon(active=True):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([2, 4, 13, 10], fill=(0, 0, 0, 255) if active else None, outline=(0, 0, 0, 255))
    d.line([7, 10, 8, 13], fill=(0, 0, 0, 255))
    return img

# --- 2-second activation popup ---
def show_activation_popup(text="StayOn Activated", ms=2000):
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    frm = ttk.Frame(root, padding=12)
    frm.pack()
    ttk.Label(frm, text=text).pack()
    root.update_idletasks()
    w, h = root.winfo_reqwidth(), root.winfo_reqheight()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"+{(sw//2)-(w//2)}+{(sh//2)-(h//2)}")
    root.after(ms, root.destroy)
    root.mainloop()

class StayOnTray:
    def __init__(self):
        self.interval = 30
        self.stop_event = threading.Event()
        self.worker = threading.Thread(target=self._run, daemon=True)

        apply_keep_awake()
        threading.Thread(target=show_activation_popup, daemon=True).start()

        self.icon = pystray.Icon(
            APP_NAME,
            make_icon(True),
            title=f"{APP_NAME}: Active"   # <- no API mention
        )
        self.icon.menu = Menu(Item("Quit", self.quit_app))

    def _run(self):
        while not self.stop_event.is_set():
            apply_keep_awake()
            time.sleep(self.interval)

    def quit_app(self, icon, item):
        self.stop_event.set()
        clear_keep_awake()
        self.icon.stop()

    def run(self):
        self.worker.start()
        self.icon.run()

if __name__ == "__main__":
    StayOnTray().run()
