# -*- coding: utf-8 -*-

import mock
import pytest

from keepass_http.utils import has_gui_support

if has_gui_support():
    from keepass_http.ui import gui
    from PySide import QtGui, QtCore


class TestBackend(mock.Mock):
    open_database = mock.Mock()


class TestConf(mock.Mock):
    backend = TestBackend()


skip_if_has_no_gui_support = pytest.mark.skipif(not has_gui_support(), reason="No GUI Support")


@skip_if_has_no_gui_support
def test_cancel(qtbot):
    window = gui.ClientConnectDecisionUi()

    window.dialog.show()
    qtbot.waitForWindowShown(window.dialog)

    buttons = window.dialog.buttons
    button_no = buttons.button(buttons.No)

    qtbot.mouseClick(button_no, QtCore.Qt.RightButton)

    assert window._client_name is None


@skip_if_has_no_gui_support
def test_should_connect(qtbot):
    window = gui.ClientConnectDecisionUi()

    # window.baseui.show()
    # no need to call the code commented code below, because
    # the widget will close itself.

    window.should_connect_with_client(1)

    qtbot.waitForWindowShown(window.baseui)

    window.baseui.client_name = mock.Mock()
    window.baseui.client_name.text.return_value = "chrome 01"

    buttons = window.baseui.buttons
    button_no = buttons.button(buttons.Ok)
    qtbot.mouseClick(button_no, QtCore.Qt.LeftButton)

    assert window._client_name == "chrome 01"
