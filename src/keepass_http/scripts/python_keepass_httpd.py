#!/usr/bin/env python2
"""
Usage:
  python-keepass-httpd.py run <database_path> [options]
  python-keepass-httpd.py (-h | --help)
  python-keepass-httpd.py --version

Options:
  --help                    Show this screen.
  -v --version              Show version.
  -d --daemon               Start as daemon
  -p --port PORT            Specify a port [default: 19455]
  -h --host HOST            Specify a host [default: 127.0.0.1]
  -l --loglevel LOGLEVEL    Loglevel to use [default: INFO]

"""

import getpass
import logging
import os
import sys

import daemonize

import docopt
from keepass_http import backends
from keepass_http.httpd.server import KeepassHTTPRequestHandler, KeepassHTTPServer
from keepass_http.utils import ConfDir


def main():
    arguments = docopt.docopt(__doc__)

    is_daemon = arguments["--daemon"]
    database_path = arguments["<database_path>"]
    host = arguments["--host"]
    port = arguments["--port"]
    assert port.isdigit()
    loglevel = arguments["--loglevel"]

    # basic config
    kpconf = ConfDir()
    kpconf.initialize_logging(loglevel)
    log = logging.getLogger("keepass_http_script")

    # server
    server = KeepassHTTPServer((host, int(port)), KeepassHTTPRequestHandler)
    server.set_is_daemon(is_daemon)
    log.info("Server started on %s:%s" % (host, port))

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
            print "Wrong password, please try again."
            try_count += 1
        else:
            success = True
            break

    if success is False:
        sys.exit("Wrong password after %d attempts" % max_try_count)

    server.set_backend(backend)
    log.debug("Use Keepass Backend: %s" % backend.__class__.__name__)

    # config daemon
    if is_daemon:
        pid_file = os.path.join(kpconf.confdir, "process.pid")
        files_to_preserve = kpconf.get_logging_handler_streams() + [server.fileno()]
        daemon = daemonize.Daemonize(app="Keepass HTTPD server", pid=pid_file,
                                     action=server.serve_forever, keep_fds=files_to_preserve)
        daemon.start()
    else:
        server.serve_forever()

if __name__ == '__main__':
    main()
