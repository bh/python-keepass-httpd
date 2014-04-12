# -*- coding: utf-8 -*-
import pytest

from keepass_http.backends import (get_backend_by_file, libkeepass_backend, NoBackendError,
                                   python_keepass_backend)
from keepass_http.core import Conf


def test_get_backend_by_mimetype():
    Conf()
    assert get_backend_by_file("foo.kdb") is python_keepass_backend.Backend
    assert get_backend_by_file("foo.kdbx") is libkeepass_backend.Backend

    with pytest.raises(NoBackendError):
        get_backend_by_file("eggs.kdbfx")

    with pytest.raises(NoBackendError):
        get_backend_by_file("/tmp/foo.gif")
