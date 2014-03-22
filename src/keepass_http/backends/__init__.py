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
        return {"Name": kpc.encrypt(self.title),
                "Login": kpc.encrypt(self.username),
                "Uuid": kpc.encrypt(self.uuid),
                "Password": kpc.encrypt(self.password),
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


class BaseBackend:
    __metaclass__ = abc.ABCMeta

    def __init__(self, database_path, passphrase):

        self.database_path = database_path
        self.passphrase = passphrase
        self.database = self.open_database()

        self.entries = Entries()

    @abc.abstractmethod
    def open_database(self):
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
    def get_config(self):
        """
        """


def get_backend_by_file(filepath):
    mimetype = mimetypes.guess_type(filepath)[0]

    if mimetype is None:
        raise NoBackendError("No backend for file: %s" % filepath)

    backends = list(pkg_resources.iter_entry_points(group='keepass_http_backends', name=mimetype))

    if not len(backends):
        raise NoBackendError("No backend for file: %s" % filepath)

    return backends.pop().load()
