import logging
import random
from Levenshtein import distance
import tkinter
from typing import TYPE_CHECKING
from PIL import Image, ImageTk
import screeninfo
from activities import BaseActivity
from core.config.app import AppConfig
from pack.pack import Pack

if TYPE_CHECKING:
    from app import App


class PromptActivity(BaseActivity):
    __type__ = "prompt"

    def __init__(self, app: "App", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app
        self.logger = logging.getLogger(__name__)
        self.config = AppConfig()
        self.pack = Pack()
        self.root = tkinter.Toplevel(self.app.root)
        self.root.withdraw()
        self.root.wm_overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-toolwindow", True)

        max_size = (
            int(self.root.winfo_screenwidth() * 0.5),
            int(self.root.winfo_screenheight() * 0.5),
        )
        self.image = Image.open(random.choice(self.pack.image))
        self.image.thumbnail(max_size)
        self.image = ImageTk.PhotoImage(self.image)

        self.canvas = tkinter.Canvas(
            self.root,
            width=self.image.width(),
            height=self.image.height(),
            bd=0,
            highlightthickness=0,
        )

        self.canvas.create_image(
            self.image.width(),
            self.image.height(),
            image=self.image,
            anchor=tkinter.SE,
        )


        self.prompt = random.choice(self.pack.prompt)

        # Ensure the text is wrapped
        text = self.canvas.create_text(
            self.image.width() / 2,
            self.image.height() / 2,
            text=self.prompt,
            font=("Helvetica", 16),
            fill="white",
            justify=tkinter.CENTER,
            width=self.image.width() - 50,
            anchor=tkinter.CENTER,
            activefill="white"
        )

        text_dim = self.canvas.bbox(text)

        self.text_background = ImageTk.PhotoImage(
            Image.new(
                "RGBA", (text_dim[2] - text_dim[0] + 10, text_dim[3] - text_dim[1] + 10), (0, 0, 0, 128)
            )
        )
        self.canvas.create_image(
            (self.image.width() / 2, self.image.height() / 2),
            image=self.text_background,
            anchor=tkinter.CENTER,
        )
        self.canvas.text_background = self.text_background # type: ignore

        # Redraw the text on top of the background
        text = self.canvas.create_text(
            self.image.width() / 2,
            self.image.height() / 2,
            text=self.prompt,
            font=("Helvetica", 16),
            fill="white",
            justify=tkinter.CENTER,
            width=self.image.width() - 50,
            anchor=tkinter.CENTER,
            activefill="white"
        )

        # Add an entry box for the user to write the line in
        self.entry = tkinter.Entry(self.canvas, width=50, justify=tkinter.CENTER)

        if self.config.prompt.track.should():
            self.entry.bind("<Key>", self._on_keypress)
        else:
            self.entry.bind("<Return>", self._on_attempt)

        self.canvas.create_window(
            self.image.width() / 2,
            self.image.height() / 2 + 50,
            window=self.entry,
            anchor=tkinter.CENTER,
        )
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

        self.canvas.pack()
        self.root.update()
        self.root.deiconify()
        self.entry.focus_set()
        self.root.focus_force()

    def _on_keypress(self, event):
        """
        Check if the entry is correct so far, else wipe it
        """
        attempt = self.entry.get()
        prompt = self.prompt[: len(attempt)]
        if attempt != prompt:
            self.entry.delete(0, tkinter.END)
            self.entry.config(bg="red")
            self.root.after(100, lambda: self.entry.config(bg="white"))
        elif attempt == self.prompt:
            self.stop()


    def _on_attempt(self, event):
        mistakes = self.config.prompt.mistakes.random()
        if (
            distance(
                self.entry.get().strip(),
                self.prompt.strip(),
                score_cutoff=mistakes,
            )
            > mistakes
        ):
            self.entry.config(bg="red")
            self.root.after(100, lambda: self.entry.config(bg="white"))
            self.entry.delete(0, tkinter.END)
            if self.config.prompt.mitosis.should():
                self.logger.info("Launching mitosis")
                for _ in range(self.config.prompt.mitosis.random()):
                    self.app.launch("prompt")
        else:
            self.stop()

    def stop(self):
        self.root.destroy()
