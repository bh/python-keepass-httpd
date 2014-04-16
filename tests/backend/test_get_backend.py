# -*- coding: utf-8 -*-
import pytest

from keepass_http.backends import (BaseBackend, libkeepass_backend, NoBackendError,
                                   python_keepass_backend)
from keepass_http.core import Conf


def test_get_backend_by_mimetype():
    Conf()

    assert isinstance(BaseBackend.get_by_filepath("foo.kdb"), python_keepass_backend.Backend)
    assert isinstance(BaseBackend.get_by_filepath("foo.kdbx"), libkeepass_backend.Backend)

    with pytest.raises(NoBackendError):
        BaseBackend.get_by_filepath("eggs.kdbfx")

    with pytest.raises(NoBackendError):
        BaseBackend.get_by_filepath("/tmp/foo.gif")
