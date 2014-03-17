
import pytest

from keepass_http.backends import get_backend_by_file, NoBackendError
from keepass_http.backends.libkeepass_backend import KeePass2HTTPBackend
from keepass_http.backends.python_keepass_backend import KeePassHTTPBackend


def test_get_backend_by_mimetype():
    assert get_backend_by_file("foo.kdb") is KeePassHTTPBackend
    assert get_backend_by_file("foo.kdbx") is KeePass2HTTPBackend

    with pytest.raises(NoBackendError):
        get_backend_by_file("eggs.kdbfx")

    with pytest.raises(NoBackendError):
        get_backend_by_file("/tmp/foo.gif")
