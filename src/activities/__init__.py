from abc import ABC
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app import App


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
from .image import ImageActivity
from .prompt import PromptActivity
from .wallpaper import WallpaperActivity
from .gif import GifActivity
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
    def all(_cls):
        return set(_cls.__type__).union(
            [s for c in _cls.__type__() for s in Activity.__all_subclasses__(c)]
        )
