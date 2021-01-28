import os
from cryptography.fernet import Fernet
from datagram import UDPDatagram


class CryptographyUnit:
    def __init__(self):
        if os.path.isfile("crypto/key.key"):
            print("Found the key!")
            self.key = open("crypto/key.key", "rb").read()
        else:
            print("Key not found! Making a new one.")
            self.key = Fernet.generate_key()
            with open("crypto/key.key", "wb") as f:
                f.write(self.key)

    def encrypt(self, obj: UDPDatagram) -> bytes:
        f = Fernet(self.key)
        enc = f.encrypt(obj.encode())
        return enc

    def decrypt(self, data: bytes) -> UDPDatagram:
        f = Fernet(self.key)
        dec = f.decrypt(data)
        return UDPDatagram.decode(dec)


crypto_unit = CryptographyUnit()
