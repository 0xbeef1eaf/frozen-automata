from dataclasses import dataclass
from enum import Enum
import json
import logging
from pathlib import Path
from re import S
import sys
from types import SimpleNamespace
from platformdirs import PlatformDirs

class Config(SimpleNamespace):
    _config_path = Path(PlatformDirs("Frozen Automata", "0xbeef1eaf", ensure_exists=True).user_config_dir).joinpath("config.json")
    _user_data_path = Path(PlatformDirs("Frozen Automata", "0xbeef1eaf", ensure_exists=True).user_data_dir)
    def __init__(self):
        self.logger = logging.getLogger("Config")
        self._config = {
            "password_hash": "",
            "timer": {
                "loop": 0.1,
                "startup": 5,
                "runtime": 60*60
            },
            "windows": {
                "startup": {
                    "enabled": True,
                    "transparency": 0.5,
                    "image": "",
                    "timeout": 5,
                },
                "popup": {
                    "enabled": True,
                    "transparency": {
                        "min": 0.5,
                        "max": 0.8
                    },
                    "probability": 0.5,
                    "timeout": {
                        "min": 5,
                        "max": 10
                    },
                    "close_on_click": False,
                    "mitosis": {
                        "enabled": True,
                        "probability": 0.5,
                    }
                },
                "prompt": {
                    "enabled": True,
                    "mistakes": 3,
                    "repetition": 5,
                    "probability": 0.2,
                    "image": {
                        "enabled": True,
                        "animate": True
                    }
                }
            },
            "pack": {
                "name": "default",
                "author": "default",
                "description": "default",
                "version": "0.0.0",
                "url": "",
                "password": "random_password_to_decrypt_media"
            },
            "panic": {
                "key": "ctrl+alt+end", # Panic key, bind to close the program
                "enabled": True,
            },
            "paths": {}
        }

        if not self._config_path.exists():
            self.logger.info(f"Config file not found, creating one at {self._config_path}")
            self._config_path.write_text(json.dumps(self._config, indent=4))
        self._config = json.loads(self._config_path.read_text(), object_hook=lambda d: SimpleNamespace(**d))
        self.logger.info("Config loaded")

        if getattr(sys, "_MEIPASS", False):
            self.logger.info("Running in a PyInstaller bundle")
            self._config.paths.resources = Path(sys._MEIPASS).joinpath("resources") # type: ignore
        else:
            self._config.paths.resources = Path(__file__).parent.parent.parent.joinpath("resources")
        self._config.paths.pack = self._user_data_path.joinpath("packs").joinpath(self._config.pack.name)
        self._config.paths.config = self._config_path

    def __getattr__(self, name):
        return getattr(self._config, name)


