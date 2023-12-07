import logging
import random
import tkinter
from typing import TYPE_CHECKING

import screeninfo
from activities import BaseActivity
from core.config.app import AppConfig
from pack.pack import Pack
from PIL import Image, ImageTk, ImageFilter


if TYPE_CHECKING:
    from app import App

class GifActivity(BaseActivity):
    __type__ = "gif"

    def __init__(self, app: 'App'):
        # Same as ImageActivity, but with a gif so that it is animated and loops
        self.pack = Pack()
        self.config = AppConfig()
        self.logger = logging.getLogger(__name__)
        # Should we set a timeout?
        if self.config.gif.timeout.minimum + self.config.gif.timeout.maximum > 0:
            timeout = self.config.gif.timeout.random()
        else:
            timeout = 0
        super().__init__(app, timeout=timeout)
        self.root = tkinter.Toplevel(self.app.root)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-toolwindow", True)
        self.root.attributes("-alpha", self.config.gif.alpha.random()/100.0)
        self.root.withdraw()

        self.image = Image.open(random.choice(self.pack.gif))
        # extract the frames from the image
        self.frames = []
        try:
            while True:
                self.frames.append(self.image.copy())
                self.image.seek(len(self.frames))  # skip to next frame
        except EOFError:
            pass
        # resize the frames
        [frame.thumbnail((int(self.root.winfo_screenwidth() * 0.3), int(self.root.winfo_screenheight() * 0.3))) for frame in self.frames]

        # Check if we should add an image overlay (censor)
        if self.config.gif.censor.should():
            # Add the Image filter
            filter = random.choice([
                ImageFilter.GaussianBlur(radius=10),
                ImageFilter.BoxBlur(radius=10),
                ImageFilter.GaussianBlur(radius=2),
                ImageFilter.BoxBlur(radius=2)
            ])
            self.frames = [frame.filter(filter) for frame in self.frames]
        
        self.image = ImageTk.PhotoImage(self.frames[0])
        self.canvas = tkinter.Canvas(
            self.root,
            width=self.image.width(),
            height=self.image.height(),
            bd=0,
            highlightthickness=0,
        )
        # Pack the canvas and start the activity
        self.canvas.create_image(0, 0, anchor=tkinter.NW, image=self.image)
        self.canvas.pack()

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
        self.root.geometry(f"+{x}+{y}")

        # Should we add a button?
        if self.config.gif.button:
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
        
        self.root.deiconify()
        
        # Start the animation
        self._animate(0)

    def _animate(self, frame):
        self.image.paste(self.frames[frame])
        self.canvas.itemconfig(self.canvas.find_all()[0], image=self.image)
        self.root.after(int(1000/30), lambda: self._animate((frame + 1) % len(self.frames)))
    
    def _on_close_request(self):
        # If the user tries to close the window, we should stop the activity, or should we mess with them?
        if self.config.image.mitosis.should():
            for _ in range(self.config.image.mitosis.random()):
                self.app.launch("gif")
        if self.config.image.denial.should():
            return
        else:
            self.stop()
    
    def stop(self):
        self.root.after(0, self.root.destroy)
        super().stop()