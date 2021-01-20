from __future__ import annotations
import pickle
from project.utils import MAX_DATA_SIZE


class UDPDatagram:
    def __init__(self, src_port: int, dest_port: int, data: bytes):
        assert 0 < len(data) <= MAX_DATA_SIZE, print(
            f"The data length should be bigger than 0 bytes "
            f"and lower than or equal to {MAX_DATA_SIZE} bytes.")
        
        self.src_port = src_port
        self.dest_port = dest_port
        self.data = data
    
    def encode(self) -> bytes:
        return pickle.dumps(self)
    
    @staticmethod
    def decode(data: bytes) -> UDPDatagram:
        return pickle.loads(data)
