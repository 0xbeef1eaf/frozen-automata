from functools import cache
import json
from pathlib import Path
from typing import List
from core import Singleton
from core.paths import Paths


class Pack(metaclass=Singleton):
    path: Path
    config: dict
    description: str
    tags: List[str]
    images: Path
    wallpapers: Path
    prompts: List[str]
    buttons: List[str]

    def __init__(self, name: str = "default"):
        self.path = Paths.packs.joinpath(name).resolve()
        if not self.path.exists():
            self.path = Paths.resources.joinpath("packs", "default").resolve()
        with self.path.joinpath("pack.json").open("r") as f:
            self.config = json.load(f)
        self.images = self.path.joinpath("images").resolve()
        self.gifs = self.path.joinpath("gifs").resolve()
        self.wallpapers = self.path.joinpath("wallpapers").resolve()
        try:
            self.description = self.config["description"]
            self.tags = self.config["tags"]
            self.prompts = self.config["prompts"]
            self.buttons = self.config["buttons"]
            self.webs = self.config["webs"]
        except KeyError:
            raise ValueError("Invalid pack.json")

    @property
    @cache
    def image(self):
        return list(self.images.glob("*"))

    @property
    @cache
    def wallpaper(self):
        return list(self.wallpapers.glob("*"))

    @property
    @cache
    def prompt(self):
        return list(self.prompts)

    @property
    @cache
    def button(self):
        return list(self.buttons)

    @property
    @cache
    def gif(self):
        return list(self.gifs.glob("*"))

    @property
    @cache
    def web(self):
        return list(self.webs)
