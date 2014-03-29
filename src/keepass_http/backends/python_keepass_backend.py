from urlparse import urlparse

from keepass import kpdb

from keepass_http.backends import EntrySpec

from . import BaseBackend, WrongPassword


class Backend(BaseBackend):
    #for_mimetype = "application/x-keepass-database-v1"

    def _ignore_entry(self, entry):
        if entry.uuid == "00000000000000000000000000000000":
            return True
        return False

    def open_database(self):
        try:
            return kpdb.Database(self.database_path, self.passphrase)
        except ValueError:
            raise WrongPassword("Incorrect password")

    def sync_entries(self):
        self.entries.purge()
        for entry in self.database.entries:

            if self._ignore_entry(entry):
                continue

            entry_spec = EntrySpec(title=entry.title, uuid=entry.uuid,
                                   login=entry.username, password=entry.password,
                                   url=entry.url)

            self.entries.push(entry_spec)

    def add_entry(self, path, title, username="", password="", url="", notes=""):
        self.sync_entries()
        self.database.add_entry(path.encode("utf-8"),
                                title.encode("utf-8"),
                                username.encode("utf-8"),
                                password.encode("utf-8"),
                                url.encode("utf-8"))
        self._save()
        self.sync_entries()

    def _save(self):
        self.database.write(self.database_path, self.passphrase)

    def create_config_key(self, client_name, client_key):
        self.add_entry(path="Python Keepass HTTP",
                       title=client_name,
                       password=client_key)

    def create_login(self, client_name, login, password, url):
        parse_url = urlparse(url)
        self.add_entry(path="Python Keepass HTTP/Logins/%s" % client_name,
                       title=parse_url.netloc,
                       username=login,
                       password=password,
                       url=url)

    def get_config(self, client_name):
        self.sync_entries()
        try:
            entry = self.entries.search_by_field("title", client_name)
            key = entry[0].password
        except IndexError:
            return None
        else:
            return key
