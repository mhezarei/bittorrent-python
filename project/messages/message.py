import yaml


class Message:
    def __init__(self):
        pass

    def encode(self) -> bytes:
        return yaml.dump(self.__dict__).encode()

    @staticmethod
    def decode(data: bytes):
        return yaml.full_load(data)
