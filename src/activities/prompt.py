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

        self.text_background = Image.new(
            "RGBA", (self.image.width(), self.image.height() // 4)
        )
        self.canvas.create_image(
            self.image.width() / 2,
            self.image.height() / 2,
            image=ImageTk.PhotoImage(self.text_background),
            anchor=tkinter.SE,
        )
        self.prompt = random.choice(self.pack.prompt)
        # Ensure the text is wrapped
        self.canvas.create_text(
            self.image.width() / 2,
            self.image.height() / 2,
            text=self.prompt,
            font=("Helvetica", 16),
            fill="white",
            justify=tkinter.CENTER,
            width=self.image.width() - 50,
        )

        # Add an entry box for the user to write the line in
        self.entry = tkinter.Entry(self.canvas)
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

    def _on_attempt(self, event):
        mistakes = self.config.prompt.mistakes.random()
        if (
            distance(
                self.entry.get().lower().strip(),
                self.prompt.lower().strip(),
                score_cutoff=mistakes,
            )
            > mistakes
        ):
            self.entry.config(bg="red")
            self.root.after(100, lambda: self.entry.config(bg="white"))
            self.entry.delete(0, tkinter.END)
        else:
            self.stop()

    def stop(self):
        self.root.destroy()
