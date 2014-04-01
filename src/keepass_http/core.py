# -*- coding: utf-8 -*-
import logging.config
import mimetypes
import os.path

from keepass_http.utils import get_absolute_path_to_resource, is_pytest_running, mkdir_p, Singleton


class Conf(Singleton):

    def __init__(self):
        self.configure_paths()
        self.configure_mimetypes()

    @staticmethod
    def configure_mimetypes():
        """
        Register keepass mimetypes.

        """
        mimetypes.add_type("application/x-keepass-database-v1", ".kdb")
        mimetypes.add_type("application/x-keepass-database-v2", ".kdbx")

    def configure_paths(self):
        if is_pytest_running():
            import tempfile
            self.confdir = tempfile.mkdtemp()
        else:
            self.confdir = os.path.expanduser("~/.python-keepass-httpd")  # pragma: no cover
        self.logdir = os.path.join(self.confdir, "log")
        mkdir_p(self.confdir)
        mkdir_p(self.logdir)

    @staticmethod
    def set_loglevel(level):
        """
        Set the loglevel for all registered logging handlers.

        """
        for handler in logging._handlerList:
            handler = handler()
            handler.setLevel(level)


logging_template = get_absolute_path_to_resource("conf/logging.conf")
logging.config.fileConfig(logging_template, disable_existing_loggers=True,
                          defaults={"LOGGING_DIR": Conf().logdir})
