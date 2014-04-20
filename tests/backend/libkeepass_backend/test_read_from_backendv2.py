# -*- coding: utf-8 -*-
import os
import shutil

from keepass_http.backends import EntrySpec
from keepass_http.backends.libkeepass_backend import Backend

TEST_DATA_ROOT = os.path.join(os.path.normpath(os.path.dirname(__file__)), "test_data")


def _move_test_file_to_tmpdir(_tmpdir, file_name):
    test_file = os.path.join(TEST_DATA_ROOT, file_name)
    shutil.copy(test_file, str(_tmpdir))
    return os.path.join(str(_tmpdir), file_name)


def test_unicode_characters_correctly_read(tmpdir):
    test_database = _move_test_file_to_tmpdir(tmpdir, "test_unicode_handling.kdbx")

    backend = Backend(test_database)
    backend.open_database("abcd123")

    backend.sync_entries()

    the_login = u'blaf\xf1oo'
    the_url = u'http://www.unicodeinurl\xf1.com'
    # keepassx currently doesn't support unicode in password field -
    # https://www.keepassx.org/dev/issues/158
    the_password = 'blanblan'
    the_title = u'Unicode fu\xf1'
    the_uuid = ''

    backend.entries.items[0].uuid = ''

    assert backend.entries.items[0] == EntrySpec(login=the_login,
                                                 url=the_url,
                                                 password=the_password,
                                                 title=the_title,
                                                 uuid=the_uuid)


def test_fetch_entries_empty_database(tmpdir):
    test_database = _move_test_file_to_tmpdir(tmpdir, "empty.kdbx")

    backend = Backend(test_database)
    backend.open_database("abcd123")

    backend.sync_entries()
    assert len(backend.entries.items) == 0


def test_create_config(tmpdir):
    test_database = _move_test_file_to_tmpdir(tmpdir, "test_create_config.kdbx")

    backend = Backend(test_database)
    backend.open_database("abcd123")

    backend.sync_entries()
    assert len(backend.entries.items) == 0

    backend.create_config_key("test_name", "test_key")
    assert len(backend.entries.items) == 1
    assert backend.entries.items.pop() == EntrySpec(login="",
                                                    url='',
                                                    password='test_key',
                                                    title='test_name',
                                                    uuid="")


def test_get_config(tmpdir):
    test_database = _move_test_file_to_tmpdir(tmpdir, "test_get_config.kdbx")

    backend = Backend(test_database)
    backend.open_database("abcd123")

    # existing associated client
    assert backend.get_key_for_client("test_name") == "test_key"

    # unknown client
    assert backend.get_key_for_client("test_unknown") is None


def test_create_login(tmpdir):
    test_database = _move_test_file_to_tmpdir(tmpdir, "test_create_login.kdbx")

    backend = Backend(test_database)
    backend.open_database("abcd123")

    backend.sync_entries()
    assert len(backend.entries.items) == 1
    # valid logins
    backend.create_login("test_name", "bla@gmail.com", "geheim", u"https://www.google.com/login")
    # 2 accounts, same domain
    backend.create_login("test_name", "blubb@gmx.net", "geheim2", u"https://gmx.net/login")
    backend.create_login("test_name", "blubb2@gmx.net", "geheim3", u"https://gmx.net/login")
    # another login
    backend.create_login("test_name", "asdasd@web.de", "geheim4", u"http://web.de/login/form.php")
    # x.get_entries(purge_cache=True)

    assert len(backend.entries.items) == 5

    # FIXME: remove config for client!
    del backend.entries.items[0]
    # first one is the client config (key)
    #
    assert backend.entries.items[0] == EntrySpec(login="bla@gmail.com",
                                                 url='https://www.google.com/login',
                                                 password='geheim',
                                                 title=u"www.google.com",
                                                 uuid="")
    assert backend.entries.items[1] == EntrySpec(login="blubb@gmx.net",
                                                 url='https://gmx.net/login',
                                                 password='geheim2',
                                                 title=u"gmx.net",
                                                 uuid="")
    assert backend.entries.items[2] == EntrySpec(login="blubb2@gmx.net",
                                                 url='https://gmx.net/login',
                                                 password='geheim3',
                                                 title=u"gmx.net",
                                                 uuid="")
    assert backend.entries.items[3] == EntrySpec(login="asdasd@web.de",
                                                 url='http://web.de/login/form.php',
                                                 password='geheim4',
                                                 title=u"web.de",
                                                 uuid="")


def test_get_search_entries(tmpdir):
    test_database = _move_test_file_to_tmpdir(tmpdir, "test_search_for_entries.kdbx")

    backend = Backend(test_database)
    backend.open_database("abcd123")

    backend.sync_entries()
    assert len(backend.entries.items) == 5

    # FIXME: remove config for client!
    # first one is the client config (key)
    del backend.entries.items[0]

    results = backend.search_entries("url", "https://www.google.com/login")
    assert len(results) == 1

    results = backend.search_entries("url", "https://gmx.net/login")
    assert len(results) == 2

    results = backend.search_entries("url", "http://web.de/login/form.php")
    assert len(results) == 1
