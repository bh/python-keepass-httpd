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
from lockfile import pidlockfile

from keepass_http import backends
from keepass_http.httpd.server import (KeepassHTTPRequestHandler,
                                       KeepassHTTPServer)
from keepass_http.utils import ConfDir

#import setproctitle


def main():
    arguments = docopt.docopt(__doc__)

    is_daemon = arguments["--daemon"]
    database_path = arguments["<database_path>"]
    passphrase = arguments["<passphrase>"]
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
    backend = backend_class(database_path, passphrase)
    server.set_backend(backend)
    log.debug("Use Keepass Backend: %s" % backend.__class__.__name__)

    # config daemon context
    files_to_preserve = kpconf.get_logging_handler_streams() + [server.fileno()]
    pid_file = pidlockfile.PIDLockFile(os.path.join(kpconf.dir, "process.pid"))
    daemon_context = daemon.DaemonContext(detach_process=is_daemon,
                                          files_preserve=files_to_preserve,
                                          pidfile=pid_file)

    with daemon_context:
        if is_daemon:
            log.info("Process forked to background - PID: %s" % os.getpid())
        server.serve_forever()

if __name__ == '__main__':
    main()
