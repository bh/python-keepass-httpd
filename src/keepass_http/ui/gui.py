# -*- coding: utf-8 -*-
from __future__ import print_function

import Tkinter
import tkMessageBox
import ttk


class RequireAssociationDecision(Tkinter.Tk):  # pragma: no cover

    @classmethod
    def require_client_name(cls):
        gui = cls()
        gui.geometry()
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


if __name__ == "__main__":  # pragma: no cover
    new_client_name = RequireAssociationDecision.require_client_name()
    print (new_client_name)
