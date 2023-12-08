from dataclasses import dataclass
import json
import logging
import random
from typing import Optional
from dataclasses_json import dataclass_json
import requests
from core import Singleton
from core.paths import Paths


@dataclass_json
@dataclass
class RangeType:
    minimum: int
    maximum: int

    def random(self):
        rand = random.randint(self.minimum, self.maximum)
        logging.debug(
            f"Generating random number between {self.minimum} and {self.maximum} = {rand}"
        )
        return rand

    def __post_init__(self):
        if self.minimum > self.maximum:
            raise ValueError("Minimum cannot be greater than maximum")


@dataclass_json
@dataclass
class ProbabilityType:
    enabled: bool
    probability: float

    def should(self):
        rand = random.random()
        logging.debug(
            f"Random number between 0 and 1 = {rand}, probability = {self.probability}"
        )
        return self.enabled and rand <= self.probability

    def __post_init__(self):
        if self.probability < 0 or self.probability > 1:
            raise ValueError("Probability must be between 0 and 1")


@dataclass_json
@dataclass
class ProbabilityRangeType:
    enabled: bool
    probability: float
    minimum: int
    maximum: int

    def should(self):
        rand = random.random()
        logging.debug(
            f"Random number between 0 and 1 = {rand}, probability = {self.probability}"
        )
        return self.enabled and rand <= self.probability

    def random(self):
        rand = random.randint(self.minimum, self.maximum)
        logging.debug(
            f"Generating random number between {self.minimum} and {self.maximum} = {rand}"
        )
        return rand

    def __post_init__(self):
        if self.probability < 0 or self.probability > 1:
            raise ValueError("Probability must be between 0 and 1")
        if self.minimum > self.maximum:
            raise ValueError("Minimum cannot be greater than maximum")

@dataclass_json
@dataclass
class GifActivityConfig:
    active: ProbabilityType = ProbabilityType(enabled=True, probability=0.05)
    alpha: RangeType = RangeType(minimum=50, maximum=100)
    timeout: RangeType = RangeType(minimum=5, maximum=30)
    mitosis: ProbabilityRangeType = ProbabilityRangeType(
        enabled=True, probability=0.5, minimum=2, maximum=5
    )
    denial: ProbabilityType = ProbabilityType(enabled=True, probability=0.5)
    censor: ProbabilityType = ProbabilityType(enabled=True, probability=0.1)
    button: bool = True

@dataclass_json
@dataclass
class ImageActivityConfig:
    active: ProbabilityType = ProbabilityType(enabled=True, probability=0.05)
    alpha: RangeType = RangeType(minimum=50, maximum=100)
    timeout: RangeType = RangeType(minimum=5, maximum=30)
    mitosis: ProbabilityRangeType = ProbabilityRangeType(
        enabled=True, probability=0.5, minimum=2, maximum=5
    )
    denial: ProbabilityType = ProbabilityType(enabled=True, probability=0.5)
    censor: ProbabilityType = ProbabilityType(enabled=True, probability=0.1)
    button: bool = True


@dataclass_json
@dataclass
class PromptActivityConfig:
    active: ProbabilityType = ProbabilityType(enabled=True, probability=0.05)
    mistakes: RangeType = RangeType(minimum=0, maximum=3)
    overlay: ProbabilityType = ProbabilityType(enabled=True, probability=0.5)
    mitosis: ProbabilityRangeType = ProbabilityRangeType(
        enabled=True, probability=0.5, minimum=2, maximum=5
    )


@dataclass_json
@dataclass
class WallpaperActivityConfig:
    active: ProbabilityType = ProbabilityType(enabled=True, probability=0.05)
    timer: RangeType = RangeType(minimum=30, maximum=60)
    current: str = ""

@dataclass_json
@dataclass
class WebActivityConfig:
    active: ProbabilityType = ProbabilityType(enabled=True, probability=0.05)
    private: ProbabilityType = ProbabilityType(enabled=True, probability=1.0)

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
    gif: GifActivityConfig = GifActivityConfig()
    prompt: PromptActivityConfig = PromptActivityConfig()
    wallpaper: WallpaperActivityConfig = WallpaperActivityConfig()
    web: WebActivityConfig = WebActivityConfig()

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
