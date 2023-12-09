import argparse
import atexit
import logging
import os
from pathlib import Path
import platform
import random
import signal
import sys
import tempfile
import threading
import tkinter
from typing import Callable, List, Optional
from PIL import Image
from browsers import get

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

        self.reload()

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
        while True:
            with self.lock:
                for _type in Activity.all():
                    config = getattr(self.config, _type)
                    if config.active.should():
                        self.launch(_type)
            self.hibernate.sleep()

    def launch(self, activity: Optional[str] = None):
        if activity is None:
            # Determine correct activity by the probability of each activity
            activity = random.choices(
                Activity.all(),
                weights=[getattr(self.config, _type).active.probability for _type in Activity.all()],
                k=1,
            )[0]
        self.logger.info(f"Launching activity {activity}")
        thread = threading.Timer(
            random.random(), function=lambda: Activity(activity, self)
        )
        thread.start()

    def configure_system_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("Panic", lambda: self.launch("panic")),
            pystray.MenuItem("Reload", lambda: self.reload()),
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

    def reload(self):
        self.config.reload()
        if self.config.panic.keychord != "":
            self.hook = keyboard.add_hotkey(
                self.config.panic.keychord, self.launch, args=("panic",)
            )
        elif hasattr(self, "hook"):
            keyboard.remove_hotkey(self.hook)
        else:
            self.logger.warning("No panic keychord set")
        self.hibernate = Hibernation(self.config.hibernate.strategy, self)

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
        
        pid = os.getpid()

        # Add a delay to allow the threads to stop
        threading.Timer(5, os.kill, args=[pid, signal.SIGINT]).start()


if __name__ == "__main__":
    app = App()
    app.start()
