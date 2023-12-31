import logging
import platform
import random
import tempfile
import threading
from PIL import Image
from typing import TYPE_CHECKING
from activities import BaseActivity
from core.config.app import AppConfig
from pack.pack import Pack

if TYPE_CHECKING:
    from app import App

lock = threading.Lock()


class WallpaperActivity(BaseActivity):
    __type__ = "wallpaper"

    def __init__(self, app: "App"):
        if not lock.locked():
            app.on_exit_callbacks.append(self.stop)
        lock.acquire(blocking=True)
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

        self.timeout.start()

        if platform.system() == "Windows":
            import ctypes

            ctypes.windll.user32.SystemParametersInfoW(
                20, 0, str(self.wallpaper.absolute()), 3
            )

    def stop(self):
        if hasattr(self, "timeout") and self.timeout.is_alive():
            self.timeout.cancel()
        self.logger.info(f"Changing wallpaper to {self.config.wallpaper.current}")
        if platform.system() == "Windows":
            import ctypes

            ctypes.windll.user32.SystemParametersInfoW(
                20, 0, self.config.wallpaper.current, 3
            )
        if lock.locked() and not self.app.lock.locked():
            lock.release()
