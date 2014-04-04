# -*- coding: utf-8 -*-
import mock

from keepass_http.crypto import AESCipher
from keepass_http.httpd import requests
from keepass_http.ui.cli import RequireAssociationDecision


class TestBackend(mock.Mock):
    create_config_key = mock.Mock(return_value=None)
    get_config = mock.Mock(return_value="NDI2MjYyOTI0NDA1MjMyNDQ1OTg5ODc2MDYwNjY4NDI=")


class TestServer(mock.Mock):
    backend = TestBackend()


@mock.patch.object(AESCipher, 'generate_nonce')
@mock.patch.object(TestBackend, "create_config_key")
@mock.patch.object(RequireAssociationDecision, "require_client_name")
def test_associaterequest_successfull(mock_require_client_name, mock_create_config_key, mock_generate_nonce):
    test_client_name = "test client name"
    mock_require_client_name.return_value = test_client_name
    mock_generate_nonce.return_value = "OTYwOTgzNjI0MzcxMzQ5MQ=="

    test_dict = {"Key": "Some 64 encoded key",
                 'Nonce': "asd", "Verifier": "ssa"}
    test_server = TestServer()
    request = requests.AssociateRequest(test_server)

    expected_response_dict = {'Success': True,
                              'Id': test_client_name,
                              'Verifier': 'tawc1wLei/tqFyEkP2Grs1jJkqk4bQk6iN696iyvR7o=',
                              'Nonce': 'OTYwOTgzNjI0MzcxMzQ5MQ=='}

    response = request.get_response(test_dict)
    assert response == expected_response_dict

    mock_create_config_key.assert_called_once_with(test_client_name,
                                                   'Some 64 encoded key')


@mock.patch.object(RequireAssociationDecision, "require_client_name")
def test_associaterequest_no_accept(mock_require_client_name):
    mock_require_client_name.return_value = None

    test_dict = {"Key": "Some 64 encoded key"}
    test_server = TestServer()
    request = requests.AssociateRequest(test_server)

    expected_response_dict = {'Success': False}
    assert request.get_response(test_dict) == expected_response_dict
