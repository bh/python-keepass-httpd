
import pytest

from keepass_http.backends import get_backend_by_file, NoBackendError, python_keepass_backend


def test_get_backend_by_mimetype():
    assert get_backend_by_file("foo.kdb") is python_keepass_backend.Backend

    with pytest.raises(NoBackendError):
        get_backend_by_file("foo.kdbx")

    with pytest.raises(NoBackendError):
        get_backend_by_file("eggs.kdbfx")

    with pytest.raises(NoBackendError):
        get_backend_by_file("/tmp/foo.gif")
