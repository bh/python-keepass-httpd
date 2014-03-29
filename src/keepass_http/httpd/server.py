import json
import SocketServer

from keepass_http.core import logging
from keepass_http.httpd import requests

log = logging.getLogger(__name__)


class KeepassHTTPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, host, port):
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), KeepassHTTPRequestHandler)
        self._is_daemon = None
        self.backend = None

    def set_backend(self, backend):
        log.debug("Using Keepass Backend: %s" % backend.__module__)
        self.backend = backend

    def set_is_daemon(self, is_daemon):
        self._is_daemon = is_daemon

    def handle_error(self, request, client_address):
        """
        """
        client_host, client_port = client_address
        log.exception("An error has been occured for client: %s:%s" % (client_host,
                                                                       client_port))


class KeepassHTTPRequestHandler(SocketServer.BaseRequestHandler):

    def _extract_request_body(self):
        http_request = self.request.recv(1024).strip()
        unused_http_header, body = http_request.split('\r\n\r\n')
        return json.loads(body)

    def _write_reponse(self, response):
        self.request.sendall(json.dumps(response))

    def handle(self):
        request_body = self._extract_request_body()
        response_content = self.handle_request(request_body)
        self._write_reponse(response_content)

    def handle_request(self, request_dict):
        request_type = request_dict["RequestType"]

        if request_type == "test-associate":
            request = requests.TestAssociateRequest(self.server)

        elif request_type == "associate":
            request = requests.AssociateRequest(self.server)

        elif request_type == "get-logins":
            request = requests.GetLoginsRequest(self.server)

        elif request_type == "set-login":
            request = requests.SetLoginRequest(self.server)

        else:
            raise NotImplementedError(
                "Request type %s is not yet implemented" %
                request_dict["RequestType"])

        return request.get_response(request_dict)
