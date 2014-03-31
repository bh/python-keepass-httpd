# -*- coding: utf-8 -*-
import pytest

from keepass_http.crypto import AESCipher


def test_aes_ok_decrypt():
    saved_key = "thT80v8XOBJaFZ85wmP05TdqSX/BB4lVTIvGuac/vgE="

    request_nonce = "I3AWYKKIgTtchOGCHwNi6A=="
    request_verifer = "eij8zQB61XVoh36SisyTDFbmh5J88oVzq/gVpOKQHQM="

    encrypted_message = "LTvHK1ctTVFVT9APqW6jhwKtdsZ5Vu21Pa79pLV4b+Y="

    kpc = AESCipher(saved_key, request_nonce)
    assert kpc.is_valid(request_nonce, request_verifer)

    assert kpc.decrypt(encrypted_message) == "https://webmail.gurkenbruehe.de"


def test_aes_ok_encrypt():
    saved_key = "thT80v8XOBJaFZ85wmP05TdqSX/BB4lVTIvGuac/vgE="

    request_nonce = "I3AWYKKIgTtchOGCHwNi6A=="
    request_verifer = "eij8zQB61XVoh36SisyTDFbmh5J88oVzq/gVpOKQHQM="

    message = "https://webmail.gurkenbruehe.de"

    kpc = AESCipher(saved_key, request_nonce)
    assert kpc.is_valid(request_nonce, request_verifer)
    assert kpc.encrypt(message) == "LTvHK1ctTVFVT9APqW6jhwKtdsZ5Vu21Pa79pLV4b+Y="
