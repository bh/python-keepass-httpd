# -*- coding: utf-8 -*-
from keepass_http.backends import EntrySpec
from keepass_http.crypto import AESCipher


def test_entry_spec_unicode():
    saved_key = "thT80v8XOBJaFZ85wmP05TdqSX/BB4lVTIvGuac/vgE="

    request_nonce = "I3AWYKKIgTtchOGCHwNi6A=="
    request_verifer = "eij8zQB61XVoh36SisyTDFbmh5J88oVzq/gVpOKQHQM="

    kpc = AESCipher(saved_key, request_nonce)

    entry = EntrySpec(uuid=u"1", title=u"ä", login=u"ü",
                  password=u"ö", url=u"http://www.fuß.de/login/form.html")

    assert entry.to_json_dict(kpc)