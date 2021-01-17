import json
import random
import threading
from typing import Tuple

from project.messages.message import Message
from project.utils import *
from collections import defaultdict
from project.node import Node
from project.messages import modes
from project.messages.tracker_to_node import TrackerToNode

DEBUG_MODE = True


class Tracker:
    def __init__(self):
        self.nodes = []
        self.open_ports = (1024, 49151)  # available user ports
        self.tracker_s = create_socket(TRACKER_ADDR[1])
        self.uploader_list = defaultdict(list)

    def add_node(self, node: Node):
        self.nodes.append(node)

    def give_port(self) -> int:
        rand_port = random.randint(self.open_ports[0], self.open_ports[1])
        return rand_port

    def send_datagram(self, message: bytes, addr: Tuple[str, int]):
        dg = UDPDatagram(port_number(self.tracker_s), addr[1], message)
        self.tracker_s.sendto(dg.encode(), addr)

    def handle_node(self, data, addr):
        dg = UDPDatagram.decode(data)
        message = Message.decode(dg.data)
        print(message)
        message_mode = message['mode']
        if message_mode == modes.HAVE:
            self.add_uploader(message, addr)
        elif message_mode == modes.NEED:
            self.search_file(message, addr)
        elif message_mode == modes.EXIT:
            # TODO ADD EXIT
            pass

    def listen(self):
        while True:
            data, addr = self.tracker_s.recvfrom(1024)
            t = threading.Thread(target=self.handle_node, args=(data, addr))
            t.start()

    def start(self):
        t = threading.Thread(target=self.listen())
        t.daemon = True
        t.start()
        t.join()

    def add_uploader(self, message, addr):
        node_name = message['name']
        filename = message['filename']
        item = {
            'name': node_name,
            'ip': addr[0],
            'port': addr[1]
        }
        self.uploader_list[filename].append(json.dumps(item))
        self.uploader_list[filename] = list(set(self.uploader_list[filename]))
        if DEBUG_MODE:
            print(f"Current uploader list:\n{self.uploader_list}")

    def search_file(self, message, addr):
        node_name = message['name']
        filename = message['filename']
        search_result = []
        for item_json in self.uploader_list[filename]:
            item = json.loads(item_json)
            search_result.append((item['name'], (item['ip'], item['port'])))

        response = TrackerToNode(node_name, search_result, filename).encode()
        self.send_datagram(response, addr)


def main():
    t = Tracker()
    t.start()


if __name__ == '__main__':
    main()
