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


@mock.patch.object(requests.Request, "authenticate")
def test_getloginscountrequest_request_not_valid_authentication(mock_authenticate):
    request = requests.GetLoginsCountRequest(None)

    mock_authenticate.side_effect = requests.AuthenticationError()
    assert request({}) == {'Success': False}


@mock.patch.object(requests.Request, "set_verifier")
@mock.patch.object(TestBackend, "search_entries")
@mock.patch.object(requests.Request, "authenticate")
@mock.patch.object(requests.Request, "get_kpc")
def test_getloginscountrequest_no_entries(mock_get_kpc, mock_authenticate, mock_search_entries, mock_set_verifier):
    mock_search_entries.return_value = []
    kpc = TestKPC()
    kpc.decrypt.side_effect = ["url_encrypted",]
    mock_get_kpc.return_value = kpc

    test_server = TestServer()
    request = requests.GetLoginsCountRequest(test_server)

    test_dict = {"Key": "Some 64 encoded key",
                 "Id": "asdasd",
                 'Nonce': "asd", "Verifier": "ssa",
                 "Url": "http://www.google.de/login"}
    assert request(test_dict) == {'Count': 0, 'Success': True}


@mock.patch.object(requests.Request, "set_verifier")
@mock.patch.object(TestBackend, "search_entries")
@mock.patch.object(requests.Request, "authenticate")
@mock.patch.object(requests.Request, "get_kpc")
def test_getloginscountrequest_with_entries(mock_get_kpc, mock_authenticate, mock_search_entries, mock_set_verifier):
    mock_search_entries.return_value = [EntrySpec(uuid="1", title="Login To Google",
                                                  login="spam.eggs@gmail.com", password="1234",
                                                  url="http://www.google.de/login/form.html")]
    kpc = TestKPC()
    kpc.decrypt.side_effect = ["url_encrypted",]
    mock_get_kpc.return_value = kpc

    test_server = TestServer()
    request = requests.GetLoginsCountRequest(test_server)

    test_dict = {"Key": "Some 64 encoded key",
                 "Id": "some knwon client",
                 'Nonce': "some nonce", "Verifier": "some verifier",
                 "Url": "http://www.google.de/login"}

    assert request(test_dict) == {'Count': 1, 'Success': True}
