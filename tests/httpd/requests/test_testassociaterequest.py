# -*- coding: utf-8 -*-
import mock

from keepass_http.httpd import requests


class TestBackend(mock.Mock):
    pass


class TestServer(mock.Mock):
    backend = TestBackend()


@mock.patch.object(requests.Request, "authenticate")
def test_testassociaterequest(mock_authenticate):
    mock_authenticate.side_effect = requests.AuthenticationError

    test_dict = {"Id": "test_clientname"}
    test_server = TestServer()
    request = requests.TestAssociateRequest(test_server)

    assert request.get_response(test_dict) == {"Success": False}


def test_testassociaterequest_invalid_clientname():
    test_dict = {}
    test_server = TestServer()
    request = requests.TestAssociateRequest(test_server)

    assert request.get_response(test_dict) == {"Success": False}


@mock.patch.object(requests.Request, "set_verifier")
@mock.patch.object(requests.Request, "authenticate")
def test_testassociaterequest_ok(mock_authenticate, mock_set_verifier):
    mock_authenticate.return_value = None
    mock_set_verifier.return_value = None

    test_dict = {"Id": "test_clientname"}
    test_server = TestServer()
    request = requests.TestAssociateRequest(test_server)

    assert request.get_response(test_dict) == {"Id": "test_clientname", "Success": True}
