from cProfile import label
import random
import threading
import time
import tkinter
from typing import Literal
from window import AbstractBaseWindow
from PIL import Image, ImageTk
from screeninfo import get_monitors

IMAGE_EXTS = ["png", "jpg", "jpeg", "gif", "bmp", "ico", "tiff", "webp"]

class PopupWindow(AbstractBaseWindow):
    __type__ = "popup"

    def __init__(self, *args, timeout: int = 0, **kwargs):
        super().__init__(*args, **kwargs)
        max_size = (
            int(self.winfo_screenwidth()/3), int(self.winfo_screenheight()/3)
        )
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        # Load media from the pack
        image = Image.open(random.choice([image for image in self.owner.config.paths.pack.glob(f"images/*") if image.suffix[1:] in IMAGE_EXTS]))
        image.thumbnail(max_size, resample=Image.LANCZOS)
        # Choose a random image
        media = ImageTk.PhotoImage(image)
        # Show the image
        label = tkinter.Label(self, image=media)
        label.image = media # type: ignore
        label.pack()
        self.maxsize(*max_size)

        monitors = get_monitors()
        if monitors:
            monitor = random.choice(monitors)
            x = monitor.x + random.randint(0, monitor.width - image.width)
            y = monitor.y + random.randint(0, monitor.height - image.height)
            self.geometry(f"+{x}+{y}")
        else:
            self.geometry(f"+{random.randint(0, self.winfo_screenwidth() - image.width)}+{random.randint(0, self.winfo_screenheight() - image.height)}")
        
        self.attributes('-alpha', random.uniform(self.owner.config.windows.popup.transparency.min, self.owner.config.windows.popup.transparency.max))

        self.bind('<<Timeout>>', lambda e: self.destroy())
        self.bind('<Button-1>', lambda e: self.owner.config.windows.popup.close_on_click and self.close())

        if timeout > 0:
            self.timeout = threading.Thread(target=self.timer, args=(timeout,))
            self.timeout.start()
    
    def close(self):
        if self.owner.config.windows.popup.mitosis.enabled:
            # spawn popups based on the probability
            rand = random.random()
            mitosis = self.owner.config.windows.popup.mitosis.probability
            self.owner.logger.info(f"Mitosis: {rand} < {self.owner.config.windows.popup.mitosis.probability}")
            while rand < mitosis:
                self.owner.spawn_window("popup", timeout=random.uniform(self.owner.config.windows.popup.timeout.min, self.owner.config.windows.popup.timeout.max))
                mitosis -= max(rand, 0.1)
        self.destroy()


    def timer(self, timeout: int):
        time.sleep(timeout)
        try:
            self.event_generate("<<Timeout>>")
        except tkinter.TclError:
            pass

        
