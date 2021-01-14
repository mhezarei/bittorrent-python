import socket

from CA.util import *
from CA.routing_packet import *

ROUTER_ID = 0


def init():
    # Find the neighbors e.g. each node with a non-infinite cost
    neighbors = [i for i, cost in enumerate(base_cost) if
                 cost != INF and i != ROUTER_ID]
    table = make_routing_table(neighbors)

    # The initialization DV
    table[ROUTER_ID] = base_cost[ROUTER_ID]

    # Transfer to each neighbor
    for n in neighbors:
        transfer(RoutingPacket(ROUTER_ID, n, table[ROUTER_ID]))

    print(f"Made the initial routing table for node {ROUTER_ID} and sent it "
          f"to all the neighbors")

    return table


def update(dv: list):
    # TODO DEPLOY THE ALGORITHM USING THE INPUT DV
    pass


def transfer(rp: RoutingPacket) -> None:
    src = rp.src_router
    dest = rp.dest_router

    s = socket.socket()
    s.connect(('127.0.0.1', ports[dest]))

    # TODO SEND THE PACKET
    # s.send()

    s.close()


def socket_init():
    # Create the corresponding socket and return it
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', ports[ROUTER_ID]))
    s.listen(5)

    return s


def main():
    s = socket_init()
    table = init()

    # Keep listening for updates
    while True:
        c, addr = s.accept()
        print(c, addr)
        dv = c.recv(1024)

        # TODO CALL UPDATE AND UPDATE THE ROUTING TABLE USING THE DATA
        # update(dv)

        c.close()


if __name__ == '__main__':
    main()
