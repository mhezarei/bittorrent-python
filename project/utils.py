import socket
from project.datagram import *

TRACKER_ADDR = ('localhost', 12340)


def split_file(path: str, chunk_size: int = MAX_DATA_SIZE) -> list:
    assert chunk_size > 0, print("The chunk size should be bigger than 0.")

    ret = []
    with open(path, "rb") as f:
        parts = iter(lambda: f.read(chunk_size), '')
        for chunk in parts:
            if chunk == b'':
                break
            ret.append(chunk)

    return ret


def assemble_file(chunks: list, filename: str) -> None:
    f = open(f"files/{filename}", "wb+")
    for c in chunks:
        f.write(c)


def create_socket(port: int) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('localhost', port))
    return s


def port_number(s: socket.socket) -> int:
    return s.getsockname()[1]
