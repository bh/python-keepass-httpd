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

import daemon

import docopt
from keepass_http import backends
from keepass_http.httpd.server import KeepassHTTPRequestHandler, KeepassHTTPServer
from keepass_http.utils import ConfDir, query_yes_no
from lockfile import pidlockfile

#import setproctitle


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

    pid_file = pidlockfile.PIDLockFile(os.path.join(kpconf.confdir, "process.pid"))

    if pid_file.is_locked():
        if query_yes_no("It looks like another instance of python-keepass-http is currently running. "
                        "Do you want to overwrite the pid file?", default="yes"):
            existing_pid = pid_file.read_pid()
            pid_file.break_lock()

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

    # config daemon context
    files_to_preserve = kpconf.get_logging_handler_streams() + [server.fileno()]
    daemon_context = daemon.DaemonContext(detach_process=is_daemon,
                                          files_preserve=files_to_preserve,
                                          pidfile=pid_file)

    with daemon_context:
        if is_daemon:
            log.info("Process forked to background - PID: %s" % os.getpid())
        server.serve_forever()

if __name__ == '__main__':
    main()