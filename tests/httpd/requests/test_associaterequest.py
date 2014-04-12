# -*- coding: utf-8 -*-
import mock

from keepass_http.crypto import AESCipher
from keepass_http.httpd import requests
from keepass_http.ui import cli


class TestBackend(mock.Mock):
    create_config_key = mock.Mock(return_value=None)
    get_config = mock.Mock(return_value="NDI2MjYyOTI0NDA1MjMyNDQ1OTg5ODc2MDYwNjY4NDI=")


class TestConf(mock.Mock):
    backend = TestBackend()
    get_selected_ui = mock.Mock(return_value=cli)

@mock.patch("keepass_http.httpd.requests.Conf", TestConf)
@mock.patch.object(AESCipher, 'generate_nonce')
@mock.patch.object(TestBackend, "create_config_key")
@mock.patch.object(cli.RequireAssociationDecision, "require_client_name")
def test_associaterequest_successfull(mock_require_client_name, mock_create_config_key, mock_generate_nonce):
    test_client_name = "test client name"
    mock_require_client_name.return_value = test_client_name
    mock_generate_nonce.return_value = "OTYwOTgzNjI0MzcxMzQ5MQ=="

    test_dict = {"Key": "Some 64 encoded key",
                 'Nonce': "asd", "Verifier": "ssa"}
    request = requests.AssociateRequest()

    expected_response_dict = {'Success': True,
                              'Id': test_client_name,
                              'Verifier': 'tawc1wLei/tqFyEkP2Grs1jJkqk4bQk6iN696iyvR7o=',
                              'Nonce': 'OTYwOTgzNjI0MzcxMzQ5MQ=='}

    response = request(test_dict)
    assert response == expected_response_dict

    mock_create_config_key.assert_called_once_with(test_client_name,
                                                   'Some 64 encoded key')


@mock.patch.object(cli.RequireAssociationDecision, "require_client_name")
def test_associaterequest_no_accept(mock_require_client_name):
    mock_require_client_name.return_value = None

    test_dict = {"Key": "Some 64 encoded key"}
    request = requests.AssociateRequest()

    assert request(test_dict) == {'Success': False}
