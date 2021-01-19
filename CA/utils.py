import re
import socket

SLEEP_SECS = 3
INF = 'inf'

send_ports = {
    0: 1111,
    1: 2222,
    2: 3333,
    3: 4444
}

rec_ports = {
    0: 1110,
    1: 2220,
    2: 3330,
    3: 4440
}

base_cost = {
    0: [0.0, 1.0, 3.0, 7.0],
    1: [1.0, 0.0, 1.0, INF],
    2: [3.0, 1.0, 0.0, 2.0],
    3: [7.0, INF, 2.0, 0.0],
}


def make_routing_table(neighbors: list, nodes: list = None) -> dict:
    if nodes is None:
        nodes = [0, 1, 2, 3]

    table = {i: [INF] * len(nodes) for i in neighbors}
    return table


def get_router_id(path: str) -> int:
    filename = str(path).split('/')[-1]
    filename = re.sub(r"[^\d]", "", filename)
    return int(filename)


def create_socket(port: int) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('localhost', port))
    return s
