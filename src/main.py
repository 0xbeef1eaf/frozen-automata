from email.mime import image
import os
import queue
import random
import threading
import logging
import time
from timeit import repeat
import tkinter
from turtle import st
import keyboard
import pystray
from PIL import Image
from pathlib import Path
import config
from window import Window

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)


class App:
    def __init__(self):
        # Load the config
        self.config = config.Config()
        self.logger = logging.getLogger("App")

        self.start_time = time.time()

        # Load the icon
        self.icon = pystray.Icon(
            "frozen-automata",
            Image.open(self.config.paths.resources.joinpath("default/default.ico")),
            "Frozen Automata",
            pystray.Menu(
                pystray.MenuItem("Quit", self.panic),
            ),
        )

        self.root = tkinter.Tk()
        self.root.withdraw()
        # Start the background thread
        self.background_thread = threading.Thread(target=self.background)
        self.root.after(0, self.background_thread.start)
        self.icon_thread = threading.Thread(target=self.icon.run).start()

    def run(self):
        self.logger.info("Running Frozen Automata")
        self.spawn_window("startup")
        self.root.mainloop()

    def spawn_window(self, _type: str, *args, **kwargs):
        self.logger.debug(f"Spawning window of type {_type}")
        self.root.after(0, lambda: Window(_type, owner=self, *args, **kwargs))
    
    def panic(self, icon: pystray.Icon, item):
        if not self.config.panic.enabled:
            self.logger.warning("Panic is disabled, ignoring panic request")
            self.spawn_window(
                "prompt",
                title="You didn't think you could escape that easily, did you?",
                message="I will not escape.",
                repeat=3,
                image=self.config.paths.resources.joinpath("default/loading.png"),
            )
        elif self.config.password_hash != "":
            self.logger.info("Password is set, requesting password")
            self.spawn_window(
                "prompt",
                title="You didn't think you could escape that easily, did you?",
                message="Enter the password to quit",
                password=True,
                repeat=1,
                image=self.config.paths.resources.joinpath("default/loading.png"),
            )
        else:
            self.logger.info("Panic is enabled, quitting")
            self.quit(icon, item)



    def quit(self, icon: pystray.Icon, item):
        icon.stop()
        self.root.quit()
        self.root.destroy()
        os._exit(0)

    def background(self):
        start_time = time.time()
        time.sleep(self.config.timer.startup)
        while True:
            if self.config.timer.runtime > 0 and time.time() - start_time > self.config.timer.runtime:
                self.logger.info("Runtime has expired, quitting")
                self.root.after(0, self.quit, self.icon, None)

            roll = random.random()
            if roll < self.config.windows.popup.probability:
                self.spawn_window("popup", timeout=random.uniform(self.config.windows.popup.timeout.min, self.config.windows.popup.timeout.max))
            if roll < self.config.windows.prompt.probability:
                self.spawn_window(
                    "prompt",
                    image=random.choice(
                        [image for image in self.config.paths.pack.glob(f"images/*")]
                    ),
                    repeat=self.config.windows.prompt.repetition,
                    message=random.choice(self.config.paths.pack.joinpath("prompts.txt").read_text().splitlines())
                )
            time.sleep(self.config.timer.loop)


app = App()
app.run()
