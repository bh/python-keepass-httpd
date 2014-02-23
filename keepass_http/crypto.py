import base64

from Crypto.Cipher import AES


class AESEncryption(object):
    BLOCKSIZE = 32

    def __init__(self, key, iv):
        self.key = base64.b64decode(key)
        self.iv = base64.b64decode(iv)

    @staticmethod
    def padding(string):
        return string + (AESEncryption.BLOCKSIZE - len(string) % AESEncryption.BLOCKSIZE) \
            * chr(AESEncryption.BLOCKSIZE - len(string) % AESEncryption.BLOCKSIZE)

    @staticmethod
    def unpad(string):
        return string[0:-ord(string[-1])]

    def encrypt(self, message):
        message = self.padding(message)
        encrypted_message = AES.new(self.key, AES.MODE_CBC, self.iv).encrypt(message)
        return base64.b64encode(encrypted_message)

    def decrypt(self, encrypted_message):
        encrypted_message = base64.b64decode(encrypted_message)
        message = AES.new(self.key, AES.MODE_CBC, self.iv).decrypt(encrypted_message)
        return self.unpad(message)

    def is_valid(self, iv, verifier):
        return iv == self.decrypt(verifier)
