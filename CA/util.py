from CA.routing_packet import RoutingPacket


INF = 'inf'

ports = {
    0: 1111,
    1: 2222,
    2: 3333,
    3: 4444
}

base_cost = {
    0: [0, 1, 3, 7],
    1: [1, 0, 1, INF],
    2: [3, 1, 0, 2],
    3: [7, INF, 2, 0],
}


def make_routing_table(neighbors: list, nodes: list = None):
    if nodes is None:
        nodes = [0, 1, 2, 3]

    table = {i: [INF] * len(nodes) for i in neighbors}
    return table
