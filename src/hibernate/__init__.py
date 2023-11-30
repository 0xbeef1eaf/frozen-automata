from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from core import Singleton

if TYPE_CHECKING:
    from app import App


class BaseHibernation(ABC):
    __type__: str

    def __init__(self):
        pass

    @abstractmethod
    def sleep(self):
        """
        Sleeps the thread for a set amount of time to determine the tick rate.
        """
        pass


from .default import DefaultHibernation
from .original import OriginalHibernation


class Hibernation:
    @staticmethod
    def __all_subclasses__(_cls):
        return set(_cls.__subclasses__()).union(
            [
                s
                for c in _cls.__subclasses__()
                for s in Hibernation.__all_subclasses__(c)
            ]
        )

    @staticmethod
    def __new__(
        cls, hibernation_type: str, app: "App", *args, **kwargs
    ) -> BaseHibernation:
        for subclass in Hibernation.__all_subclasses__(BaseHibernation):
            if subclass.__type__ == hibernation_type:
                return subclass(app, *args, **kwargs)
        raise ValueError(f"Hibernation {hibernation_type} not found")

    @staticmethod
    def all(_cls):
        return set(_cls.__type__).union(
            [s for c in _cls.__type__() for s in Hibernation.__all_subclasses__(c)]
        )
