
import pytest

from keepass_http.backends import (get_backend_by_file, KeePassHTTPBackend,
                                   NoBackendError)


def test_get_backend_by_mimetype():
    assert get_backend_by_file("foo.kdb") is KeePassHTTPBackend

    with pytest.raises(NoBackendError):
        get_backend_by_file("eggs.kdbx")

    with pytest.raises(NoBackendError):
        get_backend_by_file("/tmp/foo.gif")
