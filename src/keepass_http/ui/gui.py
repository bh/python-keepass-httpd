# -*- coding: utf-8 -*-

import logging
import os
import sys
from functools import partial

from PySide import QtCore, QtGui, QtUiTools

from keepass_http.backends import UnableToOpenDatabase
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


class OpenDatabaseUi(QtGui.QMainWindow):  # pragma: no cover

    def __init__(self, *args, **kwargs):
        QtGui.QMainWindow.__init__(*(self,) + args)
        # set success to True if the passphrase was correct and we are now connected to
        # the keepassdatabase.
        self._success = None

        self.ui = _read_ui_file("open_database.ui", self)

        self.setCentralWidget(self.ui)

        self.ui.passphrase_group.toggled.connect(lambda x: self.ui.filepath_group.setChecked(not x))
        self.ui.filepath_group.toggled.connect(lambda x: self.ui.passphrase_group.setChecked(not x))

        self.ui.buttons.accepted.connect(self.try_authenticate)
        self.ui.buttons.rejected.connect(partial(self._exit, False))

        self.ui.select_keyfile.clicked.connect(self._key_file_selected)

    def _key_file_selected(self):
        file_path, unused = QtGui.QFileDialog.getOpenFileName(self, "Select Keepass Key File", "", )

        if file_path:
            self.ui.file_path.setText(file_path)

    def try_authenticate(self, *args):
        use_passphrase = self.ui.passphrase_group.isChecked()
        try:
            if use_passphrase:
                passphrase = self.ui.passphrase.text()
                Conf().backend.open_database(passphrase=passphrase)
            else:
                key_file = self.ui.file_path.text()
                Conf().backend.open_database(keyfile=key_file)

        except UnableToOpenDatabase:
            statusbar = self.ui.statusBar()
            msg = "Wrong %s, try again please." % ("password" if use_passphrase else "key file")
            statusbar.showMessage(msg)
            log.warning(msg)
        else:
            log.info("%s accepted" % ("Password" if use_passphrase else "Key file"))
            self._exit(True)

    def _exit(self, success):
        self._success = success
        self.ui.close()

    def _center_widgets(self):
        qr = self.ui.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.ui.move(qr.topLeft())

    @classmethod
    def do(cls, unused_try_count):
        app = _get_app()
        window = cls()
        window.ui.show()
        window._center_widgets()
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

    def _center_widgets(self):
        cp = QtGui.QDesktopWidget().availableGeometry().center()

        # base form
        qr = self.baseui.frameGeometry()
        qr.moveCenter(cp)
        self.baseui.move(qr.topLeft())

        # dialog
        qr = self.dialog.frameGeometry()
        qr.moveCenter(cp)
        self.dialog.move(qr.topLeft())

    @classmethod
    def do(cls):
        app = _get_app()
        window = cls()
        window.dialog.show()
        window._center_widgets()
        window.activateWindow()

        app.exec_()
        return window._client_name
