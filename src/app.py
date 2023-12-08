import argparse
import atexit
import logging
import os
from pathlib import Path
import platform
import tempfile
import threading
import tkinter
from typing import Callable, List
from PIL import Image

import keyboard
from activities import Activity
from core import Singleton
import core.config
import core.paths
from hibernate import Hibernation
from pack import Pack
import pystray


class App(metaclass=Singleton):
    logger: logging.Logger
    config: core.config.AppConfig
    pack: Pack
    root: tkinter.Tk

    on_exit_callbacks: List[Callable[[], None]] = []

    def __init__(self):
        self.config = core.config.AppConfig.load()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

        if self.config.debug:
            self.logger.setLevel(logging.DEBUG)

        atexit.register(self.stop)
        self.pack = Pack(self.config.pack)
        self.paths = core.paths.Paths()
        self.system_tray: pystray.Icon = self.configure_system_tray()
        self.hook = keyboard.add_hotkey(
            self.config.panic.keychord, self.launch, args=("panic",)
        )
        self.hibernate = Hibernation(self.config.hibernate.strategy, self)

        self.lock = threading.Lock()

        self.root = tkinter.Tk()
        self.root.geometry("0x0+0+0")
        self.root.withdraw()

        self.threads = [
            threading.Thread(
                target=self.system_tray.run,
            ),
            threading.Thread(
                target=self.tick,
            ),
        ]

        if self.config.timer.minimum + self.config.timer.maximum > 0:
            _time = self.config.timer.random()
            self.logger.info(f"Timer set to {_time} seconds")
            self.threads.append(
                threading.Timer(
                    _time,
                    self.stop,
                )
            )

        # If the wallpaper module is enabled, we should save the current wallpaper
        if self.config.wallpaper.active.enabled:
            if platform.system() == "Windows":
                import ctypes

                wallpaper = ctypes.create_unicode_buffer(512)
                result = ctypes.windll.user32.SystemParametersInfoW(
                    0x73, 512, wallpaper, 0
                )
                if result:
                    self.logger.info(f"Saving current wallpaper {wallpaper.value}")
                    wallpaper_path = Path(wallpaper.value)
                    temp_file = tempfile.TemporaryFile(
                        suffix=wallpaper_path.suffix, delete=False
                    )
                    with wallpaper_path.open("rb") as f:
                        temp_file.write(f.read())
                    self.config.wallpaper.current = temp_file.name

    def tick(self):
        self.lock.acquire(blocking=True)
        if self.config.image.active.should() and len(self.pack.image) > 0:
            self.launch("image")
        if self.config.gif.active.should() and len(self.pack.gif) > 0:
            self.launch("gif")
        if self.config.prompt.active.should() and len(self.pack.prompt) > 0:
            self.launch("prompt")
        if self.config.wallpaper.active.should() and len(self.pack.wallpaper) > 0:
            self.launch("wallpaper")
        if self.config.web.active.should() and len(self.pack.web) > 0:
            self.launch("web")
        self.lock.release()
        self.hibernate.sleep()
        self.tick()

    def launch(self, activity: str):
        if activity in ("panic", "configure"):
            self.lock.acquire(blocking=True)
        self.logger.info(f"Launching activity {activity}")
        thread = threading.Thread(target= lambda: Activity(activity, self))
        thread.start()

    def configure_system_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("Panic", lambda: self.launch("panic")),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Debug",
                pystray.Menu(
                    pystray.MenuItem(
                        "Image",
                        lambda: self.launch("image"),
                    ),
                    pystray.MenuItem(
                        "Prompt",
                        lambda: self.launch("prompt"),
                    ),
                    pystray.MenuItem(
                        "Wallpaper",
                        lambda: self.launch("wallpaper"),
                    ),
                    pystray.MenuItem(
                        "Gif",
                        lambda: self.launch("gif"),
                    ),
                    pystray.MenuItem(
                        "Web",
                        lambda: self.launch("web"),
                    ),
                ),
                visible=self.config.debug,
            ),
        )
        return pystray.Icon(
            "Frozen Automata",
            icon=Image.open(self.paths.resources.joinpath("default.ico").resolve()),
            menu=menu,
        )

    def start(self):
        self.logger.info("Starting application")
        [thread.start() for thread in self.threads]
        self.root.mainloop()

    def stop(self):
        self.logger.info("Stopping application")
        [s() for s in self.on_exit_callbacks]
        self.root.after(0, self.root.destroy)
        self.system_tray.stop()
        keyboard.remove_hotkey(self.hook)
        os._exit(0)


if __name__ == "__main__":
    app = App()
    app.start()
