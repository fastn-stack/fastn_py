import base64
from Crypto.Cipher import AES
from hashlib import sha256


class AESCipher:
    """
    decrypt strings encrypted by magic_crypt default AES256 method

    https://github.com/magiclen/rust-magiccrypt
    """

    def __init__(self, key_str: str):
        key = sha256(bytes(key_str, "utf-8"))
        self.key = key.digest()

    def decrypt(self, enc_str: str) -> bytes:
        enc = base64.b64decode(enc_str)
        iv = bytearray(16)  # empty byte array used by fastn
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(enc))

    @staticmethod
    def unpad(s):
        return s[: -ord(s[len(s) - 1 :])]
