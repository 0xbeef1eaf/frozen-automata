import tkinter
import tkinter.ttk
from typing import TYPE_CHECKING
from activities import BaseActivity, panic
from core.config.app import AppConfig
from pack.pack import Pack

if TYPE_CHECKING:
    from app import App


class ConfigurationActivity(BaseActivity):
    __type__ = "configuration"

    def __init__(self, app: 'App'):
        self.root = tkinter.Toplevel(app.root)
        self.root.title("Configuration")
        self.root.geometry("800x600")

        self.app = app
        self.config = AppConfig()
        self.pack = Pack()
        self.notebook = tkinter.ttk.Notebook(self.root)
        
        # Save on 
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_request)

        # Add the tabs
        self.notebook.add(self._general_tab(), text="General")

        self.notebook.pack(expand=1, fill="both")

    
    def _on_close_request(self):
        """
            Called when the user requests to close the window.
        """
        self.root.destroy()
        self.config.save()

        # Restart the app
        self.app.stop()

    def _general_tab(self):
        """
            The general tab, containing information around the app, and allowing the user to configure base settings.
        """
        tab = tkinter.Frame(self.notebook)

        # Panic Group
        panic_group = tkinter.LabelFrame(tab, text="Panic")
        # Panic Keychord
        panic_keychord_var = tkinter.StringVar(value=self.config.panic.keychord)
        panic_keychord_label = tkinter.Label(panic_group, text="Keychord")
        panic_keychord_entry = tkinter.Entry(panic_group, textvariable=panic_keychord_var)
        panic_keychord_label.grid(row=0, column=0)
        panic_keychord_entry.grid(row=0, column=1)

        # Panic Password
        panic_password_var = tkinter.StringVar()
        panic_password_label = tkinter.Label(panic_group, text="Password")
        panic_password_entry = tkinter.Entry(panic_group, textvariable=panic_password_var)
        panic_password_label.grid(row=1, column=0)
        panic_password_entry.grid(row=1, column=1)

        # Panic Password Confirm
        panic_password_confirm_var = tkinter.StringVar()
        panic_password_confirm_label = tkinter.Label(panic_group, text="Confirm Password")
        panic_password_confirm_entry = tkinter.Entry(panic_group, textvariable=panic_password_confirm_var)
        panic_password_confirm_label.grid(row=2, column=0)
        panic_password_confirm_entry.grid(row=2, column=1)

        panic_group.pack()

        return tab

