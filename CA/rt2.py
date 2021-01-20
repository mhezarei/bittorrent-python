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


def update(table: dict, dv: list, src_router: int, neighbors: list) -> dict:
    table[src_router] = dv
    any_change = False
    for j in range(len(table.get(ROUTER_ID))):
        min_cost = min(float(table[ROUTER_ID][j]), (float(table[ROUTER_ID][src_router])) + (float(dv[j])))
        if table[ROUTER_ID][j] != min_cost:
            # Table modified
            any_change = True

        table[ROUTER_ID][j] = min_cost

    if any_change:
        # Transfer modified table to each neighbor
        transfer_all_neighbors(neighbors, table)

    return table


def transfer_all_neighbors(neighbors, table):
    # Transfer to each neighbor
    print("Sending updates to all the neighbors...\n")
    for n in neighbors:
        time.sleep(0.1)
        transfer(RoutingPacket(ROUTER_ID, n, table[ROUTER_ID]))


def transfer(rp: RoutingPacket) -> None:
    dest = rp.dest_router
    send_s = create_socket(send_ports[ROUTER_ID])
    send_s.sendto(rp.encode(), ('localhost', rec_ports[dest]))
    send_s.close()


def listen(s, table, neighbors):
    # Keep listening for updates
    while True:
        c, addr = s.recvfrom(1024)
        rp = pickle.loads(c)
        print(f"In router {ROUTER_ID}, received DV={rp.min_cost} "
              f"from (ip:{addr[0]}, port:{addr[1]}) which is router {rp.src_router}.\n")

        table = update(table, rp.min_cost, rp.src_router, neighbors)
        print_table(table)


def print_table(table: dict):
    print('Current table : ')
    print('   0    1    2    3')
    for row in table:
        print(row, table[row])
    print()


def main():
    rec_sock = create_socket(rec_ports[ROUTER_ID])
    table, neighbors = init()
    print_table(table)
    t = threading.Thread(target=listen, args=(rec_sock, table, neighbors))
    t.start()
    time.sleep(SLEEP_SECS)
    transfer_all_neighbors(neighbors, table)


if __name__ == '__main__':
    main()
