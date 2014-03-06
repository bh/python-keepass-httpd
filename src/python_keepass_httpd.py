#!/usr/bin/env python
"""
Usage:
  ./python-keepass-httpd.py start <database_path> <passphrase> [options]
  ./python-keepass-httpd.py (-h | --help)
  ./python-keepass-httpd.py --version

Options:
  --help                    Show this screen.
  -v --version              Show version.
  -d --daemon               Start as daemon
  -p --port PORT            Specify a port [default: 19455]
  -h --host HOST            Specify a host [default: 127.0.0.1]
  -l --loglevel LOGLEVEL    Loglevel to use [default: INFO]

"""

import logging
import os

import daemon

import docopt
import lockfile
#import setproctitle
from keepass_http import backends
from keepass_http.httpd.server import (KeepassHTTPRequestHandler,
                                       KeepassHTTPServer)
from keepass_http.utils import ConfDir


def main():
    arguments = docopt.docopt(__doc__)

    is_daemon = arguments["--daemon"]
    database_path = arguments["<database_path>"]
    passphrase = arguments["<passphrase>"]
    host = arguments["--host"]
    port = arguments["--port"]
    assert port.isdigit()
    loglevel = arguments["--loglevel"]

    kpconf = ConfDir()
    kpconf.initialize_logging(loglevel)
    log = logging.getLogger("keepass_http_script")

    # backend
    backend_class = backends.get_backend_by_file(database_path)
    backend = backend_class(database_path, passphrase)

    # server
    server = KeepassHTTPServer((host, int(port)), KeepassHTTPRequestHandler)
    server.set_is_daemon(is_daemon)
    log.info("Server started on %s:%s" % (host, port))

    server.set_backend(backend)
    log.debug("Use Keepass Backend: %s" % backend.__class__.__name__)

    if is_daemon:
        files_to_preserve = kpconf.get_logging_handler_streams() + [server.fileno()]
        context = daemon.DaemonContext(files_preserve=files_to_preserve,
                                       pidfile=lockfile.FileLock('/tmp/spam.pid'),
                                       )

        with context:
            log.debug("Process is forking to background...")
            server.serve_forever()

    else:
        server.serve_forever()

if __name__ == '__main__':
    main()
