from functools import cache
import json
from pathlib import Path
import platform
import shutil
from typing import List
from core import Singleton
from core.paths import Paths


class Pack(metaclass=Singleton):
    path: Path
    config: dict
    description: str
    tags: List[str]
    images: Path
    fonts: Path
    audios: Path
    videos: Path
    wallpapers: Path
    overlays: Path
    captions: List[str]
    prompts: List[str]
    buttons: List[str]

    def __init__(self, name: str = "default"):
        self.path = Paths.packs.joinpath(name).resolve()
        if not self.path.exists():
            self.path = Paths.resources.joinpath("packs", "default").resolve()
        with self.path.joinpath("pack.json").open("r") as f:
            self.config = json.load(f)
        self.description = self.config["description"]
        self.tags = self.config["tags"]
        self.images = self.path.joinpath("images").resolve()
        self.fonts = self.path.joinpath("fonts").resolve()
        self.audios = self.path.joinpath("audios").resolve()
        self.videos = self.path.joinpath("videos").resolve()
        self.wallpapers = self.path.joinpath("wallpapers").resolve()
        self.overlays = self.path.joinpath("overlays").resolve()
        self.captions = self.config["captions"]
        self.prompts = self.config["prompts"]
        self.buttons = self.config["buttons"]

    @property
    @cache
    def image(self):
        return list(self.images.glob("*"))

    @property
    @cache
    def font(self):
        return list(self.fonts.glob("*"))

    @property
    @cache
    def audio(self):
        return list(self.audios.glob("*"))

    @property
    @cache
    def video(self):
        return list(self.videos.glob("*"))

    @property
    @cache
    def wallpaper(self):
        return list(self.wallpapers.glob("*"))

    @property
    @cache
    def wallpaper_safe(self):
        return Paths.resources.joinpath("packs", "default", "wallpaper", f'safe.{platform.system().lower()}.png').resolve()

    @property
    @cache
    def overlay(self):
        return list(self.overlays.glob("*"))

    @property
    @cache
    def caption(self):
        return list(self.captions)

    @property
    @cache
    def prompt(self):
        return list(self.prompts)

    @property
    @cache
    def button(self):
        return list(self.buttons)
