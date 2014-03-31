# -*- coding: utf-8 -*-
import mock

from keepass_http.httpd import requests


class TestBackend(mock.Mock):
    create_login = mock.Mock(return_value=None)


class TestServer(mock.Mock):
    backend = TestBackend()


class TestKPC(mock.Mock):
    encrypt = mock.Mock()


@mock.patch.object(TestBackend, "create_login")
@mock.patch.object(requests.Request, "get_kpc")
@mock.patch.object(requests.Request, "authenticate")
def test_setloginrequest_successfull(mock_authenticate, mock_get_kpc, mock_create_login):
    mock_authenticate.return_value = None
    kpc = TestKPC()
    mock_get_kpc.return_value = kpc
    mock_create_login.return_value = []

    test_dict = {"Id": "test_clientname",
                 "SubmitUrl": "submiturl_encrypted",
                 "Login": "login_encrypted",
                 "Password": "password_encrypted"}

    test_server = TestServer()

    kpc.decrypt.side_effect = ["http://twitter.com/login", "some user", "password"]

    request = requests.SetLoginRequest(test_server)

    # TODO: remove the request values from response dict
    assert request.get_response(test_dict) == {'Success': True}

    mock_create_login.assert_called_once_with('test_clientname', 'some user',
                                              'password', 'http://twitter.com/login')


@mock.patch.object(requests.Request, "authenticate")
def test_setlogin_request_not_valid_authentication(mock_authenticate):
    request = requests.SetLoginRequest(None)

    mock_authenticate.side_effect = requests.AuthenticationError()
    assert request.get_response({}) == {'Success': False}
