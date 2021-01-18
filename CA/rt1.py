import threading
import time
from CA.utils import *
from CA.routing_packet import *

ROUTER_ID = get_router_id(__file__)


def init() -> (dict, list):
    # Find the neighbors e.g. each node with a non-infinite cost
    neighbors = [i for i, cost in enumerate(base_cost[ROUTER_ID]) if
                 cost != INF and i != ROUTER_ID]
    table = make_routing_table(neighbors)

    # The initialization DV
    table[ROUTER_ID] = base_cost[ROUTER_ID]

    return table, neighbors


def update(table: dict, dv: list, src_router: int) -> dict:
    print('items : ', table.get(src_router), ' from : ', src_router)
    pass


def transfer_all_neighbors(neighbors, table):
    # Transfer to each neighbor
    for n in neighbors:
        transfer(RoutingPacket(ROUTER_ID, n, table[ROUTER_ID]))

    print(f"Made the initial routing table for node {ROUTER_ID} and sent it "
          f"to all the neighbors.")


def transfer(rp: RoutingPacket) -> None:
    dest = rp.dest_router
    send_s = create_socket(send_ports[ROUTER_ID])
    send_s.sendto(rp.encode(), ('localhost', rec_ports[dest]))
    send_s.close()


def listen(s, table):
    # Keep listening for updates
    while True:
        c, addr = s.recvfrom(1024)
        rp = pickle.loads(c)
        print(f"In router {ROUTER_ID}, received DV={rp.min_cost} "
              f"from (ip:{addr[0]}, port:{addr[1]}) which is router {rp.src_router}.")

        # TODO CALL UPDATE AND UPDATE THE ROUTING TABLE USING THE DATA
        update(table, rp.min_cost, rp.src_router)


def main():
    rec_sock = create_socket(rec_ports[ROUTER_ID])
    table, neighbors = init()
    t = threading.Thread(target=listen, args=(rec_sock, table))
    t.start()
    time.sleep(SLEEP_SECS)
    transfer_all_neighbors(neighbors, table)


if __name__ == '__main__':
    main()
