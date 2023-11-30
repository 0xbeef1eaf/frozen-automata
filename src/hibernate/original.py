import logging
import time
from typing import TYPE_CHECKING
from core.config.app import AppConfig
from hibernate import BaseHibernation

if TYPE_CHECKING:
    from app import App


class OriginalHibernation(BaseHibernation):
    __type__ = "original"

    def __init__(self, app: "App"):
        self.config = AppConfig()
        self.app = app
        self.logger = logging.getLogger(__name__)
        self._activity = self.config.hibernate.activity.random()
        self.logger.debug(f"Set activity to {self._activity}")

    def sleep(self):
        """
        Sleeps the thread for a set amount of time to determine the tick rate.
        """
        # Yield to the main thread for the awaken amount
        if self._activity > 0:
            self.logger.info(f"Yielding for {self._activity} ticks")
            self._activity -= 1
            return
        _time = self.config.hibernate.timer.random()
        self.logger.info(f"Sleeping for {_time} seconds")
        time.sleep(_time)
        self._activity = self.config.hibernate.activity.random()
        self.logger.info(f"Reset activity to {self._activity}")
