from abc import ABC
import tkinter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import main

class AbstractBaseWindow(tkinter.Toplevel, ABC):
    __type__ = "base"
    
    def __init__(self, *args, owner: 'main.App', **kwargs):
        self.owner = owner
        super().__init__(*args, master=self.owner.root, **kwargs)
        self.title('Frozen Automata Base Window')
    

from .popup import PopupWindow
from .prompt import PromptWindow
from .startup import StartupWindow
# from .video import VideoPopup

class Window:
    def __new__(cls, _type: str, owner: 'main.App', *args, **kwargs) -> tkinter.Toplevel:
        def __all_subclasses__(cls):
            return set(cls.__subclasses__()).union(
                [s for c in cls.__subclasses__() for s in __all_subclasses__(c)]
            )

        matched_subclasses = [
            subclass
            for subclass in __all_subclasses__(AbstractBaseWindow)
            if subclass.__type__ == _type
        ]
        if len(matched_subclasses) == 0:
            raise ValueError(f"Invalid window type: {_type}")
        elif len(matched_subclasses) > 1:
            raise ValueError(
                f"Multiple subclasses of AbstractBaseWindow with type {_type}"
            )
        else:
            return matched_subclasses[0](*args, owner=owner, **kwargs)
