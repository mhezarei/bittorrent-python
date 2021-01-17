import json
import random
import threading
from project.utils import *
from project.node import Node

class Tracker:
    def __init__(self):
        self.nodes = []
        self.open_ports = (1024, 49151)  # available user ports
        self.tracker_s = create_socket(TRACKER_PORT)

    def add_node(self, node: Node):
        self.nodes.append(node)

    def give_port(self) -> int:
        rand_port = random.randint(self.open_ports[0], self.open_ports[1])
        return rand_port

    def handle_node(self, data, addr):
        packet = json.loads(data.decode())
        packet_mode = packet['mode']
        s = create_socket(self.give_port())
        s.sendto(b"received", (addr[0], addr[1]))
        s.close()

    def listen(self):
        while True:
            data, addr = self.tracker_s.recvfrom(1024)
            t = threading.Thread(target=self.handle_node(data, addr))
            t.start()

    def start(self):
        t = threading.Thread(target=self.listen())
        t.daemon = True
        t.start()
        t.join()


def main():
    t = Tracker()
    t.start()


if __name__ == '__main__':
    main()
