import pytest

from keepass_http.crypto import AESEncryption


def test_aes_ok_decrypt():
    saved_key = "thT80v8XOBJaFZ85wmP05TdqSX/BB4lVTIvGuac/vgE="

    request_nonce = "I3AWYKKIgTtchOGCHwNi6A=="
    request_verifer = "eij8zQB61XVoh36SisyTDFbmh5J88oVzq/gVpOKQHQM="

    encrypted_message = "LTvHK1ctTVFVT9APqW6jhwKtdsZ5Vu21Pa79pLV4b+Y="

    kpc = AESEncryption(saved_key, request_nonce)
    assert kpc.is_valid(request_nonce, request_verifer)

    assert kpc.decrypt(encrypted_message) == "https://webmail.gurkenbruehe.de"


def test_aes_corrupted_keys():
    request_nonce = "I3AWYKKIgTtchOGCHwNi6A=="
    request_verifer = "eij8zQB61XVoh36SisyTDFbmh5J88oVzq/gVpOKQHQM="

    # invalid keys
    with pytest.raises(TypeError):
        kpc = AESEncryption("sasdasdasdasdasdasdasdasdasdasdasdasdasdasdasdasdasdasdads",
                            request_nonce)
        kpc.is_valid(request_nonce, request_verifer)

    with pytest.raises(ValueError):
        kpc = AESEncryption("", request_nonce)
        kpc.is_valid(request_nonce, request_verifer)


def test_aes_decrypt_invalid_encrypted_string():
    saved_key = "thT80v8XOBJaFZ85wmP05TdqSX/BB4lVTIvGuac/vgE="

    request_nonce = "NVH+vcNiV+5yUC+B9pg1Dw=="
    request_verifer = "BD965euv4tfr36DRIXqbK6vAbrHfcELqMDRYyWKsYQo="

    encrypted_message = "8YYG/sHh3tNWmeqIwViiHO8AqWo5YsYGSh/StyaEt3U="

    kpc = AESEncryption(saved_key, request_nonce)
    assert kpc.is_valid(request_nonce, request_verifer) is True

    assert kpc.decrypt(encrypted_message) != "https://webmail.gurkenbruehe.de"


def test_aes_decrypt_wrong_nonce():
    saved_key = "thT80v8XOBJaFZ85wmP05TdqSX/BB4lVTIvGuac/vgE="

    request_nonce = "I3AWYKKIgTtchoGCHwNi6A=="
    request_verifer = "eij8zQB61XVoh36SisyTDFbmh5J88oVzq/gVpOKQHQM="

    encrypted_message = "LTvHK1ctTVFVT9APqW6jhwKtdsZ5Vu21Pa79pLV4b+Y="

    kpc = AESEncryption(saved_key, request_nonce)
    # save the result in a variable to make the assert work with py.test :S
    is_valid = kpc.is_valid(request_nonce, request_verifer)
    assert is_valid is False
    assert kpc.decrypt(encrypted_message) != "https://webmail.gurkenbruehe.de"


def test_aes_decrypt_wrong_key():
    saved_key = "ThT80v8XOBJaFZ85wmP05TdqSX/BB4lVTIvGuac/vgE="

    request_nonce = "I3AWYKKIgTtchOGCHwNi6A=="
    request_verifer = "eij8zQB61XVoh36SisyTDFbmh5J88oVzq/gVpOKQHQM="

    encrypted_message = "LTvHK1ctTVFVT9APqW6jhwKtdsZ5Vu21Pa79pLV4b+Y="

    kpc = AESEncryption(saved_key, request_nonce)
    # save the result in a variable to make the assert work with py.test :S
    is_valid = kpc.is_valid(request_nonce, request_verifer)
    assert is_valid is False

    assert kpc.decrypt(encrypted_message) == ""


def test_aes_ok_encrypt():
    saved_key = "thT80v8XOBJaFZ85wmP05TdqSX/BB4lVTIvGuac/vgE="

    request_nonce = "I3AWYKKIgTtchOGCHwNi6A=="
    request_verifer = "eij8zQB61XVoh36SisyTDFbmh5J88oVzq/gVpOKQHQM="

    message = "https://webmail.gurkenbruehe.de"

    kpc = AESEncryption(saved_key, request_nonce)
    assert kpc.is_valid(request_nonce, request_verifer)
    assert kpc.encrypt(message) == "LTvHK1ctTVFVT9APqW6jhwKtdsZ5Vu21Pa79pLV4b+Y="
