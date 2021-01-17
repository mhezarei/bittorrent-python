import os
import sys
from threading import Thread
from typing import Tuple
from project.messages.file_communication import FileCommunication
from project.messages.message import Message
from project.messages.size_information import SizeInformation
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
        self.files = []
        self.set_filenames()
        # {filename: list(msg of that file which contain the parts of data)}
        self.received_files = {}

    def set_filenames(self):
        path = f"node_files/{self.name}"
        if os.path.isdir(path):
            _, _, self.files = next(os.walk(path))

    def send_datagram(self, message: bytes, addr: Tuple[str, int]):
        dg = UDPDatagram(port_number(self.send_s), addr[1], message)
        self.send_s.sendto(dg.encode(), addr)

    def start_download(self, filename: str):
        res = self.search(filename)
        owners = res["owners"]
        self.split_owners(filename, owners)
        # split the parts and assign each part to a node

    def search(self, filename: str) -> dict:
        message = NodeToTracker(self.name, modes.NEED, filename).encode()
        self.send_datagram(message, TRACKER_ADDR)

        while True:
            data, addr = self.send_s.recvfrom(1024)
            dg: UDPDatagram = UDPDatagram.decode(data)
            if dg.src_port != TRACKER_ADDR[1]:
                raise ValueError(f"Someone other than the tracker with "
                                 f"port:{dg.src_port} sent {self.name} "
                                 f"the search datagram.")
            return Message.decode(dg.data)

    @staticmethod
    def split_size(size: int, num_parts: int):
        step = size / num_parts
        return [(round(step * i), round(step * (i + 1))) for i in
                range(num_parts)]

    def split_owners(self, filename: str, owners: list):
        print(owners)
        owners = [o for o in owners if o[0] != self.name]
        if not owners:
            print(f"Could not find an owner of {filename} for {self.name}.")
            return

        # retrieve file's size from one of the owners
        size = self.ask_file_size(filename, owners[0])
        # splitting equally on all the owners
        ranges = self.split_size(size, len(owners))
        # tell each one which parts you want in a thread.
        threads = []
        for i, o in enumerate(owners):
            t = Thread(target=self.transfer_file,
                       args=(filename, ranges[i], o))
            t.setDaemon(True)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        # we have received all parts of the file.
        # now sort them based on the ranges
        print(self.received_files)
        # check if there is a missing range


        # TODO add algorithm

    def transfer_file(self, filename: str, rng: Tuple[int, int], owner: tuple):
        # telling the nodes we NEED a file therefore data is None.
        msg = FileCommunication(self.name, owner[0], filename, rng).encode()
        self.send_datagram(msg, owner[1])
        self.received_files[filename] = []

        while True:
            data, addr = self.send_s.recvfrom(1024)
            dg: UDPDatagram = UDPDatagram.decode(data)
            msg = Message.decode(dg.data)
            # msg now contains the actual bytes of the data for that file.

            # some validation
            if msg["filename"] != filename:
                print(f"Wanted {filename} but received {msg['range']} range "
                      f"of {msg['filename']}")
                return

            self.received_files[filename].append(msg)
            return

    def ask_file_size(self, filename: str, owner: tuple) -> int:
        # size == -1 means asking the size
        message = SizeInformation(self.name, owner[0], filename, -1).encode()
        self.send_datagram(message, owner[1])

        while True:
            data, addr = self.send_s.recvfrom(1024)
            dg: UDPDatagram = UDPDatagram.decode(data)
            if dg.src_port != owner[1][1]:
                raise ValueError(f"Someone other than {owner[0]} with "
                                 f"port:{dg.src_port} told {self.name} "
                                 f"the size of {filename}.")
            return Message.decode(dg.data)["size"]

    def tell_file_size(self, dg: UDPDatagram, message: dict):
        filename = message["filename"]
        size = os.stat(f"node_files/{self.name}/{filename}").st_size
        resp_message = SizeInformation(self.name, message["src_name"],
                                       filename, size).encode()
        # TODO generalize localhost
        self.send_datagram(resp_message, ('localhost', dg.src_port))

    def set_upload(self, filename: str):
        if filename not in self.files:
            print(f"Node {self.name} does not have {filename}.")
            return

        message = NodeToTracker(self.name, modes.HAVE, filename).encode()
        self.send_datagram(message, TRACKER_ADDR)

        # start listening for requests in a thread.
        t = Thread(target=self.start_listening, args=())
        t.setDaemon(True)
        t.start()

    def start_listening(self):
        while True:
            data, addr = self.send_s.recvfrom(1024)
            dg: UDPDatagram = UDPDatagram.decode(data)
            msg = Message.decode(dg.data)
            if "size" in msg.keys() and msg["size"] == -1:
                # meaning someone needs the file size
                self.tell_file_size(dg, msg)
            elif "range" in msg.keys() and msg["data"] is None:

                pass

    def exit(self):
        # tell tracker i want to go :(
        pass


def main(name: str, port1: int, port2: int):
    node = Node(name, port1, port2)

    command = input()
    while True:
        if "upload" in command:
            # torrent -upload filename
            filename = command.split(' ')[2]
            node.set_upload(filename)
        elif "download" in command:
            # torrent -download filename
            filename = command.split(' ')[2]
            t2 = Thread(target=node.start_download, args=(filename,))
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
