# -*- coding: utf-8 -*-
import abc
import mimetypes
import pkg_resources


class NoBackendError(Exception):
    pass


class WrongPassword(Exception):
    pass


class EntrySpec:

    def __init__(self, uuid, title, login, password, url):
        self.uuid = uuid
        self.title = title
        self.username = login
        self.password = password
        self.url = url

    def to_json_dict(self, kpc):
        return {"Name": kpc.encrypt(self.title.encode("utf-8")),
                "Login": kpc.encrypt(self.username.encode("utf-8")),
                "Uuid": kpc.encrypt(self.uuid.encode("utf-8")),
                "Password": kpc.encrypt(self.password.encode("utf-8")),
                }

    def __eq__(self, other):
        # FIXME: uuid handling?
        return all([  # self.uuid == other.uuid,
                   self.title == other.title,
                   self.username == other.username,
                   self.password == other.password,
                   self.url == other.url])


class Entries:

    def __init__(self):
        self.items = []

    def push(self, entry):
        assert isinstance(entry, EntrySpec)
        self.items.append(entry)

    def search_by_field(self, field, value):
        results = []
        for entry in self.items:
            if value in getattr(entry, field):
                results.append(entry)
        return results

    def purge(self):
        self.items = []


class BaseBackend(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, database_path):

        self.database_path = database_path
        self.passphrase = None
        self.database = None

        self.entries = Entries()

    @classmethod
    def get_by_filepath(cls, filepath):
        mimetype = mimetypes.guess_type(filepath)[0]

        if mimetype is None:
            raise NoBackendError("Unknown mimetype for file: %s" % filepath)

        backends = list(
            pkg_resources.iter_entry_points(
                group='keepass_http_backends',
                name=mimetype))

        if not len(backends):
            raise NoBackendError("No registered backend for file: %s" % filepath)

        backend = backends.pop().load()
        return backend(database_path=filepath)

    @abc.abstractmethod
    def open_database(self, database_path):
        """
        """

    @abc.abstractmethod
    def sync_entries(self):
        """
        """

    @abc.abstractmethod
    def add_entry(self, path, title, username, password, url):
        """
        """

    def search_entries(self, field, value):
        self.sync_entries()
        return self.entries.search_by_field(field, value)

    @abc.abstractmethod
    def create_config_key(self, client_name, client_key):
        """
        """

    @abc.abstractmethod
    def get_key_for_client(self):
        """
        """
