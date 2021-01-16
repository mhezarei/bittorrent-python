import time
from CA.utils import *
from CA.routing_packet import *

ROUTER_ID = get_router_id(__file__)


def init() -> dict:
    # Find the neighbors e.g. each node with a non-infinite cost
    neighbors = [i for i, cost in enumerate(base_cost[ROUTER_ID]) if
                 cost != INF and i != ROUTER_ID]
    table = make_routing_table(neighbors)

    # The initialization DV
    table[ROUTER_ID] = base_cost[ROUTER_ID]

    # Transfer to each neighbor
    for n in neighbors:
        transfer(RoutingPacket(ROUTER_ID, n, table[ROUTER_ID]))

    print(f"Made the initial routing table for node {ROUTER_ID} and sent it "
          f"to all the neighbors.")

    return table


def update(dv: list):
    # TODO DEPLOY THE ALGORITHM USING THE INPUT DV
    pass


def transfer(rp: RoutingPacket) -> None:
    dest = rp.dest_router

    send_s = create_socket(send_ports[ROUTER_ID])
    send_s.connect(('127.0.0.1', rec_ports[dest]))
    send_s.send(rp.encode())
    send_s.close()


def main():
    rec_sock = create_socket(rec_ports[ROUTER_ID])
    rec_sock.listen(10)
    time.sleep(SLEEP_SECS)
    table = init()
    time.sleep(SLEEP_SECS)
    table = init()

    # Keep listening for updates
    while True:
        c, addr = rec_sock.accept()
        rp = pickle.loads(c.recv(1024))
        print(f"In router {ROUTER_ID}, received DV={rp.min_cost} "
              f"from port {addr[1]} which is router {rp.src_router}.")

        # TODO CALL UPDATE AND UPDATE THE ROUTING TABLE USING THE DATA
        # table = update(data, send_sock)


if __name__ == '__main__':
    main()
