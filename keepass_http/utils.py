import logging
import logging.config
import sys

logger = logging.getLogger(__name__)

# TODO: better logging configuration

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            "format": '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
        "exception": {
            "format": "%(asctime)s %(levelname)-8s %(name)-16s %(message)s"
                      " [%(filename)s%(lineno)d in %(funcName)s]"
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            "formatter": "standard",
            'class': 'logging.StreamHandler',
        },
        'info_logger': {
            'level': 'INFO',
            "formatter": "standard",
            'class': 'logging.FileHandler',
            "filename": "/tmp/bla.log"
        },
        'error_logger': {
            'level': 'ERROR',
            "formatter": "exception",
            'class': 'logging.FileHandler',
            "filename": "/tmp/bla.error.log"
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'info_logger', "error_logger"],
            'level': 'INFO',
            'propagate': True
        }
    }
})


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
