from dataclasses import dataclass
from gc import enable
import json
import random
from tracemalloc import start

from dataclasses_json import dataclass_json
from core import Singleton
from core.paths import Paths


@dataclass_json
@dataclass
class RangeType:
    minimum: int
    maximum: int

    def random(self):
        return random.randint(self.minimum, self.maximum)

    def __post_init__(self):
        if self.minimum > self.maximum:
            raise ValueError("Minimum cannot be greater than maximum")


@dataclass_json
@dataclass
class ProbabilityType:
    enabled: bool
    probability: float

    def should(self):
        return self.enabled and random.random() <= self.probability

    def __post_init__(self):
        if self.probability < 0 or self.probability > 1:
            raise ValueError("Probability must be between 0 and 1")


@dataclass_json
@dataclass
class ImageActivityConfig:
    active: ProbabilityType = ProbabilityType(enabled=True, probability=0.05)
    alpha: RangeType = RangeType(minimum=50, maximum=100)
    timeout: RangeType = RangeType(minimum=5, maximum=30)
    overlay: ProbabilityType = ProbabilityType(enabled=True, probability=0.5)
    caption: ProbabilityType = ProbabilityType(enabled=True, probability=0.5)
    mitosis: ProbabilityType = ProbabilityType(enabled=True, probability=0.5)
    mitosis_count: RangeType = RangeType(minimum=2, maximum=5)
    denial: ProbabilityType = ProbabilityType(enabled=True, probability=0.5)
    button: bool = True


@dataclass_json
@dataclass
class AudioActivityConfig:
    active: ProbabilityType = ProbabilityType(enabled=True, probability=0.05)
    timeout: RangeType = RangeType(minimum=5, maximum=30)
    volume: RangeType = RangeType(minimum=50, maximum=100)


@dataclass_json
@dataclass
class VideoActivityConfig:
    active: ProbabilityType = ProbabilityType(enabled=True, probability=0.05)
    timeout: RangeType = RangeType(minimum=5, maximum=30)
    volume: RangeType = RangeType(minimum=50, maximum=100)
    button: bool = True
    denial: ProbabilityType = ProbabilityType(enabled=True, probability=0.5)
    mitosis: ProbabilityType = ProbabilityType(enabled=True, probability=0.5)
    alpha: RangeType = RangeType(minimum=50, maximum=100)


@dataclass_json
@dataclass
class PromptActivityConfig:
    active: ProbabilityType = ProbabilityType(enabled=True, probability=0.05)
    mistakes: RangeType = RangeType(minimum=0, maximum=3)
    overlay: ProbabilityType = ProbabilityType(enabled=True, probability=0.5)


@dataclass_json
@dataclass
class WallpaperActivityConfig:
    active: ProbabilityType = ProbabilityType(enabled=True, probability=0.05)
    timer: RangeType = RangeType(minimum=30, maximum=60)


@dataclass_json
@dataclass
class PanicConfig:
    keychord: str = "shift+escape"
    password_hash: str = (
        ""  # "$2b$12$76povxWTe.wP.F6.w/7enueNrqJkEKODRpd7ZtWA6Pts3V29YAjv." #password
    )


@dataclass_json
@dataclass
class HibernateConfig:
    strategy: str = "default"
    timer: RangeType = RangeType(minimum=30, maximum=60)
    activity: RangeType = RangeType(minimum=5, maximum=10)


@dataclass_json
@dataclass(init=True)
class AppConfig(metaclass=Singleton):
    debug: bool = False
    pack: str = "default"
    # startup: bool = True # Disabled until I can figure out how to make it work safely without triggering the antivirus (running as a .exe seems to trigger it)

    # App Timer
    timer: RangeType = RangeType(minimum=15, maximum=60)

    # Activities
    image: ImageActivityConfig = ImageActivityConfig()
    # audio: AudioActivityConfig = AudioActivityConfig()
    # video: VideoActivityConfig = VideoActivityConfig()
    prompt: PromptActivityConfig = PromptActivityConfig()
    wallpaper: WallpaperActivityConfig = WallpaperActivityConfig()

    # Hibernate
    hibernate: HibernateConfig = HibernateConfig()

    # Panic
    panic: PanicConfig = PanicConfig()

    def __post_init__(self):
        if self.timer.minimum > self.timer.maximum:
            raise ValueError("Minimum cannot be greater than maximum")
        self.save()

    @classmethod
    def load(cls):
        paths = Paths()
        if not paths.config.exists():
            cfg = AppConfig()
            cfg.save()
            return cfg
        with open(paths.config, "r") as f:
            return AppConfig.from_json(f.read())  # type: ignore

    def save(self):
        paths = Paths()
        with open(paths.config, "w") as f:
            json.dump(self.__dict__, f, indent=4, default=lambda o: o.__dict__)
