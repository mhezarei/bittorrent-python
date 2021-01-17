import os
import random
import sys
import threading

from project.utils import *


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

    def search(self, filename: str):
        # i want a file
        pass

    def download(self):
        # call search
        # split the parts and assign each part to a node
        # start requesting
        pass

    def set_upload(self, filename: str):
        # tell tracker which files you want to
        pass

    def exit(self):
        # tell tracker i want to go :(
        pass

    def start(self):
        # we need a file
        # self.send_s.sendto(b"asdasdasd", ("localhost", tracker_port))
        while True:
            data, addr = self.send_s.recvfrom(1024)
            print(data, addr, self.send_s.getsockname()[1])


def main(name: str, port1: int, port2: int):
    node = Node(name, port1, port2)
    # make start a thread
    t = threading.Thread(target=node.start())
    t.start()

    command = input()
    while True:
        if "upload" in command:
            filename = command.split(' ')[2]
            node.set_upload(filename)
        elif "download" in command:
            t2 = threading.Thread(target=node.download())
            t2.start()
        elif "exit" in command:
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
