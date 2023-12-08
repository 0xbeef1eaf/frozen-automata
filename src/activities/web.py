
import logging
from pathlib import Path
import platform
import random
from typing import TYPE_CHECKING
import browsers
from activities import BaseActivity
from core.config.app import AppConfig
from pack.pack import Pack

if TYPE_CHECKING:
    from app import App

_private_modes = {
    'firefox': ['--private-window'],
    'chrome': ['--incognito'],
    'edge': ['--inprivate'],
    'opera': ['--private'],
    'safari': ['--private'],
    'brave': ['--incognito'],
    'vivaldi': ['--incognito']
}


class WebActivity(BaseActivity):
    """
    Class to launch a web browser with a random URL from the pack
    """
    __type__ = "web"

    def __init__(self, app: 'App'):
        super().__init__(app, timeout=0)
        self.pack = Pack()
        self.config = AppConfig()
        self.logger = logging.getLogger(__name__)
        match platform.system():
            case "Windows":
                from winreg import HKEY_CLASSES_ROOT, HKEY_CURRENT_USER, OpenKey, QueryValueEx

                with OpenKey(HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice') as regkey:
                    # Get the user choice
                    browser_choice = QueryValueEx(regkey, 'ProgId')[0]

                with OpenKey(HKEY_CLASSES_ROOT, r'{}\shell\open\command'.format(browser_choice)) as regkey:
                    # Get the application the user's choice refers to in the application registrations
                    browser_path_tuple = QueryValueEx(regkey, None) # type: ignore

                    # This is a bit sketchy and assumes that the path will always be in double quotes
                    _browser = browser_path_tuple[0].split('"')[1]
            case _:
                raise ValueError("Unsupported operating system")
        # Get the browser's name
        browser_path = Path(_browser)
        browser_name = browser_path.stem
        # Check if the browser is supported
        if browser_name not in [b['browser_type'] for b in browsers.browsers()]:
            raise ValueError(f"Browser {browser_name} not supported")

        # Should we load in incognito mode?
        if self.config.web.private.should():
            self.logger.debug("Launching web browser in incognito mode")
            browsers.launch(browser_name, args=_private_modes[browser_name], url=random.choice(self.pack.web))
        else:
            browsers.launch(browser_name, url=random.choice(self.pack.web))
        