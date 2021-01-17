import os
import sys
from threading import Thread
from typing import Tuple

from project.messages.message import Message
from project.messages.node_to_tracker import NodeToTracker
from project.utils import *
from project.messages import modes


class Node:
    def __init__(self, name: str, rec_port: int, send_port: int):
        # TODO
        # send tracker the node_files each node has (in init).
        self.rec_s = create_socket(rec_port)
        self.send_s = create_socket(send_port)
        self.name = name
        self.sent_files_cnt = 0
        self.received_files_cnt = 0
        self.files = []
        self.set_filenames()

    def set_filenames(self):
        path = f"node_files/{self.name}"
        if os.path.isdir(path):
            _, _, self.files = next(os.walk(path))

    def send_datagram(self, message: bytes, addr: Tuple[str, int]):
        dg = UDPDatagram(port_number(self.send_s), addr[1], message)
        self.send_s.sendto(dg.encode(), addr)

    def search(self, filename: str) -> bytes:
        # wrap this packet in UDP datagram
        message = NodeToTracker(self.name, modes.NEED, filename).encode()
        self.send_datagram(message, TRACKER_ADDR)

        while True:
            data, addr = self.send_s.recvfrom(1024)
            dg = UDPDatagram.decode(data)
            # validate the data. it should be from the tracker.
            return Message.decode(dg.data)

    def download(self, filename: str):
        search_result = self.search(filename)
        print(search_result)
        # split the parts and assign each part to a node

    def set_upload(self, filename: str):
        # wrap this packet in UDP datagram
        message = NodeToTracker(self.name, modes.HAVE, filename).encode()
        self.send_datagram(message, TRACKER_ADDR)

    def exit(self):
        # tell tracker i want to go :(
        pass

    def start(self):
        pass
        # self.send_s.sendto(b"asdasdasd", (TRACKER_IP, TRACKER_PORT))
        # while True:
        #     data, addr = self.rec_s.recvfrom(1024)
        #     print(data, addr, self.rec_s.getsockname()[1])


def main(name: str, port1: int, port2: int):
    node = Node(name, port1, port2)
    # t = Thread(target=node.start)
    # t.setDaemon(True)
    # t.start()

    command = input()
    while True:
        if "upload" in command:
            # torrent -upload filename
            filename = command.split(' ')[2]
            node.set_upload(filename)
        elif "download" in command:
            # torrent -download filename
            filename = command.split(' ')[2]
            t2 = Thread(target=node.download, args=(filename,))
            t2.setDaemon(True)
            t2.start()
        elif "exit" in command:
            # torrent exit
            node.exit()
            exit(0)

        command = input()


def handle_args():
    if len(sys.argv) > 1:
        # example: "python3 node.py -n name -p port1 port2"
        name_pos = sys.argv.index("-n")
        name = str(sys.argv[name_pos + 1])
        ports_pos = sys.argv.index("-p")
        port1 = int(sys.argv[ports_pos + 1])
        port2 = int(sys.argv[ports_pos + 2])
        return name, port1, port2


if __name__ == '__main__':
    name, p1, p2 = handle_args()
    main(name, p1, p2)
