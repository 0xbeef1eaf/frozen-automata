import logging
import time
from typing import TYPE_CHECKING
from core.config.app import AppConfig
from hibernate import BaseHibernation

if TYPE_CHECKING:
    from app import App


class DefaultHibernation(BaseHibernation):
    __type__ = "default"

    def __init__(self, app: "App"):
        self.config = AppConfig()
        self.app = app
        self.logger = logging.getLogger(__name__)

    def sleep(self):
        """
        Sleeps the thread for a set amount of time to determine the tick rate.
        """
        _time = (
            self.config.hibernate.timer.random()
            / self.config.hibernate.activity.random()
        )
        self.logger.debug(f"Sleeping for {_time} seconds")
        time.sleep(_time)
