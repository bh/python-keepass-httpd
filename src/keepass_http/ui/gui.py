# -*- coding: utf-8 -*-
from __future__ import print_function

import logging
import Tkinter
import tkMessageBox
import ttk

from keepass_http.backends import WrongPassword
from keepass_http.core import Conf

log = logging.getLogger(__name__)

class CenteredWindowMixIn(object):  # pragma: no cover
    def center(self):
        self.update_idletasks()
        width = self.winfo_width()
        frm_width = self.winfo_rootx() - self.winfo_x()
        win_width =  width + 2 * frm_width
        height = self.winfo_height()
        titlebar_height = self.winfo_rooty() - self.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = self.winfo_screenwidth() // 2 - win_width // 2
        y = self.winfo_screenheight() // 2 - win_height // 2
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        if self.attributes('-alpha') == 0:
            self.attributes('-alpha', 1.0)
        self.deiconify()

class RequireAssociationDecision(CenteredWindowMixIn, Tkinter.Tk):  # pragma: no cover

    @classmethod
    def require_client_name(cls):
        gui = cls()
        gui.center()
        gui.mainloop()
        gui.destroy()
        return gui._client_name

    def __init__(self):
        Tkinter.Tk.__init__(self)
        self.setup_frame_1()
        self.title("Setup new connection with browser")
        self._client_name = None

    def setup_frame_1(self):
        self._frame_1 = frame = ttk.Frame(self)
        frame.style = ttk.Style()
        frame.style.theme_use("default")

        frame.pack(anchor=Tkinter.CENTER, expand=Tkinter.YES)

        label = ttk.Label(frame, text="Create a new association with the browser?")
        label.grid(row=0, column=0, rowspan=1, pady=10, padx=10, columnspan=2)

        button_1 = ttk.Button(frame, text="Yes", command=self.accept_client)
        button_1.grid(row=1, column=0, ipadx=20, padx=0, pady=10)

        button_2 = ttk.Button(frame, text="No", command=self.quit)
        button_2.grid(row=1, column=1, ipadx=20, padx=0, pady=10)

    def setup_frame_2(self):
        self._frame_2 = frame = ttk.Frame(self)
        frame.style = ttk.Style()
        frame.style.theme_use("default")

        frame.pack(anchor=Tkinter.CENTER, expand=Tkinter.YES)

        label = ttk.Label(frame, text="Enter a name for the new connection:")
        label.grid(row=0, column=0, pady=10, padx=10, columnspan=2)

        entry = ttk.Entry(frame, width=27)
        entry.grid(row=1, column=0, pady=10, columnspan=2)

        button_1 = ttk.Button(frame, text="OK", command=lambda: self.name_entered(entry.get()))
        button_1.grid(row=2, column=0, ipadx=20, padx=0, pady=10, rowspan=1)

        button_2 = ttk.Button(frame, text="Cancel", command=self.quit)
        button_2.grid(row=2, column=1, columnspan=1, ipadx=20, padx=0, pady=10, rowspan=1)

    @staticmethod
    def validate_clientname(name):
        # TODO: needs more checks (special chars etc.)
        return name.strip() != ""

    def name_entered(self, client_name):
        if self.validate_clientname(client_name):
            self._client_name = client_name
            self.quit()
        else:
            should_retry = tkMessageBox.askretrycancel(title="invalid name",
                                                       message="The name you enterd is not valid.")
            if not should_retry:
                self._client_name = None
                self.quit()

    def accept_client(self):
        self._frame_1.destroy()
        self.setup_frame_2()
        self._frame_2.grid()


class OpenDatabase(CenteredWindowMixIn, Tkinter.Tk):  # pragma: no cover

    @classmethod
    def open(cls, max_try_count):
        success = False
        try_count = 1
        while try_count <= max_try_count:
            gui = cls()
            gui.center()
            gui.mainloop()
            gui.destroy()
            if gui._success is True:
                log.info("Passphrase accepted")
                success = True
                break
            if gui._success is None:
                break
            else:
                try_count += 1
                continue
        return success

    def __init__(self):
        Tkinter.Tk.__init__(self)
        self.kpconf = Conf()
        self._success = False
        self.setup_frame_1()
        self.title("Enter the passphrase for %s" % self.kpconf.backend.database_path)

    def setup_frame_1(self):
        self._frame_1 = frame = ttk.Frame(self)
        frame.style = ttk.Style()
        frame.style.theme_use("default")

        frame.pack(anchor=Tkinter.CENTER, expand=Tkinter.YES)

        entry = ttk.Entry(frame, width=27)
        entry.grid(row=1, column=0, pady=10, columnspan=2)
        entry.focus_set()

        button_1 = ttk.Button(frame, text="OK", command=lambda: self.passphrase_entered(entry.get()))
        button_1.grid(row=2, column=0, ipadx=20, padx=0, pady=10, rowspan=1)

        button_2 = ttk.Button(frame, text="Cancel", command=self.cancel)
        button_2.grid(row=2, column=1, columnspan=1, ipadx=20, padx=0, pady=10, rowspan=1)

    def passphrase_entered(self, passphrase):

        try:
            self.kpconf.backend.open_database(passphrase)
            self._success = True
            self.quit()
        except WrongPassword:
            self.quit()

    def cancel(self):
        self._success = None
        self._frame_1.destroy()
        self.quit()
