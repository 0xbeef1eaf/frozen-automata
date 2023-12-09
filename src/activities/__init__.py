from abc import ABC
import threading
from typing import TYPE_CHECKING, List, Set

from core.config.app import AppConfig
from pack.pack import Pack

if TYPE_CHECKING:
    from app import App


config = AppConfig.load()
pack = Pack(config.pack)


class BaseActivity(ABC):
    __type__: str
    timeout: threading.Timer

    def __init__(self, app: "App", timeout: int = 0):
        self.app = app
        if timeout > 0:
            self.timeout = threading.Timer(timeout, self.stop)
            self.timeout.start()

    def stop(self):
        if hasattr(self, "timeout") and self.timeout.is_alive():
            self.timeout.cancel()


from .panic import PanicActivity

if config.image.active.enabled and len(pack.image) > 0:
    from .image import ImageActivity
if config.prompt.active.enabled and len(pack.prompt) > 0:
    from .prompt import PromptActivity
if config.wallpaper.active.enabled and len(pack.wallpaper) > 0:
    from .wallpaper import WallpaperActivity
if config.gif.active.enabled and len(pack.gif) > 0:
    from .gif import GifActivity
if config.web.active.enabled and len(pack.web) > 0:
    from .web import WebActivity


class Activity:
    @staticmethod
    def __all_subclasses__(_cls):
        return set(_cls.__subclasses__()).union(
            [s for c in _cls.__subclasses__() for s in Activity.__all_subclasses__(c)]
        )

    @staticmethod
    def __new__(cls, activity_type: str, app: "App", *args, **kwargs) -> BaseActivity:
        for subclass in Activity.__all_subclasses__(BaseActivity):
            if subclass.__type__ == activity_type:
                return subclass(app, *args, **kwargs)
        raise ValueError(f"Activity {activity_type} not found")

    @staticmethod
    def all() -> List[str]:
        return [
            c.__type__
            for c in Activity.__all_subclasses__(BaseActivity)
            if c.__type__ != "panic"
        ]
