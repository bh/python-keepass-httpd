# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from keepass_http.utils import query_yes_no


class RequireAssociationDecision(object):

    @staticmethod
    def require_client_name():
        client_name = None
        if query_yes_no("Should be the client accepted?", default="no"):
            # TODO: handle an empty string
            client_name = raw_input("Give the client a name: ")
        return client_name

if __name__ == "__main__":  # pragma: no cover
    new_client_name = RequireAssociationDecision.require_client_name()
    print (new_client_name)
