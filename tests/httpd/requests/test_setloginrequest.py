# -*- coding: utf-8 -*-
import mock

from keepass_http.httpd import requests


class TestBackend(mock.Mock):
    create_login = mock.Mock(return_value=None)


class TestKPC(mock.Mock):
    encrypt = mock.Mock()
    decrypt = mock.Mock()


class TestConf(mock.Mock):
    backend = TestBackend()


@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
@mock.patch.object(requests.Request, "set_verifier")
@mock.patch.object(TestBackend, "create_login")
@mock.patch.object(requests.Request, "kpc")
@mock.patch.object(requests.Request, "response_kpc")
@mock.patch.object(requests.Request, "authenticate")
def test_setloginrequest_successfull(
        mock_authenticate, mock_get_kpc, mock_response_kpc, mock_create_login, mock_set_verifier):
    kpc = TestKPC()
    mock_get_kpc.return_value = kpc
    mock_response_kpc.return_value = kpc

    test_dict = {"Id": "test_clientname",
                 "SubmitUrl": "submiturl_encrypted",
                 "Login": "login_encrypted",
                 "Password": "password_encrypted"}

    mock_response_kpc.decrypt.side_effect = ["http://twitter.com/login", "some user", "password"]

    request = requests.SetLoginRequest()

    # TODO: remove the request values from response dict
    assert request(test_dict) == {'Success': True}

    mock_create_login.assert_called_once_with('test_clientname', 'some user',
                                              'password', 'http://twitter.com/login')


@mock.patch.object(requests.Request, "authenticate")
def test_setlogin_request_not_valid_authentication(mock_authenticate):
    request = requests.SetLoginRequest()

    mock_authenticate.side_effect = requests.AuthenticationError()
    assert request({}) == {'Success': False}
