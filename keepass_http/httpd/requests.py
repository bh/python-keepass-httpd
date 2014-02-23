import abc

from keepass_http.crypto import AESEncryption
from keepass_http.utils import logging, query_yes_no

log = logging.getLogger(__name__)


class AuthenticationError(Exception):
    pass


class InvalidAuthentication(AuthenticationError):
    pass


class NotAuthenticated(AuthenticationError):
    pass


class Request:
    __metaclass__ = abc.ABCMeta
    name = None

    def __init__(self, server):
        self.server = server
        self._kpc = None
        log.info("Got request: %s" % self.__class__.__name__)

    @abc.abstractmethod
    def get_response(self, request_dict):
        """
        """

    def authenticate(self, request_dict):
        client_name = request_dict["Id"]

        log.info("Authenticate client %s" % client_name)

        key = self.server.backend.get_config(client_name)
        if not key:
            raise AuthenticationError()

        nonce = request_dict['Nonce']
        verifier = request_dict['Verifier']

        kpc = AESEncryption(key, nonce)

        # wrong saved key in database -> force associate
        if not kpc.is_valid(nonce, verifier):
            raise InvalidAuthentication()

        self._kpc = kpc

    def get_kpc(self):
        if not self._kpc:
            raise NotAuthenticated()
        return self._kpc

    def cleanup_request_dict(self, request_dict):
        """
        """
        # Todo: implement
        raise NotImplementedError

class TestAssociateRequest(Request):

    def get_response(self, request_dict):
        request_dict['Success'] = False

        # missing field -> force associate
        if "Id" not in request_dict:
            return request_dict

        # no auth -> force associate
        try:
            self.authenticate(request_dict)
        except AuthenticationError as unused_e:
            return request_dict

        # already associated, all fine
        request_dict['Id'] = request_dict["Id"]
        request_dict['Success'] = True

        return request_dict


class AssociateRequest(Request):

    def get_response(self, request_dict):
        request_dict['Success'] = False

        if query_yes_no("Should be the client accepted?", default="no"):
            client_name = raw_input("Give the client a name: ")
            self.server.backend.create_config_key(client_name, request_dict["Key"])
            request_dict['Id'] = client_name
            request_dict['Success'] = True

        return request_dict


class GetLoginsRequest(Request):

    def get_response(self, request_dict):
        request_dict['Success'] = False

        try:
            self.authenticate(request_dict)
        except AuthenticationError as unused_e:
            return request_dict

        kpc = self.get_kpc()
        url = kpc.decrypt(request_dict['Url'])

        request_dict["Entries"] = []
        entries = self.server.backend.search_entries("url", url)
        for entry in entries:
            request_dict["Entries"].append(entry.to_json_dict(kpc))

        request_dict['Success'] = True
        return request_dict


class SetLoginRequest(Request):

    def get_response(self, request_dict):
        request_dict['Success'] = False
        try:
            self.authenticate(request_dict)
        except AuthenticationError as unused_e:
            return request_dict

        kpc = self.get_kpc()

        url = kpc.decrypt(request_dict['SubmitUrl'])
        login = kpc.decrypt(request_dict['Login'])
        password = kpc.decrypt(request_dict['Password'])

        self.server.backend.create_login(request_dict["Id"], login, password, url)

        request_dict['Success'] = True
        return request_dict
