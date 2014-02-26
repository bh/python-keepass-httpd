from keepass_http.httpd.server import KeepassHTTPServer

import mock
import SocketServer


@mock.patch.object(SocketServer.ThreadingTCPServer, "__init__")
def test_server_init(mock_init):
    httpd = KeepassHTTPServer()
    httpd.set_is_daemon(True)
    httpd.set_backend(None)


@mock.patch.object(SocketServer.ThreadingTCPServer, "__init__")
def test_server_handle_exception(mock_init):
    httpd = KeepassHTTPServer()
    test_request_class = type("TestRequest", (object,), {})
    httpd.handle_error(test_request_class, ("localhost", 22222))
