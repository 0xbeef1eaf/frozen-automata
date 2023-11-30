import logging
import os
import platform
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
        self.logger = logging.getLogger(__name__)
        self.config = core.config.AppConfig.load()
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

        if self.config.debug:
            self.logger.setLevel(logging.DEBUG)

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

    def tick(self):
        self.lock.acquire(blocking=True)
        if self.config.image.active.should():
            self.launch("image")
        # if self.config.video.active.should():
        #     self.launch("video")
        # if self.config.audio.active.should():
            # self.launch("audio")
        if self.config.prompt.active.should():
            self.launch("prompt")
        if self.config.wallpaper.active.should():
            self.launch("wallpaper")
        # Should sleep based on the hibernation strategy
        self.lock.release()
        self.hibernate.sleep()
        self.tick()

    def launch(self, activity: str):
        if activity in ("panic", "configure"):
            self.lock.acquire(blocking=True)
        self.logger.info(f"Launching activity {activity}")
        Activity(activity, self)

    def configure_system_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("Panic", lambda: self.launch("panic")),
            pystray.MenuItem(
                "Configure",
                lambda: self.launch("configuration"),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Debug",
                pystray.Menu(
                    pystray.MenuItem(
                        "Image",
                        lambda: self.launch("image"),
                    ),
                    # pystray.MenuItem(
                    #     "Video",
                    #     lambda: self.launch("video"),
                    # ),
                    # pystray.MenuItem(
                    #     "Audio",
                    #     lambda: self.launch("audio"),
                    # ),
                    pystray.MenuItem(
                        "Prompt",
                        lambda: self.launch("prompt"),
                    ),
                    pystray.MenuItem(
                        "Wallpaper",
                        lambda: self.launch("wallpaper"),
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
