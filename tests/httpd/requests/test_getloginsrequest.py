# -*- coding: utf-8 -*-
import mock

from keepass_http.backends import EntrySpec
from keepass_http.httpd import requests


class TestBackend(mock.Mock):
    search_entries = mock.Mock()


class TestServer(mock.Mock):
    backend = TestBackend()


class TestKPC(mock.Mock):
    decrypt = mock.Mock(return_value=None)
    encrypt = mock.Mock()


@mock.patch.object(TestBackend, "search_entries")
@mock.patch.object(requests.Request, "get_kpc")
@mock.patch.object(requests.Request, "authenticate")
def test_getloginsrequest_no_entries(mock_authenticate, mock_get_kpc, mock_search_entries):
    mock_authenticate.return_value = None

    mock_get_kpc.return_value = TestKPC()
    mock_search_entries.return_value = []

    test_dict = {"Id": "test_clientname",
                 "Url": "http://www.google.de/login"}
    test_server = TestServer()

    request = requests.GetLoginsRequest(test_server)
    assert request.get_response(test_dict) == {'Success': True, 'Entries': []}


@mock.patch.object(requests.Request, "set_verifier")
@mock.patch.object(TestBackend, "search_entries")
@mock.patch.object(requests.Request, "get_kpc")
@mock.patch.object(requests.Request, "get_response_kpc")
@mock.patch.object(requests.Request, "authenticate")
def test_associaterequest_with_entries(mock_authenticate, mock_get_response_kpc, mock_get_kpc, mock_search_entries, mock_set_verifier):
    mock_authenticate.return_value = None

    kpc = TestKPC()
    mock_get_kpc.return_value = kpc
    mock_get_response_kpc.return_value = kpc
    mock_search_entries.return_value = [EntrySpec(uuid="1", title="Login To Google",
                                                  login="spam.eggs@gmail.com", password="1234",
                                                  url="http://www.google.de/login/form.html")]

    test_dict = {"Id": "test_clientname",
                 "Url": "http://www.google.de/login"}

    test_server = TestServer()
    kpc.encrypt.side_effect = ["name_encrypted", "login_encrypted", "uuid_encrypted",
                               "password_encrypted"]

    request = requests.GetLoginsRequest(test_server)

    assert request.get_response(test_dict) == {'Success': True,
                                               'Entries': [{'Login': 'login_encrypted',
                                                            'Password': 'password_encrypted',
                                                            'Name': 'name_encrypted',
                                                            'Uuid': 'uuid_encrypted'}]}

    assert kpc.encrypt.call_args_list == [mock.call('Login To Google'),
                                          mock.call('spam.eggs@gmail.com'),
                                          mock.call('1'),
                                          mock.call('1234')]


@mock.patch.object(requests.Request, "authenticate")
def test_getlogins_request_not_valid_authentication(mock_authenticate):
    request = requests.GetLoginsRequest(None)

    mock_authenticate.side_effect = requests.AuthenticationError()
    assert request.get_response({}) == {'Success': False}
