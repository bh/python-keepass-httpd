# -*- coding: utf-8 -*-
import SocketServer

import mock

from keepass_http.httpd.server import KeepassHTTPServer


class FakeBackend(mock.Mock):
    pass

@mock.patch.object(SocketServer.ThreadingTCPServer, "__init__")
def test_server_init(mock_init):
    httpd = KeepassHTTPServer("localhost", 1234)
    httpd.set_is_daemon(True)
    httpd.set_backend(FakeBackend)


@mock.patch.object(SocketServer.ThreadingTCPServer, "__init__")
def test_server_handle_exception(mock_init):
    httpd = KeepassHTTPServer("localhost", 22222)
    test_request_class = type("TestRequest", (object,), {})
    httpd.handle_error(test_request_class, ("localhost", 22222))
