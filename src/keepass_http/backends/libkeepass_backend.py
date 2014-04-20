# -*- coding: utf-8 -*-
import base64
import uuid
from urlparse import urlparse

import libkeepass
from lxml import etree, objectify

from keepass_http.backends import BaseBackend, EntrySpec, WrongPassword


class Backend(BaseBackend):

    def _ignore_entry(self, uuid):
        if uuid == "00000000000000000000000000000000":
            return True
        return False

    def open_database(self, passphrase):
        try:
            with libkeepass.open(self.database_path, password=passphrase) as kdb:
                self.database = kdb
        except IOError:
            raise WrongPassword("Incorrect password")

    def sync_entries(self):
        self.entries.purge()

        db_entries = self.database.obj_root.xpath('//Group/Entry')
        for entry in db_entries:
            el_uuid = "00000000000000000000000000000000"
            if len(entry.xpath("UUID")) > 0:
                el_uuid = entry.find("UUID").text

            if self._ignore_entry(el_uuid):
                continue

            title = entry.find("String[Key='Title']/Value").text or ""
            login = entry.find("String[Key='UserName']/Value").text or ""
            password = entry.find("String[Key='Password']/Value").text or ""
            url = entry.find("String[Key='URL']/Value").text or ""

            entry_spec = EntrySpec(
                uuid=el_uuid,
                title=title,
                login=login,
                password=password,
                url=url)
            self.entries.push(entry_spec)

    def add_entry(self, path, title, username="", password="", url="", notes=""):
        # handle groups - check if exists and if not, create group
        xpathstring = '/KeePassFile/Root/Group[Name="Root"]'

        deepest_group = 0
        # search if group path exists, if not, create it
        groups = path.split("/")
        for group in groups:
            #group =  groups[i]
            # FIXME: use .find()
            prev_xpath_element = self.database.obj_root.xpath(xpathstring)
            xpathstring = '%s/Group[Name="%s"]' % (xpathstring, group)

            group_el = self.database.obj_root.xpath(xpathstring)
            if not group_el:
                if prev_xpath_element:
                    new_group_el = etree.SubElement(prev_xpath_element[0], "Group")
                    new_group_el.Name = group
                    new_group_el.UUID = base64.b64encode(uuid.uuid4().bytes)
                    deepest_group = new_group_el
            else:
                deepest_group = group_el[0]

        # create entry
        entry = etree.SubElement(deepest_group, "Entry")
        entry.UUID = base64.b64encode(uuid.uuid4().bytes)
        self._entry_el_add_stringattribute(entry, "Title", title.decode("utf-8"))
        self._entry_el_add_stringattribute(entry, "UserName", username.decode("utf-8"))
        self._entry_el_add_stringattribute(entry, "Password", password.decode("utf-8"))
        self._entry_el_add_stringattribute(entry, "URL", url.decode("utf-8"))

        objectify.deannotate(self.database.obj_root, cleanup_namespaces=True)

        self._save()

    def _entry_el_add_stringattribute(self, entry_el, attribute_name, attribute_value):
        elString = etree.SubElement(entry_el, "String")

        etree.SubElement(elString, "Key")
        elString.Key = attribute_name

        etree.SubElement(elString, "Value")
        elString.Value = attribute_value.encode("utf-8")

    def _save(self):
        self.sync_entries()
        with open(self.database_path, 'wb') as output:
            self.database.write_to(output)

    def create_config_key(self, client_name, client_key):
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

    def get_key_for_client(self, client_name):
        self.sync_entries()
        try:
            entry = self.entries.search_by_field("title", client_name)
            key = entry[0].password
        except IndexError:
            return None
        else:
            return key
