import mmap
import socket
from random import randint
from typing import Tuple

MAX_DATA_SIZE = 65507
BUFFER_SIZE = 65536
TRACKER_ADDR = ('localhost', 12340)
open_ports = (1024, 49151)  # available user ports


def split_file(path: str, rng: Tuple[int, int],
               chunk_size: int = MAX_DATA_SIZE - 2000) -> list:
    assert chunk_size > 0, print("The chunk size should be bigger than 0.")
    
    # TODO get a part of the file and split it
    with open(path, "r+b") as f:
        # getting the specified range
        mm = mmap.mmap(f.fileno(), 0)[rng[0]: rng[1]]
        # diving the bytes into chunks
        ret = [mm[chunk: chunk + chunk_size] for chunk in
               range(0, rng[1] - rng[0], chunk_size)]
        return ret


def assemble_file(chunks: list, path: str) -> None:
    f = open(path, "bw+")
    for c in chunks:
        f.write(c)
    f.flush()
    f.close()


def give_port() -> int:
    rand_port = randint(open_ports[0], open_ports[1])
    return rand_port


def create_socket(port: int) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('localhost', port))
    return s


def port_number(s: socket.socket) -> int:
    return s.getsockname()[1]
