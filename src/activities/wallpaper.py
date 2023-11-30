import logging
import platform
import random
import tempfile
import threading
import time
from PIL import Image
from typing import TYPE_CHECKING
from activities import BaseActivity
from core.config.app import AppConfig
from pack.pack import Pack

if TYPE_CHECKING:
    from app import App

class WallpaperActivity(BaseActivity):
    __type__ = "wallpaper"

    def __init__(self, app: "App"):
        self.app = app
        self.config = AppConfig()
        self.pack = Pack()
        self.logger = logging.getLogger(__name__)

        super().__init__(app=app, timeout=0)
        timeout = self.config.wallpaper.timer.random()
        self.logger.info(f"Wallpaper timeout: {timeout}s")
        self.timeout = threading.Timer(timeout, self.stop)

        # Change the wallpaper
        self.wallpaper = random.choice(self.pack.wallpaper)
        self.logger.info(f"Changing wallpaper to {self.wallpaper}")

        # Trap the app exit to change the wallpaper back
        self.app.on_exit_callbacks.append(self.stop)

        # Resize the image to fit the screen
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        image = Image.open(self.wallpaper)
        image.thumbnail(
            (self.app.root.winfo_screenwidth(), self.app.root.winfo_screenheight()), Image.LANCZOS
        )
        image.save(temp_file.name)

        self.timeout.start()

        if platform.system() == "Windows":
            import ctypes

            ctypes.windll.user32.SystemParametersInfoW(
                20, 0, temp_file.name, 0
            )
        elif platform.system() == "Darwin":
            import subprocess

            subprocess.run(
                [
                    "osascript",
                    "-e",
                    f'tell application "Finder" to set desktop picture to POSIX file "{temp_file.name}"',
                ]
            )
        else:
            self.logger.warning("Unsupported platform")

    def stop(self):
        if hasattr(self, "timeout") and self.timeout.is_alive():
            self.timeout.cancel()
        # Change to a safe wallpaper
        safe = str(self.pack.wallpaper_safe)
        self.logger.info(f"Changing wallpaper to {safe}")
        if platform.system() == "Windows":
            import ctypes

            ctypes.windll.user32.SystemParametersInfoW(
                20, 0, safe, 0
            )
        elif platform.system() == "Darwin":
            import subprocess

            subprocess.run(
                [
                    "osascript",
                    "-e",
                    f'tell application "Finder" to set desktop picture to POSIX file "{safe}"',
                ]
            )
        else:
            self.logger.warning("Unsupported platform")