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


class Request(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._kpc = None
        self._response_kpc = None
        self._request_dict = None
        self._response_dict = None

    def __call__(self, request_dict):
        self._request_dict = request_dict
        self.process()
        return self.response_dict

    @property
    def response_dict(self):
        if not self._response_dict:
            self._response_dict = {"Success": False}
        return self._response_dict

    @abc.abstractmethod
    def process(self, request_dict):
        """
        """

    def authenticate(self):
        client_id = self.get_client_id()
        log.info("Authenticate client %s" % client_id)

        key = Conf().backend.get_config(client_id)
        if not key:
            raise AuthenticationError()

        nonce = self._request_dict['Nonce']
        verifier = self._request_dict['Verifier']

        kpc = AESCipher(key, nonce)

        # wrong saved key in database -> force associate
        if not kpc.is_valid(nonce, verifier):
            raise InvalidAuthentication()

        self._kpc = kpc

    def set_verifier(self, new_client_id=None):
        client_id = new_client_id or self.get_client_id()

        key = Conf().backend.get_config(client_id)
        if not key:
            raise AuthenticationError("set_verifier - Could not set verifier: no valid "
                                      "key for client: %s " % client_id)
        nonce = AESCipher.generate_nonce()
        self._response_kpc = AESCipher(key, nonce)
        self.response_dict.update({"Nonce": nonce,
                                   "Verifier": self._response_kpc.encrypt(nonce)})

    def get_client_id(self):
        return self._request_dict.get("Id", None)

    def get_kpc(self):
        if not self._kpc:
            raise NotAuthenticated()
        return self._kpc

    def get_response_kpc(self):
        if not self._response_kpc:
            raise NotAuthenticated()
        return self._response_kpc


class TestAssociateRequest(Request):

    def process(self):
        client_id = self.get_client_id()
        # missing field -> force associate
        if not client_id:
            return

        # no auth -> force associate
        try:
            self.authenticate()
        except AuthenticationError as unused_e:
            return

        # already associated, all fine
        self.response_dict.update({"Id": client_id,
                                  "Success": True})

        self.set_verifier()


class AssociateRequest(Request):

    def process(self):

        kpconf = Conf()
        new_client_id = kpconf.get_selected_ui().RequireAssociationDecision.require_client_name()
        if new_client_id:
            kpconf.backend.create_config_key(new_client_id, self._request_dict["Key"])
            self.response_dict.update({"Id": new_client_id,
                                       "Success": True})

            self.set_verifier(new_client_id)


class GetLoginsRequest(Request):

    def process(self):
        try:
            self.authenticate()
        except AuthenticationError as unused_e:
            return

        url = str(self.get_kpc().decrypt(self._request_dict['Url']))
        url = urlparse(url).netloc
        url = url.decode("utf-8")

        entries = []
        self.set_verifier()
        for entry in Conf().backend.search_entries("url", url):
            json_entry = entry.to_json_dict(self.get_response_kpc())
            entries.append(json_entry)

        self.response_dict.update({"Success": True, "Id": self.get_client_id(), "Entries": entries})


class GetLoginsCountRequest(Request):

    def process(self):
        try:
            self.authenticate()
        except AuthenticationError as unused_e:
            return
        url = self.get_kpc().decrypt(self._request_dict['Url'])
        url = url.decode("utf-8")

        entries = Conf().backend.search_entries("url", url)

        self.response_dict.update({"Success": True, "Count": len(entries)})


class SetLoginRequest(Request):

    def process(self):
        try:
            self.authenticate()
        except AuthenticationError as unused_e:
            return

        kpc = self.get_kpc()

        url = kpc.decrypt(self._request_dict['SubmitUrl'])
        login = kpc.decrypt(self._request_dict['Login'])
        password = kpc.decrypt(self._request_dict['Password'])

        Conf().backend.create_login(self.get_client_id(), login, password, url)

        self.response_dict.update({"Success": True})
        self.set_verifier()
