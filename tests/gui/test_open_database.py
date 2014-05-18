# -*- coding: utf-8 -*-

import mock
import pytest

from keepass_http.backends import UnableToOpenDatabase
from keepass_http.utils import has_gui_support

if has_gui_support():
    from keepass_http.ui import gui
    from PySide import QtGui, QtCore


class TestBackend(mock.Mock):
    open_database = mock.Mock()


class TestConf(mock.Mock):
    backend = TestBackend()


skip_if_has_no_gui_support = pytest.mark.skipif(not has_gui_support(), reason="No QT Support")


@skip_if_has_no_gui_support
def test_require_ui_passphrase_correct(qtbot):
    with mock.patch("keepass_http.ui.gui.Conf", TestConf):
        window = gui.OpenDatabaseUi()

        window.ui.show()
        qtbot.addWidget(window.ui)

        qtbot.waitForWindowShown(window.ui)

        # password input field
        window.ui.passphrase = mock.Mock()
        window.ui.passphrase.text.return_value = "some passphrase"

        buttons = window.ui.buttons
        button_ok = buttons.button(buttons.Ok)

        with mock.patch.object(TestBackend, "open_database") as mock_open_database:
            qtbot.mouseClick(button_ok, QtCore.Qt.LeftButton)

            mock_open_database.assert_called_once_with(passphrase=u'some passphrase')
        assert window._success is True


@skip_if_has_no_gui_support
def test_require_ui_passphrase_incorrect(qtbot):
    with mock.patch("keepass_http.ui.gui.Conf", TestConf):
        window = gui.OpenDatabaseUi()

        window.ui.show()
        qtbot.addWidget(window.ui)

        qtbot.waitForWindowShown(window.ui)

        # password input field
        window.ui.passphrase = mock.Mock()
        window.ui.passphrase.text.return_value = "some passphrase"

        buttons = window.ui.buttons
        button_ok = buttons.button(buttons.Ok)

        with mock.patch.object(TestBackend, "open_database") as mock_open_database:
            # when calling open_database() than raise the UnableToOpenDatabase exception
            mock_open_database.side_effect = [UnableToOpenDatabase()]

            qtbot.mouseClick(button_ok, QtCore.Qt.LeftButton)

            mock_open_database.assert_called_once_with(passphrase=u'some passphrase')

        assert window._success is None


@skip_if_has_no_gui_support
def test_require_ui_passphrase_quit_or_cancel(qtbot):
    window = gui.OpenDatabaseUi()

    window.ui.show()
    qtbot.addWidget(window.ui)

    qtbot.waitForWindowShown(window.ui)

    buttons = window.ui.buttons
    button_ok = buttons.button(buttons.Cancel)

    qtbot.mouseClick(button_ok, QtCore.Qt.LeftButton)

    assert window._success is False
