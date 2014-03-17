import base64
import uuid
from urlparse import urlparse

from lxml import etree, objectify

import libkeepass
from keepass_http.backends import EntrySpec

from . import Backend


class KeePass2HTTPBackend(Backend):
    for_mimetype = "application/x-keepass-database-v2"

    def _ignore_entry(self, uuid):
        if uuid == "00000000000000000000000000000000":
            return True
        return False

    def open_database(self):
        with libkeepass.open(self.database_path, password=self.passphrase) as kdb:
            return kdb

    def extract_attribute_safe(self, xml_element):
        attribute_value = ""
        if len(xml_element) > 0:
                    attribute_value = xml_element[0].text
                    if attribute_value == None:
                        print "setting attribute to empty"
                        attribute_value = ""
        return attribute_value

    def sync_entries(self):
        self.entries.purge()

        db_entries = self.database.obj_root.xpath('//Group/Entry')
        try:
            for e in db_entries:
                el_uuid = "00000000000000000000000000000000"
                if len(e.xpath("UUID")) > 0:
                    el_uuid = e.xpath("UUID")[0].text

                if self._ignore_entry(el_uuid):
                    continue

                title = self.extract_attribute_safe(e.xpath("String[Key='Title']/Value"))
                login = self.extract_attribute_safe(e.xpath("String[Key='UserName']/Value"))
                password = self.extract_attribute_safe(e.xpath("String[Key='Password']/Value"))
                url = self.extract_attribute_safe(e.xpath("String[Key='URL']/Value"))

                entry_spec = EntrySpec(uuid=el_uuid, title=title, login=login, password=password, url=url)
                self.entries.push(entry_spec)
        except Exception as e:
            print e
        return

    def add_entry(self, path, title, username="", password="", url="", notes=""):
        # search if group path exists, if not, create it
        groups = path.split("/")
        last_index = len(groups) - 1

        # handle groups - check if exists and if not, create group
        xpathstring = '/KeePassFile/Root/Group[Name="Root"]'

        deepest_group = 0

        for i in range(0, last_index):
            prev_xpath_element = self.database.obj_root.xpath(xpathstring)
            xpathstring += '/Group[Name="'+groups[i]+'"]'
            group_el = self.database.obj_root.xpath(xpathstring)

            if len(group_el) == 0:
                if len(prev_xpath_element) > 0:
                    new_group_el = etree.SubElement(prev_xpath_element[0], "Group")
                    new_group_el.Name = groups[i]
                    new_group_el.UUID = base64.b64encode(uuid.uuid4().bytes)
                    deepest_group = new_group_el
            else:
                deepest_group = group_el[0]

        # create entry
        entry = etree.SubElement(deepest_group, "Entry")
        entry.UUID = base64.b64encode(uuid.uuid4().bytes)
        self.entry_el_add_stringattribute(entry, "Title", title)
        self.entry_el_add_stringattribute(entry, "UserName", username)
        self.entry_el_add_stringattribute(entry, "Password", password)
        self.entry_el_add_stringattribute(entry, "URL", url)

        objectify.deannotate(self.database.obj_root, cleanup_namespaces=True)

        self.save()

    def entry_el_add_stringattribute(self, entry_el, attributeName, attributeValue):
        elString = etree.SubElement(entry_el, "String")

        etree.SubElement(elString, "Key")
        etree.SubElement(elString, "Value")

        elString.Key = attributeName
        elString.Value = attributeValue.encode("utf-8")

    def save(self):
        self.sync_entries()
        with open(self.database_path, 'wb') as output:
            self.database.write_to(output)

    def create_config_key(self, client_name, client_key):
        print "creating config key " + client_name
        self.add_entry(path="Python Keepass HTTP/%s" % client_name,
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
