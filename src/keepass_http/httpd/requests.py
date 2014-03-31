# -*- coding: utf-8 -*-
import abc

from keepass_http.core import logging
from keepass_http.crypto import AESCipher
from keepass_http.utils import query_yes_no

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

        kpc = AESCipher(key, nonce)

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
        response_dict = {}
        response_dict['Success'] = False

        client_name = request_dict.get("Id", None)
        # missing field -> force associate
        if not client_name:
            return response_dict

        # no auth -> force associate
        try:
            self.authenticate(request_dict)
        except AuthenticationError as unused_e:
            return response_dict

        # already associated, all fine
        response_dict['Id'] = client_name
        response_dict['Success'] = True

        return response_dict


class AssociateRequest(Request):

    def get_response(self, request_dict):
        response_dict = {}
        response_dict['Success'] = False

        if query_yes_no("Should be the client accepted?", default="no"):
            client_name = raw_input("Give the client a name: ")
            self.server.backend.create_config_key(client_name, request_dict["Key"])
            response_dict['Id'] = client_name
            response_dict['Success'] = True
            response_dict['Nonce'] = request_dict['Nonce']
            response_dict['Verifier'] = request_dict['Verifier']

        return response_dict


class GetLoginsRequest(Request):

    def get_response(self, request_dict):
        response_dict = {}
        response_dict['Success'] = False

        try:
            self.authenticate(request_dict)
        except AuthenticationError as unused_e:
            return response_dict

        kpc = self.get_kpc()
        url = kpc.decrypt(request_dict['Url'])

        response_dict["Entries"] = []
        entries = self.server.backend.search_entries("url", url)
        for entry in entries:
            response_dict["Entries"].append(entry.to_json_dict(kpc))

        response_dict['Success'] = True
        return response_dict


class SetLoginRequest(Request):

    def get_response(self, request_dict):
        response_dict = {}
        response_dict['Success'] = False

        try:
            self.authenticate(request_dict)
        except AuthenticationError as unused_e:
            return response_dict

        kpc = self.get_kpc()

        url = kpc.decrypt(request_dict['SubmitUrl'])
        login = kpc.decrypt(request_dict['Login'])
        password = kpc.decrypt(request_dict['Password'])

        self.server.backend.create_login(request_dict["Id"], login, password, url)

        response_dict['Success'] = True
        return response_dict
