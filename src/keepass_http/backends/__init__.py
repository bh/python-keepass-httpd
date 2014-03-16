import abc
import mimetypes

from urlparse import urlparse

from keepass import kpdb

from .. import libkeepass
from lxml import etree, objectify
import uuid
import base64

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


class Backend:
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


class KeePassHTTPBackend(Backend):
    for_mimetype = "application/x-keepass-database-v1"

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
        self.save()
        self.sync_entries()

    def save(self):
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

class KeePass2HTTPBackend(Backend):
    for_mimetype = "application/x-keepass-database-v2"

    def _ignore_entry(self, uuid):
        if uuid == "00000000000000000000000000000000":
            return True
        return False

    def open_database(self):
        with libkeepass.open(self.database_path, password=self.passphrase) as kdb:
            return kdb

    def sync_entries(self):
        self.entries.purge()
        
        dbEntries = self.database.obj_root.xpath('//Group/Entry')

        # print "syncing entries " + str(len(dbEntries))

        for e in dbEntries:

            # print etree.tostring(e, pretty_print=True)

            title = ""
            if len(e.xpath("String[Key='Title']/Value")) > 0:
                title = str(e.xpath("String[Key='Title']/Value")[0])

            uuid = "00000000000000000000000000000000"
            if len(e.xpath("UUID")) > 0:
                uuid = str(e.xpath("UUID")[0])

            login = ""
            if len(e.xpath("String[Key='UserName']/Value")) > 0:
                login = str(e.xpath("String[Key='UserName']/Value")[0])

            password = ""
            if len(e.xpath("String[Key='Password']/Value")) > 0:
                password = str(e.xpath("String[Key='Password']/Value")[0])
            
            url = ""
            if len(e.xpath("String[Key='URL']/Value")) > 0:                
                url = str(e.xpath("String[Key='URL']/Value")[0])
            
            # print "login: " + repr(login)
            # print "password: " + repr(password)
            # print "url: " + repr(url)
            # print "uuid: " + repr(uuid)
            # print "title: " + repr(title)
            

            if self._ignore_entry(uuid):
                continue

            
            entry_spec = EntrySpec(title=title, uuid=uuid, login=login, password=password, url=url)
            self.entries.push(entry_spec)

        return

    def add_entry(self, path, title, username="", password="", url="", notes=""):
        print "adding entry"
        # search if group path exists, if not, create it
        groups = path.split("/")
        lastIndex = len(groups) - 1
            
        # handle groups - check if exists and if not, create group
        xpathString = '/KeePassFile/Root/Group[Name="Root"]'
        prevXPathString = xpathString

        latestGroups = self.database.obj_root.xpath(xpathString)
        
        deepestGroup = 0

        for i in range(0, lastIndex):
            print str(i) + " / " + str(lastIndex)
            prevXPathElement = self.database.obj_root.xpath(xpathString)
            xpathString += '/Group[Name="'+groups[i]+'"]'
            print xpathString
            groupEl = self.database.obj_root.xpath(xpathString)
            deepestGroup = groupEl[0]
            if len(groupEl) == 0:
                if len(prevXPathElement) > 0:
                    newGroupEl = etree.SubElement(prevXPathElement[0], "Group")
                    newGroupEl.Name = groups[i]
                    newGroupEl.UUID = base64.b64encode(uuid.uuid4().bytes)
                    print "created group " + groups[i]
                    deepestGroup = newGroupEl

            print "------------------------"
        
        print "creating element " + groups[lastIndex]
        # create entry
        entry = etree.SubElement(deepestGroup, "Entry")
        entry.UUID = base64.b64encode(uuid.uuid4().bytes)
        self.entryEl_add_stringattribute(entry, "Title", groups[lastIndex])
        self.entryEl_add_stringattribute(entry, "Username", username)
        self.entryEl_add_stringattribute(entry, "Password", password)
        self.entryEl_add_stringattribute(entry, "URL", url)

        # print etree.tostring(entry, pretty_print=True)

        objectify.deannotate(self.database.obj_root, cleanup_namespaces=True)
        self.save()


    def entryEl_add_stringattribute(self, entryEl, attributeName, attributeValue):
        elString = etree.SubElement(entryEl, "String")

        elStringKey = etree.SubElement(elString, "Key")
        elStringValue = etree.SubElement(elString, "Value")

        elString.Key = attributeName
        elString.Value = attributeValue.encode("utf-8")

    def save(self):
        print "saving"
        with open(self.database_path, 'wb') as output:
            self.database.write_to(output)

    def create_config_key(self, client_name, client_key):
        print "creating config key"
        self.add_entry(path="Python Keepass HTTP/%s" % client_name,
                       title=client_name,
                       password=client_key)

    def create_login(self, client_name, login, password, url):
        print "creating login"
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


def get_backend_by_file(filepath):
    mimetype = mimetypes.guess_type(filepath)[0]

    for backend in Backend.__subclasses__():
        if backend.for_mimetype == mimetype:
            return backend

    raise NoBackendError("No backend for file: %s" % filepath)
