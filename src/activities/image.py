import logging
import random
import tkinter
from typing import TYPE_CHECKING
from PIL import Image, ImageTk, ImageFilter
import screeninfo
from activities import BaseActivity
from core.config.app import AppConfig
from pack import Pack

if TYPE_CHECKING:
    from app import App


class ImageActivity(BaseActivity):
    """
    An activity that displays an image popup to the user.
    """

    __type__ = "image"

    def __init__(self, app: "App"):
        timeout = 0
        if app.config.image.timeout.minimum + app.config.image.timeout.maximum > 0:
            timeout = app.config.image.timeout.random()

        super().__init__(app, timeout=timeout)
        self.pack = Pack()
        self.config = AppConfig()
        self.logger = logging.getLogger(__name__)
        # Should we set a timeout?

        self.root = tkinter.Toplevel(self.app.root)

        self.image = Image.open(random.choice(self.pack.image))
        self.image.thumbnail(
            (
                int(self.root.winfo_screenwidth() * 0.3),
                int(self.root.winfo_screenheight() * 0.3),
            )
        )

        # Check if we should add an image overlay (censor)
        if self.config.image.censor.should():
            # Add the Image filter
            filter = random.choice([
                ImageFilter.GaussianBlur(radius=10),
                ImageFilter.BoxBlur(radius=10),
                ImageFilter.GaussianBlur(radius=2),
                ImageFilter.BoxBlur(radius=2)
            ])
            self.image = self.image.filter(filter)

        self.image = ImageTk.PhotoImage(self.image)

        self.canvas = tkinter.Canvas(
            self.root,
            width=self.image.width(),
            height=self.image.height(),
            bd=0,
            highlightthickness=0,
        )

        # Pack the canvas and start the activity
        self.canvas.create_image(0, 0, anchor=tkinter.NW, image=self.image)

        # Set the geometry of the window
        ## This should go over all monitors
        monitors = screeninfo.get_monitors()
        if monitors:
            monitor = random.choice(monitors)
            # Choose a random position on the monitor (so that all the image is visible)
            x = random.randint(
                monitor.x, monitor.x + monitor.width - self.image.width()
            )
            y = random.randint(
                monitor.y, monitor.y + monitor.height - self.image.height()
            )
        else:
            x = random.randint(0, self.root.winfo_screenwidth() - self.image.width())
            y = random.randint(0, self.root.winfo_screenheight() - self.image.height())
        self.root.geometry(f"{self.image.width()}x{self.image.height()}+{x}+{y}")

        # Should we add a button?
        if self.config.image.button:
            # Add the button to the canvas (bottom center)
            self.button = tkinter.Button(
                self.canvas,
                text=random.choice(self.pack.button),
                command=self._on_close_request,
            )
            self.canvas.create_window(
                self.image.width() / 2,
                self.image.height(),
                anchor=tkinter.S,
                window=self.button,
            )
        else:
            self.root.bind("<Button-1>", lambda _: self._on_close_request())

        self.canvas.pack()
        self.root.attributes("-alpha", self.config.image.alpha.random() / 100.0)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        # Set so that the window doesn't appear in the taskbar
        self.root.attributes("-toolwindow", True)

    def _on_close_request(self):
        # If the user tries to close the window, we should stop the activity, or should we mess with them?
        if self.config.image.mitosis.should():
            for _ in range(self.config.image.mitosis.random()):
                self.app.launch("image")
        elif self.config.image.denial.should():
            pass
        else:
            self.stop()

    def stop(self):
        self.root.after(0, self.root.destroy)
        super().stop()
        del self.image
