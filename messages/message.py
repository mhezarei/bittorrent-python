from __future__ import annotations
import pickle


class Message:
    def __init__(self):
        pass

    def encode(self) -> bytes:
        return pickle.dumps(self.__dict__)

    @staticmethod
    def decode(data: bytes) -> dict:
        return pickle.loads(data)
