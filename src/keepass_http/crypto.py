# -*- coding: utf-8 -*-
import base64

from libkeepass import crypto as libkeepass_crypto


class AESCipher(object):

    def __init__(self, key, iv):
        self.key = base64.b64decode(key)
        self.iv = base64.b64decode(iv)

    def encrypt(self, message):
        message = libkeepass_crypto.pad(message)
        encrypted_message = libkeepass_crypto.aes_cbc_encrypt(message, self.key, self.iv)
        return base64.b64encode(encrypted_message)

    def decrypt(self, encrypted_message):
        encrypted_message = base64.b64decode(encrypted_message)
        message = libkeepass_crypto.aes_cbc_decrypt(encrypted_message, self.key, self.iv)
        return libkeepass_crypto.unpad(message)

    def is_valid(self, iv, verifier):
        return iv == self.decrypt(verifier)
