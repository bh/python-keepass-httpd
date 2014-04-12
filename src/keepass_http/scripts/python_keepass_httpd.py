#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Usage:
  python-keepass-httpd run <database_path> [options]
  python-keepass-httpd (-h | --help)
  python-keepass-httpd --version

Options:
  --help                    Show this screen
  -v --version              Show version
  -d --daemon               Start in daemon mode
  -p --port PORT            Specify a port [default: 19455]
  -h --host HOST            Specify a host [default: 127.0.0.1]
  -l --loglevel LOGLEVEL    Loglevel to use [default: INFO]
"""

import getpass
import os
import sys

import daemonize
import docopt

from keepass_http import backends
from keepass_http.core import Conf, logging
from keepass_http.httpd.server import KeepassHTTPServer
from keepass_http.utils import get_logging_handler_streams, has_gui_support

APP_NAME = "keepass_http_script"
log = logging.getLogger(APP_NAME)


def main():
    # avoid: UnboundLocalError: local variable '__doc__' referenced before assignment
    doc_ = __doc__
    kpconf = Conf()

    if has_gui_support():
        doc_ += "  --gui                     Use TKinter for a graphical interface"

    # handle arguments
    arguments = docopt.docopt(doc_)

    is_daemon = arguments["--daemon"]
    database_path = arguments["<database_path>"]
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

    # server
    server = KeepassHTTPServer(host, int(port))
    server.set_is_daemon(is_daemon)
    # backend
    backend_class = backends.get_backend_by_file(database_path)

    try_count = 1
    max_try_count = 3
    success = False
    while try_count <= max_try_count:
        passphrase = getpass.getpass(
            "Please enter the passphrase for database %s: \n" %
            database_path)
        try:
            backend = backend_class(database_path, passphrase)
        except backends.WrongPassword:
            log.info(
                "Wrong passphrase, please try again. (attempt [%s/%s]" %
                (try_count, max_try_count))
            try_count += 1
        else:
            success = True
            log.info("Passphrase accepted")
            break

    if success is False:
        sys.exit("Wrong passphrase after %d attempts" % max_try_count)

    kpconf.set_backend(backend)

    # config daemon
    if is_daemon:
        pid_file = os.path.join(kpconf.confdir, "process.pid")
        log.info("Server started as daemon on %s:%s" % (host, port))
        daemon = daemonize.Daemonize(app=APP_NAME,
                                     pid=pid_file,
                                     action=server.serve_forever,
                                     keep_fds=get_logging_handler_streams() + [server.fileno()])
        daemon.logger = log
        daemon.start()
    else:
        log.info("Server started on %s:%s" % (host, port))
        server.serve_forever()

if __name__ == '__main__':
    main()
