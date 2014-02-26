#!/usr/bin/env python
"""
Usage:
  ./python-keepass-httpd.py start <database_path> <passphrase> [options]
  ./python-keepass-httpd.py (-h | --help)
  ./python-keepass-httpd.py --version

Options:
  --help                  Show this screen.
  -v --version            Show version.
  -d --daemon             Start as daemon
  -p --port PORT          Specify a port [default: 19455]
  -h --host HOST          Specify a host [default: 127.0.0.1]

"""

import sys

import daemon
import docopt
import lockfile
import setproctitle

from keepass_http import backends
from keepass_http.httpd.server import (KeepassHTTPRequestHandler,
                                       KeepassHTTPServer)
from keepass_http.utils import logging

sys.path.append("..")


log = logging.getLogger(__name__)


if __name__ == '__main__':
    arguments = docopt.docopt(__doc__)

    is_daemon = arguments["--daemon"]
    database_path = arguments["<database_path>"]
    passphrase = arguments["<passphrase>"]
    host = arguments["--host"]
    port = arguments["--port"]
    assert port.isdigit()

    # backend
    backend_class = backends.get_backend_by_file(database_path)
    backend = backend_class(database_path, passphrase)

    # server
    server = KeepassHTTPServer((host, int(port)), KeepassHTTPRequestHandler)
    server.set_is_daemon(is_daemon)
    server.set_backend(backend)

    log.debug("Use Keepass Backend: %s" % backend.__class__.__name__)
    log.info("Server started on %s:%s" % (host, port))

    if is_daemon:
        context = daemon.DaemonContext(stdout=open("/tmp/o.log", "w"),
                                       stderr=open("/tmp/e.log", "w"),
                                       files_preserve=[server.fileno()],
                                       pidfile=lockfile.FileLock('/tmp/spam.pid'),
                                       )

        with context:
            setproctitle.setproctitle("Keepass HTTPD server on %s:%s" % (host, port))
            server.serve_forever()

    else:
        server.serve_forever()
