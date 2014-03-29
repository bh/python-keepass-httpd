import logging.config
import os.path

from keepass_http.utils import get_absolute_path_to_resource, is_pytest_running, mkdir_p


class ConfDir(object):

    def __init__(self):
        if is_pytest_running():
            import tempfile
            self.confdir = tempfile.mkdtemp()
        else:
            self.confdir = os.path.expanduser("~/.python-keepass-httpd")  # pragma: no cover
        self.logdir = os.path.join(self.confdir, "log")
        mkdir_p(self.confdir)
        mkdir_p(self.logdir)


kpconf = ConfDir()

logging_template = get_absolute_path_to_resource("conf/logging.conf")
logging.config.fileConfig(logging_template, disable_existing_loggers=True,
                          defaults={"LOGGING_DIR": kpconf.logdir})
