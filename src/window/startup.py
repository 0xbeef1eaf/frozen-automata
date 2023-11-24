import threading
import time
import tkinter
import config
from window import AbstractBaseWindow
from PIL import Image, ImageTk

class StartupWindow(AbstractBaseWindow):
    __type__ = "startup"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(bg="black")
        self.frame = tkinter.Frame(self, borderwidth=2, relief=tkinter.RAISED)
        self.wm_attributes("-topmost", True)
        self.overrideredirect(True)

        height = self.winfo_screenheight()*0.5
        
        _image = Image.open(self.owner.config.paths.resources.joinpath("default/loading.png"))
        _image = _image.resize((int(height*(_image.width/_image.height)), int(height)), resample=Image.LANCZOS)
        image = ImageTk.PhotoImage(_image)
        
        self.geometry(f"{image.width()}x{image.height()}+{int(self.winfo_screenwidth()/2-image.width()/2)}+{int(self.winfo_screenheight()/2-image.height()/2)}")
        
        label = tkinter.Label(self, image=image)
        label.image = image # type: ignore
        label.pack()

        self.alpha = 0.0

        self.bind("<<Animate>>", lambda e: self.attributes('-alpha', self.alpha))
        threading.Thread(target=self.lifecycle).start()
    
    def lifecycle(self):
        # Animate the window fading in and out, should take config.timer.startup seconds
        ## This is split into x seconds for fading in, x*2 seconds for staying visible, and x seconds for fading out
        
        x = self.owner.config.timer.startup/4
        steps = 100

        while self.alpha < 1.0:
            self.alpha += 1/steps
            self.event_generate("<<Animate>>")
            time.sleep(x/steps)
        time.sleep(x*2)
        while self.alpha > 0.0:
            self.alpha -= 1/steps
            self.event_generate("<<Animate>>")
            time.sleep(x/steps)
        self.destroy()