from dataclasses import dataclass
import sys
from platformdirs import PlatformDirs
from pathlib import Path

_dirs = PlatformDirs(
    appname="Frozen Automata", appauthor="0xbeef1eaf", ensure_exists=True
)


@dataclass
class Paths:
    packs: Path = Path(_dirs.user_data_dir).joinpath("packs")
    config: Path = Path(_dirs.user_config_dir).joinpath("config.json")
    resources: Path = (
        Path(sys._MEIPASS).joinpath("resources")
        if hasattr(sys, "_MEIPASS")
        else Path(__file__).parent.parent.parent.joinpath("resources")
    )
