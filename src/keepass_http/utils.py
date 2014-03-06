import errno
import logging.config
import os
import shutil
import sys

import pkg_resources


# http://stackoverflow.com/a/3041990
def query_yes_no(question, default="yes"):  # pragma: no cover
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes": "yes", "y": "yes", "ye": "yes",
             "no": "no", "n": "no"}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def is_pytest_running():
    return hasattr(sys, "_pytest_is_running")


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class ConfDir(object):
    logging_initialzed = False

    def __init__(self):
        if is_pytest_running():
            import tempfile
            self.dir = tempfile.mkdtemp()
        else:
            self.dir = os.path.expanduser("~/.python-keepass-httpd")
        self.logdir = os.path.join(self.dir, "log")
        mkdir_p(self.dir)
        mkdir_p(self.logdir)

    def initialize_logging(self, level=None):
        if not ConfDir.logging_initialzed:
            logging_conf = os.path.join(self.dir, "logging.conf")
            ConfDir.logging_initialzed = True

            # create basic logging config
            if not os.path.exists(logging_conf):
                logging_template = pkg_resources.resource_filename(__name__, "conf/logging.conf")
                shutil.copy(logging_template, logging_conf)

            logging.config.fileConfig(logging_conf, disable_existing_loggers=True,
                                      defaults={"LOGGING_DIR": self.logdir})

            if level:
                self.set_loglevel(level)

            log = logging.getLogger(__name__)
            log.debug("Logging conf read from: %s" % logging_conf)

            if level:
                log.debug("Set loglevel to: %s" % level)

    @staticmethod
    def set_loglevel(level):
        """
        Set the loglevel for all registered logging handlers.

        """
        for handler in logging._handlerList:
            handler = handler()
            handler.setLevel(level)

    @staticmethod
    def get_logging_handler_streams():
        """
        Return all open file handlers for logging stream loggers.
        This is used to avoid closing open file handlers while detaching to background.

        """
        return [handler().stream for handler in logging._handlerList]
