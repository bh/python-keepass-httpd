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
        self.__kpc = None
        self.__response_kpc = None
        self.__request_dict = {}
        self.__response_dict = {"Success": False}

    @property
    def response_dict(self):
        return self.__response_dict

    @property
    def request_dict(self):
        return self.__request_dict

    def get_client_id(self):
        return self.request_dict.get("Id", None)

    @property
    def kpc(self):
        if not self.__kpc:
            raise NotAuthenticated()
        return self.__kpc

    @kpc.setter
    def set_kpc(self, kpc):
        self.__kpc = kpc

    @property
    def response_kpc(self):
        if not self.__response_kpc:
            raise NotAuthenticated()
        return self.__response_kpc

    @response_kpc.setter
    def set_response_kpc(self, kpc):
        self.__response_kpc = kpc

    @abc.abstractmethod
    def process(self, request_dict):
        """
        """

    def __call__(self, request_dict):
        self.request_dict.update(request_dict)
        self.process()
        return self.response_dict

    def authenticate(self):
        client_id = self.get_client_id()

        log.info("Authenticate client %s" % client_id)

        key = Conf().backend.get_key_for_client(client_id)
        # FIXME: Fix unit tests
        # Special case when methods used in unit test are not mocked correctly.
        # <TestAES name='AESCipher().key' id='25131856'> is not None :S
        if key is None or not isinstance(key, basestring):
            raise AuthenticationError()

        nonce = self.request_dict['Nonce']
        verifier = self.request_dict['Verifier']

        kpc = AESCipher(key, nonce)

        # wrong saved key in database -> force associate
        if not kpc.is_valid(nonce, verifier):
            raise InvalidAuthentication()

        self.set_kpc = kpc
        self.set_verifier()

    def set_verifier(self, new_client_id=None):
        if new_client_id:
            client_id = new_client_id
            key = Conf().backend.get_key_for_client(client_id)
            if not key:
                raise AuthenticationError()
        else:
            client_id = self.get_client_id()
            key = self.kpc.get_key()

        nonce = AESCipher.generate_nonce()
        response_kpc = AESCipher(key, nonce)

        self.response_dict.update({"Nonce": nonce, "Verifier": response_kpc.encrypt(nonce)})
        self.set_response_kpc = response_kpc


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


class AssociateRequest(Request):

    def process(self):
        kpconf = Conf()
        new_client_id = kpconf.get_selected_ui().ClientConnectDecisionUi.do()
        if new_client_id:
            kpconf.backend.create_config_key(new_client_id, self.request_dict["Key"])
            self.response_dict.update({"Id": new_client_id,
                                       "Success": True})

            self.set_verifier(new_client_id)


class GetLoginsRequest(Request):

    def process(self):
        try:
            self.authenticate()
        except AuthenticationError as unused_e:
            return

        url = str(self.kpc.decrypt(self.request_dict['Url']))
        url = urlparse(url).netloc
        url = url.decode("utf-8")

        entries = []
        for entry in Conf().backend.search_entries("url", url):
            json_entry = entry.to_json_dict(self.response_kpc)
            entries.append(json_entry)

        self.response_dict.update({"Success": True, "Id": self.get_client_id(), "Entries": entries})


class GetLoginsCountRequest(Request):

    def process(self):
        try:
            self.authenticate()
        except AuthenticationError as unused_e:
            return
        url = self.kpc.decrypt(self.request_dict['Url'])
        url = url.decode("utf-8")

        entries = Conf().backend.search_entries("url", url)

        self.response_dict.update({"Success": True, "Count": len(entries)})


class SetLoginRequest(Request):

    def process(self):
        try:
            self.authenticate()
        except AuthenticationError as unused_e:
            return

        url = self.kpc.decrypt(self.request_dict['SubmitUrl'])
        login = self.kpc.decrypt(self.request_dict['Login'])
        password = self.kpc.decrypt(self.request_dict['Password'])

        Conf().backend.create_login(self.get_client_id(), login, password, url)

        self.response_dict.update({"Success": True})
