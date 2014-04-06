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
        self._response_dict = dict(success=False)

    def update_response_dict(self, **kwargs):
        self._response_dict.update(kwargs)

    def get_response_dict(self):
        ret = {}
        for k, v in self._response_dict.iteritems():
            ret[k.capitalize()] = v
        return ret

    def __call__(self, request_dict):
        self.process(request_dict)
        return self.get_response_dict()

    @abc.abstractmethod
    def process(self, request_dict):
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

    def set_verifier(self, client_name):
        key = self.server.backend.get_config(client_name)
        if not key:
            raise AuthenticationError("set_verifier - Could not set verifier: no valid "
                                      "key for client: %s " % client_name)
        nonce = AESCipher.generate_nonce()
        self._response_kpc = AESCipher(key, nonce)
        self.update_response_dict(Nonce=nonce,
                                  Verifier=self._response_kpc.encrypt(nonce))


    def get_kpc(self):
        if not self._kpc:
            raise NotAuthenticated()
        return self._kpc

    def get_response_kpc(self):
        if not self._response_kpc:
            raise NotAuthenticated()
        return self._response_kpc


class TestAssociateRequest(Request):

    def process(self, request_dict):

        client_name = request_dict.get("Id", None)
        # missing field -> force associate
        if not client_name:
            return

        # no auth -> force associate
        try:
            self.authenticate(request_dict)
        except AuthenticationError as unused_e:
            return

        # already associated, all fine
        self.update_response_dict(id=client_name,
                                  success=True)

        self.set_verifier(client_name)


class AssociateRequest(Request):

    def process(self, request_dict):

        kpconf = Conf()
        new_client_name = kpconf.get_selected_ui().RequireAssociationDecision.require_client_name()
        if new_client_name:
            self.server.backend.create_config_key(new_client_name, request_dict["Key"])
            self.update_response_dict(id=new_client_name,
                                      success=True)

            self.set_verifier(new_client_name)


class GetLoginsRequest(Request):

    def process(self, request_dict):
        try:
            self.authenticate(request_dict)
        except AuthenticationError as unused_e:
            return
        client_name = request_dict["Id"]

        url = str(self.get_kpc().decrypt(request_dict['Url']))
        url = urlparse(url).netloc
        url = url.decode("utf-8")


        entries = []
        for entry in self.server.backend.search_entries("url", url):
            json_entry = entry.to_json_dict(self.get_response_kpc())
            entries.append(json_entry)

        self.update_response_dict(success=True, entries=entries)
        self.set_verifier(client_name)

class GetLoginsCountRequest(Request):

    def process(self, request_dict):
        try:
            self.authenticate(request_dict)
        except AuthenticationError as unused_e:
            return
        client_name = request_dict["Id"]
        url = self.get_kpc().decrypt(request_dict['Url'])
        url = url.decode("utf-8")

        entries = self.server.backend.search_entries("url", url)

        self.update_response_dict(success=True,
                                  count=len(entries))

        self.set_verifier(client_name)


class SetLoginRequest(Request):

    def process(self, request_dict):
        try:
            self.authenticate(request_dict)
        except AuthenticationError as unused_e:
            return

        kpc = self.get_kpc()

        url = kpc.decrypt(request_dict['SubmitUrl'])
        login = kpc.decrypt(request_dict['Login'])
        password = kpc.decrypt(request_dict['Password'])

        self.server.backend.create_login(request_dict["Id"], login, password, url)

        self.update_response_dict(success=True)
