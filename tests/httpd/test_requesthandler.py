import mock
import pytest

from keepass_http.httpd.server import KeepassHTTPRequestHandler
from keepass_http.httpd import requests


class TestServer(mock.Mock):
    pass


class TestRequest(mock.Mock):
    recv = mock.Mock()


@mock.patch.object(KeepassHTTPRequestHandler, "handle_request")
def test_extract_request_body(mock_handle_request):
    """
    Ensure that the http request body extraction works fine.
    After that, the json request body will be converted to native python types (dictionary).

    """
    mock_request = """
POST / HTTP/1.1
Host: localhost:19455
Connection: keep-alive
Content-Length: 54
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36
Origin: chrome-extension://ompiailgknfdndiefoaoiligalphfdae
Content-Type: application/json
Accept: */*
Accept-Encoding: gzip,deflate,sdch
Accept-Language: en-US,en;q=0.8

{"RequestType":"test-associate","TriggerUnlock":false}
""".replace("\n\n", "\r\n\r\n")

    mock_handle_request.return_value = {}

    server = TestServer()
    request = TestRequest()
    request.recv.return_value = mock_request

    client_address = ("localhost", 12334)
    request = KeepassHTTPRequestHandler(request, client_address, server)
    assert request._extract_request_body() == {"RequestType": "test-associate",
                                               "TriggerUnlock": False}


@mock.patch.object(KeepassHTTPRequestHandler, "handle")
def test_handle_request(mock_handle):
    """
    Check that the correct request class is called.

    """
    server = TestServer()

    with mock.patch.object(requests.TestAssociateRequest, "get_response") as mock_get_response:
        request = KeepassHTTPRequestHandler(None, None, server)
        request.handle_request({"RequestType": "test-associate"})
        mock_get_response.assert_callend_once_with(server)

    with mock.patch.object(requests.AssociateRequest, "get_response") as mock_get_response:
        request = KeepassHTTPRequestHandler(None, None, server)
        request.handle_request({"RequestType": "associate"})
        mock_get_response.assert_callend_once_with(server)

    with mock.patch.object(requests.GetLoginsRequest, "get_response") as mock_get_response:
        request = KeepassHTTPRequestHandler(None, None, server)
        request.handle_request({"RequestType": "get-logins"})
        mock_get_response.assert_callend_once_with(server)

    with mock.patch.object(requests.SetLoginRequest, "get_response") as mock_get_response:
        request = KeepassHTTPRequestHandler(None, None, server)
        request.handle_request({"RequestType": "set-login"})
        mock_get_response.assert_callend_once_with(server)

    request = KeepassHTTPRequestHandler(None, None, server)
    with pytest.raises(NotImplementedError):
        request.handle_request({"RequestType": "not-implemented-request"})
