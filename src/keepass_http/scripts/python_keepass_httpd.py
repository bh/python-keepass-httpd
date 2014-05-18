#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Usage:
  python-keepass-httpd run <database_path> [options]
  python-keepass-httpd (-h | --help)
  python-keepass-httpd --version

Options:
  --help                        Show this screen
  -v --version                  Show version
  -d --daemon                   Start in daemon mode
  -p --port PORT                Specify a port [default: 19455]
  -h --host HOST                Specify a host [default: 127.0.0.1]
  -l --loglevel LOGLEVEL        Loglevel to use [default: INFO]
  -k --keyfile path_to_keyfile  Use a key file instead of a passhprase [default: None]
"""

import os
import sys
from functools import partial

import daemonize
import docopt

from keepass_http import backends
from keepass_http.core import Conf, logging
from keepass_http.httpd.server import app
from keepass_http.utils import get_logging_filehandlers_streams_to_keep, has_gui_support

MAX_TRY_COUNT = 3
APP_NAME = "keepass_http_script"
log = logging.getLogger(APP_NAME)


def main():
    # avoid: UnboundLocalError: local variable '__doc__' referenced before assignment
    doc_ = __doc__
    kpconf = Conf()

    if has_gui_support():
        doc_ += "  --gui".ljust(28) + "Use QT (PySide) for a graphical interface"

    # handle arguments
    arguments = docopt.docopt(doc_)

    is_daemon = arguments["--daemon"]
    database_path = arguments["<database_path>"]

    key_file = arguments["--keyfile"]
    print "x: %s" % key_file

    host = arguments["--host"]
    port = arguments["--port"]
    assert port.isdigit()
    loglevel = arguments["--loglevel"]

    gui = arguments.get("--gui", False)
    if gui:
        ui = Conf.UI.GUI
    else:
        ui = Conf.UI.CLI

    kpconf.select_ui(ui)
    kpconf.set_loglevel(loglevel)

    if not has_gui_support():
        log.debug("\nIt seems that you don't have GUI support installed. Install it with:\n"
                  "  $ pip install -e '.[GUI]'\n"
                  "or\n"
                  "  $ pip install keepass_http[GUI]\n")

    # backend
    backend = backends.BaseBackend.get_by_filepath(database_path)
    kpconf.set_backend(backend)

    success = kpconf.get_selected_ui().OpenDatabaseUi.do(MAX_TRY_COUNT)
    if success is False:
        sys.exit("Wrong or no passphrase")

    # config daemon
    run_server = partial(app.run, debug=False, host=host, port=int(port))
    if is_daemon:
        pid_file = os.path.join(kpconf.confdir, "process.pid")
        log.info("Server started as daemon on %s:%s" % (host, port))
        daemon = daemonize.Daemonize(app=APP_NAME,
                                     pid=pid_file,
                                     action=run_server,
                                     keep_fds=get_logging_filehandlers_streams_to_keep())
        daemon.start()

    else:
        log.info("Server started on %s:%s" % (host, port))
        run_server()

if __name__ == '__main__':
    main()
