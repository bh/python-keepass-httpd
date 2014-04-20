# -*- coding: utf-8 -*-
import mock
import pytest

from keepass_http.httpd import requests


class TestBackend(mock.Mock):
    get_key_for_client = mock.Mock()


class TestConf(mock.Mock):
    backend = TestBackend()


class TestAES(mock.Mock):
    pass


class TestKPC(mock.Mock):
    decrypt = mock.Mock(return_value=None)
    encrypt = mock.Mock()


class ImplementedRequest(requests.Request):

    def process(self):
        return


def test_baserequest_is_abstract():
    with pytest.raises(TypeError):
        requests.Request(None)


@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
def test_baserequest_authenticate_broken_request_dict():
    request = ImplementedRequest()

    with pytest.raises(requests.AuthenticationError):
        request({})
        request.authenticate()


@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
@mock.patch.object(TestBackend, "get_key_for_client")
def test_baserequest_authenticate_unknown_key(mock_get_key_for_client):
    request = ImplementedRequest()

    mock_get_key_for_client.return_value = None
    with pytest.raises(requests.AuthenticationError):
        request({"Id": "some client name",
                 "Key": "some unknown key"})
        request.authenticate()


@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
@mock.patch.object(TestBackend, "get_key_for_client")
def test_baserequest_authenticate_broken_request_dict_2(mock_get_key_for_client):
    request = ImplementedRequest()

    mock_get_key_for_client.return_value = "known key"

    with pytest.raises(KeyError):
        request({"Id": "some client name",
                 "Key": "some known key"})
        request.authenticate()

    with pytest.raises(KeyError):
        request({"Id": "some client name",
                 "Nonce": "some nonce"})
        request.authenticate()


@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
@mock.patch("keepass_http.httpd.requests.AESCipher")
@mock.patch.object(TestBackend, "get_key_for_client")
def test_baserequest_authenticate_with_kpc_invalid(mock_get_key_for_client, mock_kpc):
    mock_get_key_for_client.return_value = "known key"

    aes = TestAES()
    mock_kpc.return_value = aes

    aes.is_valid = mock.Mock(return_value=False)

    request = ImplementedRequest()
    with pytest.raises(requests.InvalidAuthentication):
        request({"Id": "some client name",
                 "Key": "some known key",
                 "Nonce": "some nonce",
                 "Verifier": "some verifier"})
        request.authenticate()


@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
@mock.patch("keepass_http.httpd.requests.AESCipher")
@mock.patch.object(TestBackend, "get_key_for_client")
def test_baserequest_authenticate_with_kpc_valid(mock_get_key_for_client, mock_kpc):
    mock_get_key_for_client.return_value = "known key"

    aes = TestAES()
    mock_kpc.return_value = aes

    aes.is_valid = mock.Mock(return_value=True)
    request = ImplementedRequest()
    request({"Id": "some client name",
             "Key": "some known key",
             "Nonce": "some nonce",
             "Verifier": "some verifier"})
    request.authenticate()


@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
@mock.patch("keepass_http.httpd.requests.AESCipher")
@mock.patch.object(TestBackend, "get_key_for_client")
def test_baserequest_authenticate_with_kpc_authenticated(mock_get_key_for_client, mock_kpc):
    mock_get_key_for_client.return_value = "known key"
    aes = TestAES()
    mock_kpc.return_value = aes

    aes.is_valid = mock.Mock(return_value=True)
    aes.get_key = mock.Mock(return_value="c29tZSBrbm93biBrZXk=")

    request_dict = {"Id": "some client name",
                    "Key": "some known key",
                    "Nonce": "some nonce",
                    "Verifier": "some verifier"}

    request = ImplementedRequest()
    request(request_dict)
    request.authenticate()
    request.kpc


@mock.patch.object(TestBackend, "get_key_for_client")
def test_baserequest_authenticate_with_kpc_not_authenticated(mock_get_key_for_client):
    mock_get_key_for_client.return_value = "known key"

    aes = TestAES()
    aes._kpc = mock.Mock(return_value=None)

    request = ImplementedRequest()
    with pytest.raises(requests.NotAuthenticated):
        request({})
        request.kpc


@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
@mock.patch("keepass_http.httpd.requests.AESCipher")
@mock.patch.object(TestBackend, "get_key_for_client")
def test_baserequest_set_verifier_with_valid_key(mock_get_key_for_client, mock_kpc):
    mock_get_key_for_client.return_value = "known key"

    aes = TestAES()
    mock_kpc.return_value = aes

    request = ImplementedRequest()

    request.set_verifier("some client")

    assert request.response_dict['Nonce'] is not None
    assert request.response_dict['Verifier'] is not None


@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
@mock.patch.object(TestBackend, "get_key_for_client")
def test_baserequest_set_verifier_with_invalid_key(mock_get_key_for_client):
    mock_get_key_for_client.return_value = None

    aes = TestAES()
    aes._kpc = mock.Mock(return_value=None)

    request = ImplementedRequest()
    with pytest.raises(requests.AuthenticationError):
        request.set_verifier("nomatterwhat")
