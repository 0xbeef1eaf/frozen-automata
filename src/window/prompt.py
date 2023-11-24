from calendar import c
import hashlib
import os
from pathlib import Path
import random
import tkinter
from typing import Optional

from screeninfo import get_monitors
from window import AbstractBaseWindow
from PIL import Image, ImageTk


class PromptWindow(AbstractBaseWindow):
    __type__ = "prompt"
    def __init__(self, *args,  message: str, repeat: int, image: Optional[Path|str], title: Optional[str] = None, password= False, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message
        self.repeat = repeat

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg="black")
        self.focus()

        max_size = int(self.winfo_screenwidth()/2), int(self.winfo_screenheight()/2)
        
        
        size = max_size
        _image = None

        if image:
            _image = Image.open(image)
            _image.thumbnail(max_size, resample=Image.LANCZOS)
            size = _image.size
        
        canvas = tkinter.Canvas(self, width=size[0], height=size[1])
        canvas.pack()

        if _image:
            _image = ImageTk.PhotoImage(_image)
            canvas.create_image(0, 0, anchor=tkinter.NW, image=_image)
            canvas.background = _image # type: ignore
        
        if title:
            title_label = tkinter.Label(canvas, text=title, wraplength=int(size[0]*0.8))
            canvas.create_window(size[0]/2, int(size[1]*0.1), anchor=tkinter.N, window=title_label)
        
        if self.repeat > 1:
            self.to_copy = tkinter.Label(canvas, text=f'{self.message} ({self.repeat} left)')
        else:
            self.to_copy = tkinter.Label(canvas, text=f'{self.message}')
        canvas.create_window(size[0]/2, size[1]/2, anchor=tkinter.CENTER, window=self.to_copy)

        # The box for the user to write out the line into
        self.line = tkinter.Entry(canvas)
        canvas.create_window(size[0]/2, size[1]*0.9, anchor=tkinter.S, window=self.line)

        if password:
            self.bind("<Return>", lambda _: self.check_password(self.line.get()))
        else:
            self.bind("<Return>", lambda _: self.submit(self.line.get()))

        monitors = get_monitors()
        if monitors:
            monitor = random.choice(monitors)
            x = monitor.x + random.randint(0, monitor.width - size[0])
            y = monitor.y + random.randint(0, monitor.height - size[1])
            self.geometry(f"{size[0]}x{size[1]}+{x}+{y}")
        else:
            self.geometry(f"{size[0]}x{size[1]}+{random.randint(0, self.winfo_screenwidth() - size[0])}+{random.randint(0, self.winfo_screenheight() - size[1])}")

    def submit(self, line: str):
        # Check if the line is correct
        # If it is, but they need to repeat, repeat
        # If it is, and they don't need to repeat, close
        if self.message == line:
            if self.repeat > 1:
                # Clear the Entry
                self.line.delete(0, tkinter.END)
                # Update the label
                self.to_copy.config(text=f'{self.message} ({self.repeat-1} left)')
                # Decrement the repeat
                self.repeat -= 1
            else:
                self.after(0, self.destroy)
        else:
            # Clear the Entry
            self.line.delete(0, tkinter.END)
            # Flash the Entry background red
            self.line.config(bg='red')
            # Wait 0.1 seconds
            self.after(100, lambda: self.line.config(bg='white'))
    
    def check_password(self, line: str):
        self.attempts = getattr(self, 'attempts', 0) + 1
        if self.owner.config.password_hash == hashlib.sha256(line.encode()).hexdigest():
            self.owner.quit(self.owner.icon, None)
        else:
            # Clear the Entry
            self.line.delete(0, tkinter.END)
            # Flash the Entry background red
            self.line.config(bg='red')
            # Wait 0.1 seconds
            self.after(100, lambda: self.line.config(bg='white'))
            for _ in range(self.attempts):
                self.owner.spawn_window(
                    'popup',
                    timeout=random.uniform(self.owner.config.windows.popup.timeout.min, self.owner.config.windows.popup.timeout.max)
                )

            

            
        