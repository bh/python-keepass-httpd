# -*- coding: utf-8 -*-
import abc
from urlparse import urlparse

from keepass_http.core import Conf, logging
from keepass_http.crypto import AESCipher

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
        self._response_kpc = None

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

    def set_verifier(self, response_dict, client_name):
        key = self.server.backend.get_config(client_name)
        if not key:
            raise AuthenticationError("set_verifier - Could not set verifier: no valid "
                                      "key for client: %s " % client_name)
        nonce = AESCipher.generate_nonce()
        self._response_kpc = AESCipher(key, nonce)
        response_dict['Nonce'] = nonce
        response_dict['Verifier'] = self._response_kpc.encrypt(nonce)

    def get_kpc(self):
        if not self._kpc:
            raise NotAuthenticated()
        return self._kpc

    def get_response_kpc(self):
        if not self._response_kpc:
            raise NotAuthenticated()
        return self._response_kpc


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

        self.set_verifier(response_dict, client_name)

        return response_dict


class AssociateRequest(Request):

    def get_response(self, request_dict):
        response_dict = {}
        response_dict['Success'] = False

        kpconf = Conf()
        new_client_name = kpconf.get_selected_ui().RequireAssociationDecision.require_client_name()
        if new_client_name:
            self.server.backend.create_config_key(new_client_name, request_dict["Key"])
            response_dict['Id'] = new_client_name
            response_dict['Success'] = True

            self.set_verifier(response_dict, new_client_name)

        return response_dict


class GetLoginsRequest(Request):

    def get_response(self, request_dict):
        response_dict = {}
        response_dict['Success'] = False

        try:
            self.authenticate(request_dict)
        except AuthenticationError as unused_e:
            return response_dict
        client_name = request_dict["Id"]

        response_dict['Success'] = True
        response_dict["Entries"] = []

        url = str(self.get_kpc().decrypt(request_dict['Url']))
        url = urlparse(url).netloc
        url = url.decode("utf-8")

        self.set_verifier(response_dict, client_name)
        entries = self.server.backend.search_entries("url", url)
        for entry in entries:
            json_entry = entry.to_json_dict(self.get_response_kpc())
            response_dict["Entries"].append(json_entry)
        return response_dict


class GetLoginsCountRequest(Request):

    def get_response(self, request_dict):
        response_dict = {}
        response_dict['Success'] = False

        try:
            self.authenticate(request_dict)
        except AuthenticationError as unused_e:
            return response_dict

        url = self.get_kpc().decrypt(request_dict['Url'])
        url = url.decode("utf-8")

        entries = self.server.backend.search_entries("url", url)
        response_dict['Success'] = True
        response_dict['Count'] = len(entries)
        self.set_verifier(response_dict, request_dict["Id"])

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
