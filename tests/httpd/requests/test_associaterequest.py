import mock

from keepass_http.httpd import requests


class TestBackend(mock.Mock):
    create_config_key = mock.Mock(return_value=None)


class TestServer(mock.Mock):
    backend = TestBackend()


@mock.patch.object(TestBackend, "create_config_key")
@mock.patch('__builtin__.raw_input')
@mock.patch('keepass_http.httpd.requests.query_yes_no')
def test_associaterequest_successfull(mock_qyn, mock_rawinput, mock_create_config_key):
    test_client_name = "test client name"
    mock_qyn.return_value = True
    mock_rawinput.return_value = test_client_name

    test_dict = {"Key": "Some 64 encoded key"}
    test_server = TestServer()
    request = requests.AssociateRequest(test_server)

    expected_response_dict = {'Success': True, 'Id': test_client_name}
    assert request.get_response(test_dict) == expected_response_dict
    mock_create_config_key.assert_called_once_with(test_client_name,
                                                   'Some 64 encoded key')


@mock.patch('keepass_http.httpd.requests.query_yes_no')
def test_associaterequest_no_accept(mock_qyn):
    mock_qyn.return_value = False

    test_dict = {"Key": "Some 64 encoded key"}
    test_server = TestServer()
    request = requests.AssociateRequest(test_server)

    expected_response_dict = {'Success': False}
    assert request.get_response(test_dict) == expected_response_dict
