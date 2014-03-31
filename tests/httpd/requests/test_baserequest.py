# -*- coding: utf-8 -*-
import mock
import pytest

from keepass_http.httpd import requests


class TestBackend(mock.Mock):
    get_config = mock.Mock()


class TestServer(mock.Mock):
    backend = TestBackend()


class TestAES(mock.Mock):
    pass


class ImplementedRequest(requests.Request):

    def get_response(self, request_dict):
        return


def test_baserequest_is_abstract():
    with pytest.raises(TypeError):
        requests.Request(None)


def test_baserequest_authenticate_broken_request_dict():
    test_server = TestServer()
    request = ImplementedRequest(test_server)

    with pytest.raises(KeyError):
        request.authenticate({})


@mock.patch.object(TestBackend, "get_config")
def test_baserequest_authenticate_unknown_key(mock_get_config):
    test_server = TestServer()

    request = ImplementedRequest(test_server)

    mock_get_config.return_value = None
    with pytest.raises(requests.AuthenticationError):
        request.authenticate({"Id": "some client name",
                              "Key": "some unknown key"})


@mock.patch.object(TestBackend, "get_config")
def test_baserequest_authenticate_broken_request_dict_2(mock_get_config):
    test_server = TestServer()

    request = ImplementedRequest(test_server)

    mock_get_config.return_value = "known key"

    with pytest.raises(KeyError):
        request.authenticate({"Id": "some client name",
                              "Key": "some known key"})

    with pytest.raises(KeyError):
        request.authenticate({"Id": "some client name",
                              "Nonce": "some nonce"})


@mock.patch("keepass_http.httpd.requests.AESCipher")
@mock.patch.object(TestBackend, "get_config")
def test_baserequest_authenticate_with_kpc_invalid(mock_get_config, mock_kpc):
    mock_get_config.return_value = "known key"
    test_server = TestServer()

    aes = TestAES()
    mock_kpc.return_value = aes

    aes.is_valid = mock.Mock(return_value=False)

    request_dict = {"Id": "some client name",
                    "Key": "some known key",
                    "Nonce": "some nonce",
                    "Verifier": "some verifier"}

    request = ImplementedRequest(test_server)
    with pytest.raises(requests.InvalidAuthentication):
        request.authenticate(request_dict)


@mock.patch("keepass_http.httpd.requests.AESCipher")
@mock.patch.object(TestBackend, "get_config")
def test_baserequest_authenticate_with_kpc_valid(mock_get_config, mock_kpc):
    mock_get_config.return_value = "known key"
    test_server = TestServer()

    aes = TestAES()
    mock_kpc.return_value = aes

    aes.is_valid = mock.Mock(return_value=True)

    request_dict = {"Id": "some client name",
                    "Key": "some known key",
                    "Nonce": "some nonce",
                    "Verifier": "some verifier"}

    request = ImplementedRequest(test_server)
    request.authenticate(request_dict)


@mock.patch("keepass_http.httpd.requests.AESCipher")
@mock.patch.object(TestBackend, "get_config")
def test_baserequest_authenticate_with_kpc_get_kpc_authenticated(mock_get_config, mock_kpc):
    mock_get_config.return_value = "known key"
    test_server = TestServer()

    aes = TestAES()
    mock_kpc.return_value = aes

    aes.is_valid = mock.Mock(return_value=True)
    aes._kpc = mock.Mock(return_value=aes)

    request_dict = {"Id": "some client name",
                    "Key": "some known key",
                    "Nonce": "some nonce",
                    "Verifier": "some verifier"}

    request = ImplementedRequest(test_server)
    request.authenticate(request_dict)
    request.get_kpc()


@mock.patch.object(TestBackend, "get_config")
def test_baserequest_authenticate_with_kpc_get_kpc_not_authenticated(mock_get_config):
    mock_get_config.return_value = "known key"
    test_server = TestServer()

    aes = TestAES()
    aes._kpc = mock.Mock(return_value=None)

    request = ImplementedRequest(test_server)
    with pytest.raises(requests.NotAuthenticated):
        request.get_kpc()
