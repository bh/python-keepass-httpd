# -*- coding: utf-8 -*-

import logging
import os
import sys
from functools import partial

from PySide import QtCore, QtGui, QtUiTools

from keepass_http.backends import WrongPassword
from keepass_http.core import Conf
from keepass_http.utils import get_absolute_path_to_resource

log = logging.getLogger(__name__)


def _get_app():  # pragma: no cover
    try:
        app = QtGui.QApplication(sys.argv)
    except RuntimeError:
        # RuntimeError: A QApplication instance already exists.
        app = QtCore.QCoreApplication.instance()
    return app


def _read_ui_file(path, parent):  # pragma: no cover
    """
    Read a *.ui file in src/keepass_http/conf and return the root widget as QT object
    defined in ui file.

    """

    ui_file_path = get_absolute_path_to_resource(os.path.join("conf", path))

    ui_file_obj = QtCore.QFile(ui_file_path)
    ui_file_obj.open(QtCore.QFile.ReadOnly)

    loader = QtUiTools.QUiLoader()
    widget = loader.load(ui_file_obj, parent)

    ui_file_obj.close()
    return widget


class RequireDatabasePassphraseUi(QtGui.QMainWindow):  # pragma: no cover

    def __init__(self, *args, **kwargs):
        QtGui.QMainWindow.__init__(*(self,) + args)
        # set success to True if the passphrase was correct and we are now connected to
        # the keepassdatabase.
        self._success = None

        self.ui = _read_ui_file("require_passphrase.ui", self)

        self.setCentralWidget(self.ui)
        self.ui.passphrase.setFocus()
        self.ui.passphrase.returnPressed.connect(self.try_authenticate)

        self.ui.buttons.accepted.connect(self.try_authenticate)
        self.ui.buttons.rejected.connect(partial(self._exit, False))

    def try_authenticate(self, *args):
        passphrase = self.ui.passphrase.text()
        try:
            Conf().backend.open_database(passphrase)
        except WrongPassword:
            statusbar = self.ui.statusBar()
            msg = "Wrong passphrase, try again please."
            statusbar.showMessage(msg)
            log.warning(msg)
        else:
            log.info("Passphrase %s accepted" % ("*" * len(passphrase)))
            self._exit(True)

    def _exit(self, success):
        self._success = success
        self.ui.close()

    @classmethod
    def do(cls, unused_try_count):
        app = _get_app()
        window = cls()
        window.ui.show()
        window.activateWindow()
        app.exec_()
        return window._success


class ClientConnectDecisionUi(QtGui.QMainWindow):  # pragma: no cover

    def __init__(self, *args, **kwargs):
        QtGui.QMainWindow.__init__(*(self,) + args)
        # save the entered client name for further processing
        self._client_name = None

        self.baseui = _read_ui_file("client_connect.ui", self)

        self.dialog = _read_ui_file("should_connect_dialog.ui", self)
        self.dialog.finished.connect(self.should_connect_with_client)

    def should_connect_with_client(self, decision):
        if decision == QtGui.QDialog.Accepted:
            self.baseui.show()
            self.baseui.client_name.setFocus()
            self.baseui.client_name.returnPressed.connect(self.name_entered)

            self.baseui.buttons.accepted.connect(self.name_entered)
            self.baseui.buttons.rejected.connect(self._exit)
        else:
            self._exit()

    def _exit(self):
        self.baseui.close()

    def name_entered(self, *args):
        self._client_name = self.baseui.client_name.text()
        self._exit()

    @classmethod
    def do(cls):
        app = _get_app()
        window = cls()
        window.dialog.show()
        window.activateWindow()
        app.exec_()
        return window._client_name
