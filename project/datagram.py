from __future__ import annotations
import yaml

MAX_DATA_SIZE = 65507


class UDPDatagram:
    def __init__(self, src_port: int, dest_port: int, data: bytes):
        assert 0 < len(data) <= MAX_DATA_SIZE, print(
            f"The data length should be bigger than 0 bytes "
            f"and lower than or equal to {MAX_DATA_SIZE} bytes.")

        self.src_port = src_port
        self.dest_port = dest_port
        self.data = data

    def encode(self) -> bytes:
        return yaml.dump(self).encode()

    @staticmethod
    def decode(data: bytes) -> UDPDatagram:
        return yaml.full_load(data)
