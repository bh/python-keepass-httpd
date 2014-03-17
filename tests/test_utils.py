import logging

import mock

from keepass_http.utils import ConfDir


def test_confdir_init_logging():
    kpconf = ConfDir()
    ConfDir.logging_initialzed = False
    kpconf.initialize_logging()


@mock.patch.object(ConfDir, "set_loglevel")
def test_confdir_init_logging_with_Loglevel(mock_set_loglevel):
    kpconf = ConfDir()
    ConfDir.logging_initialzed = False
    kpconf.initialize_logging(logging.CRITICAL)
    mock_set_loglevel.assert_called_once_wirh(logging.CRITICAL)


def test_confdir_get_logging_handler_streams():
    kpconf = ConfDir()
    kpconf.get_logging_handler_streams()


def test_confdir_set_loglevel():
    kpconf = ConfDir()
    kpconf.set_loglevel(logging.ERROR)
