import json
import random
import threading
from project.datagram import UDPDatagram
from project.messages.message import Message
from project.utils import *
from collections import defaultdict
from project.node import Node
from project.messages import modes
from project.messages.tracker_to_node import TrackerToNode
import pprint


class Tracker:
    def __init__(self):
        self.nodes = []
        self.open_ports = (1024, 49151)  # available user ports
        self.tracker_s = create_socket(TRACKER_ADDR[1])
        self.uploader_list = defaultdict(list)
        self.upload_freq_list = defaultdict(int)

    def add_node(self, node: Node):
        self.nodes.append(node)

    def give_port(self) -> int:
        rand_port = random.randint(self.open_ports[0], self.open_ports[1])
        return rand_port

    def send_datagram(self, message: bytes, addr: Tuple[str, int]):
        dg = UDPDatagram(port_number(self.tracker_s), addr[1], message)
        self.tracker_s.sendto(dg.encode(), addr)

    def handle_node(self, data, addr):
        # print(data)
        dg = UDPDatagram.decode(data)
        # print(dg)
        message = Message.decode(dg.data)
        # print(message)
        message_mode = message['mode']
        if message_mode == modes.HAVE:
            self.add_uploader(message, addr)
        elif message_mode == modes.NEED:
            self.search_file(message, addr)
        elif message_mode == modes.EXIT:
            self.exit_uploader(message, addr)
            pass

    def listen(self):
        while True:
            data, addr = self.tracker_s.recvfrom(BUFFER_SIZE)
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
        self.upload_freq_list[node_name] = self.upload_freq_list[node_name] + 1
        self.uploader_list[filename].append(json.dumps(item))
        self.uploader_list[filename] = list(set(self.uploader_list[filename]))

        self.print_db()

    def search_file(self, message, addr):
        node_name = message['name']
        filename = message['filename']
        self.print_search_log(node_name, filename)

        search_result = []
        for item_json in self.uploader_list[filename]:
            item = json.loads(item_json)
            upload_freq = self.upload_freq_list[item['name']]
            search_result.append((item['name'], (item['ip'], item['port']), upload_freq))

        response = TrackerToNode(node_name, search_result, filename).encode()
        self.send_datagram(response, addr)

    def exit_uploader(self, message, addr):
        node_name = message['name']
        item = {
            'name': node_name,
            'ip': addr[0],
            'port': addr[1]
        }
        item_json = json.dumps(item)
        self.upload_freq_list[node_name] = 0
        files = self.uploader_list.copy()
        for file in files:
            if item_json in self.uploader_list[file]:
                self.uploader_list[file].remove(item_json)
            if len(self.uploader_list[file]) == 0:
                self.uploader_list.pop(file)
        self.print_db()

    def print_db(self):
        print('\n************************* Current Database *************************')
        print('* Upload frequency list :')
        pprint.pprint(self.upload_freq_list, width=1)
        print("\n* Files' uploader list :")
        pprint.pprint(self.uploader_list)
        print('********************************************************************')

    def print_search_log(self, node_name, filename):
        print('\n************************* Search Log *************************')
        print(f'{node_name} is searching for {filename}...')
        print('****************************************************************')


def main():
    t = Tracker()
    t.start()


if __name__ == '__main__':
    main()
