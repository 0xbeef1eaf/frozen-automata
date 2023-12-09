import logging
import tkinter
from typing import TYPE_CHECKING
from activities import BaseActivity
from core.config.app import AppConfig
from core.paths import Paths
from pack.pack import Pack
from PIL import Image, ImageTk
from passlib.hash import bcrypt

if TYPE_CHECKING:
    from app import App


class PanicActivity(BaseActivity):
    __type__ = "panic"

    def __init__(self, app: "App"):
        app.lock.acquire(blocking=True)
        timeout = 30  # 30 seconds to enter the password
        super().__init__(app, timeout=timeout)
        self.logger = logging.getLogger(__name__)
        self.config = AppConfig()
        self.pack = Pack()

        # Check if the password is set
        if not self.config.panic.password_hash:
            self.logger.warning("Panic password is not set, stopping.")
            self.app.stop()

        self.root = tkinter.Toplevel(self.app.root, bg="black")
        self.root.withdraw()
        self.root.attributes("-topmost", True)
        self.root.attributes("-toolwindow", True)
        self.root.overrideredirect(True)
        # Add _on_close_request to the close button
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_request)
        self.root.grab_set()

        max_size = (
            int(self.root.winfo_screenwidth() * 0.5),
            int(self.root.winfo_screenheight() * 0.5),
        )

        # Create a collage of the images
        self.image = Image.open(Paths.resources.joinpath("loading.png"))
        self.image.thumbnail(max_size)
        self.image = ImageTk.PhotoImage(self.image)

        self.canvas = tkinter.Canvas(
            self.root,
            width=self.image.width(),
            height=self.image.height(),
            bd=0,
            highlightthickness=0,
        )
        # Set to the center of the screen
        self.root.geometry(
            f"+{int(self.root.winfo_screenwidth() / 2 - self.image.width() / 2)}+{int(self.root.winfo_screenheight() / 2 - self.image.height() / 2)}"
        )

        self.canvas.create_image(0, 0, anchor="nw", image=self.image)
        self.canvas.background = (  # type: ignore
            self.image
        )  # Keep a reference to the image # type: ignore
        self.canvas.pack()
        # Add a background for just around the text (50% transparent black)
        ## Create the image (to allow for transparency)
        self.label_background = Image.new(
            "RGBA",
            (self.image.width(), 100),
            (0, 0, 0, 128),
        )
        self.label_background = ImageTk.PhotoImage(self.label_background)

        # Determine the position of the background, given the password prompt position on line 81

        self.canvas.create_image(0, 0, anchor="nw", image=self.label_background)

        # Show a password prompt
        self.canvas.create_text(
            self.image.width() / 2,
            50,
            text="Password (press escape to cancel)",
            font=("Helvetica", 16),
            fill="white",
            anchor="center",
        )

        self.password_var = tkinter.StringVar()
        self.prompt = tkinter.Entry(
            self.root, show="•", justify="center", textvariable=self.password_var
        )
        self.canvas.create_window(
            self.image.width() / 2,
            self.image.height() - 20,
            window=self.prompt,
        )
        self.root.update()
        self.root.deiconify()
        self.prompt.focus_set()
        self.prompt.bind("<Return>", lambda _: self._on_close_request())
        self.prompt.bind("<Escape>", lambda _: self.stop())
        self.canvas.pack()
        self.root.focus_force()
        self.prompt.focus_set()

    def _on_close_request(self):
        if bcrypt.verify(self.password_var.get(), self.config.panic.password_hash):
            self.root.withdraw()
            self.app.stop()
        else:
            self.logger.warning("Panic password is incorrect.")
            # Flash the entry boxpassword
            self.prompt.config(bg="red")
            self.root.after(100, lambda: self.prompt.config(bg="white"))
            # Clear the entry box
            self.password_var.set("")
            self.app.launch()

    def stop(self):
        self.root.destroy()
        self.app.lock.release()
        super().stop()
