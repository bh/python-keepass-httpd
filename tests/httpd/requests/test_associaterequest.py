# -*- coding: utf-8 -*-
import mock

from keepass_http.httpd import requests
from keepass_http.ui.cli import RequireAssociationDecision


class TestBackend(mock.Mock):
    create_config_key = mock.Mock(return_value=None)


class TestServer(mock.Mock):
    backend = TestBackend()


@mock.patch.object(TestBackend, "create_config_key")
@mock.patch.object(RequireAssociationDecision, "require_client_name")
def test_associaterequest_successfull(mock_require_client_name, mock_create_config_key):
    test_client_name = "test client name"
    mock_require_client_name.return_value = test_client_name

    test_dict = {"Key": "Some 64 encoded key",
                 'Nonce': "asd", "Verifier": "ssa"}
    test_server = TestServer()
    request = requests.AssociateRequest(test_server)

    expected_response_dict = {'Success': True, 'Id': test_client_name,
                              'Nonce': "asd", "Verifier": "ssa"}
    assert request.get_response(test_dict) == expected_response_dict
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
