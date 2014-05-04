# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import getpass
import logging

from keepass_http import backends
from keepass_http.core import Conf
from keepass_http.utils import query_yes_no

log = logging.getLogger(__name__)


class ClientConnectDecisionUi(object):

    @staticmethod
    def do():
        client_name = None
        if query_yes_no("Should be the client accepted?", default="no") == "yes":
            # TODO: handle an empty string
            client_name = raw_input("Give the client a name: ")
        return client_name


class RequireDatabasePassphraseUi(object):

    @staticmethod
    def do(max_try_count):
        kpconf = Conf()
        try_count = 1
        success = False
        while try_count <= max_try_count:
            passphrase = getpass.getpass("Please enter the passphrase for database %s: \n" %
                                         kpconf.backend.database_path)
            try:
                kpconf.backend.open_database(passphrase)
            except backends.WrongPassword:
                log.info("Wrong passphrase, please try again. (attempt [%s/%s]" % (try_count,
                                                                                   max_try_count))
                try_count += 1
            else:
                success = True
                log.info("Passphrase accepted")
                break

        return success
