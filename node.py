import os
import sys
from itertools import groupby
from operator import itemgetter
from threading import Thread
from crypto.cryptography_unit import crypto_unit
from datagram import UDPDatagram
from messages import modes
from messages.file_communication import FileCommunication
from messages.message import Message
from messages.node_to_tracker import NodeToTracker
from messages.size_information import SizeInformation
from utils import *

SELECT_COUNT = 2


class Node:
    def __init__(self, name: str, rec_port: int, send_port: int):
        # send tracker the node_files each node has (in init).
        self.rec_s = create_socket(rec_port)
        self.send_s = create_socket(send_port)
        self.name = name
        self.files = self.set_filenames()
        # {filename: list(msg of that file which contain the parts of data)}
        self.received_files = {}
        self.has_started_uploading = False
    
    def set_filenames(self) -> list:
        path = f"node_files/{self.name}"
        ret = []
        if os.path.isdir(path):
            _, _, ret = next(os.walk(path))
        return ret
    
    def send_datagram(self, s, msg, addr):
        dg = UDPDatagram(port_number(s), addr[1], msg.encode())
        enc = crypto_unit.encrypt(dg)
        s.sendto(enc, addr)
        return dg
    
    def self_send_datagram(self, msg: Message, addr: Tuple[str, int]):
        return self.send_datagram(self.send_s, msg, addr)
    
    def get_full_path(self, filename: str):
        return f"node_files/{self.name}/{filename}"
    
    def start_download(self, filename: str):
        if os.path.isfile(self.get_full_path(filename)):
            print(f"{filename} already exists in Node {self.name}'s "
                  f"directory. Please rename the existing file and try again.")
            return
        
        print(f"Node {self.name} is starting to download {filename}.")
        res = self.search(filename)
        owners = res["owners"]
        self.split_owners(filename, owners)
        # split the parts and assign each part to a node
    
    def search(self, filename: str) -> dict:
        message = NodeToTracker(self.name, modes.NEED, filename)
        temp_s = create_socket(give_port())
        self.send_datagram(temp_s, message, TRACKER_ADDR)
        
        while True:
            data, addr = temp_s.recvfrom(BUFFER_SIZE)
            dg: UDPDatagram = crypto_unit.decrypt(data)
            if dg.src_port != TRACKER_ADDR[1]:
                raise ValueError(f"Someone other than the tracker with "
                                 f"port:{dg.src_port} sent {self.name} "
                                 f"the search datagram.")
            return Message.decode(dg.data)
    
    def split_owners(self, filename: str, owners: list):
        owners = [o for o in owners if o[0] != self.name]
        owners = sorted(owners, key=lambda x: x[2], reverse=True)
        owners = owners[:SELECT_COUNT]
        if not owners:
            print(f"Could not find any owner of {filename} for "
                  f"Node {self.name}.")
            return
        print(f"The top {SELECT_COUNT} owner(s) of {filename} are:\n{owners}")
        
        # TODO check all the file sizes are equal
        
        # retrieve file's size from one of the owners
        print(f"Asking the {filename}'s size from {owners[0][0]}.")
        size = self.ask_file_size(filename, owners[0])
        print(f"The size of {filename} is {size}.")
        # splitting equally on all the owners
        ranges = self.split_size(size, len(owners))
        print(f"Each owner now sends {round(size / len(owners), 0)} bytes of "
              f"the {filename}.")
        
        # tell each one which parts you want in a thread.
        threads = []
        self.received_files[filename] = []
        print(f"Node {self.name} is making threads to receive the parts "
              f"from the owners.")
        for i, o in enumerate(owners):
            t = Thread(target=self.receive_file,
                       args=(filename, ranges[i], o))
            t.setDaemon(True)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        print(f"Node {self.name} has received all the parts of {filename}. "
              f"Now going to sort them based on ranges.")
        # we have received all parts of the file.
        # now sort them based on the ranges
        
        ordered_parts = self.sort_received_files(filename)
        print(f"All the parts of {filename} are now sorted.")
        whole_file = []
        for section in ordered_parts:
            for part in section:
                whole_file.append(part["data"])
        assemble_file(whole_file, self.get_full_path(filename))
        print(f"{filename} is successfully saved for Node {self.name}.")
        
        # TODO check if there is a missing range
        
        # TODO add algorithm
    
    @staticmethod
    def split_size(size: int, num_parts: int):
        step = size / num_parts
        return [(round(step * i), round(step * (i + 1))) for i in
                range(num_parts)]
    
    def sort_received_files(self, filename: str):
        sort_by_range = sorted(self.received_files[filename],
                               key=itemgetter('range'))
        group_by_range = groupby(sort_by_range, key=lambda x: x["range"])
        res = []
        for k, v in group_by_range:
            vl_srt_by_idx = sorted(list(v), key=itemgetter('idx'))
            res.append(vl_srt_by_idx)
        return res
    
    def receive_file(self, filename: str, rng: Tuple[int, int], owner: tuple):
        # telling the nodes we NEED a file, therefore idx=-1 and data=None.
        msg = FileCommunication(self.name, owner[0], filename, rng)
        temp_s = create_socket(give_port())
        self.send_datagram(temp_s, msg, owner[1])
        print(f"Node {self.name} has sent the start-of-transfer message to "
              f"{owner[0]}.")
        
        while True:
            data, addr = temp_s.recvfrom(BUFFER_SIZE)
            dg: UDPDatagram = crypto_unit.decrypt(data)
            
            msg = Message.decode(dg.data)
            # msg now contains the actual bytes of the data for that file.
            
            # TODO some validation
            if msg["filename"] != filename:
                print(f"Wanted {filename} but received {msg['range']} range "
                      f"of {msg['filename']}")
                return
            
            if msg["idx"] == -1:
                print(f"Node {self.name} received the end-of-transfer message "
                      f"from {owner[0]}.")
                free_socket(temp_s)
                return
            
            self.received_files[filename].append(msg)
    
    def ask_file_size(self, filename: str, owner: tuple) -> int:
        # size == -1 means asking the size
        message = SizeInformation(self.name, owner[0], filename)
        temp_s = create_socket(give_port())
        self.send_datagram(temp_s, message, owner[1])
        
        while True:
            data, addr = temp_s.recvfrom(BUFFER_SIZE)
            dg: UDPDatagram = crypto_unit.decrypt(data)
            
            # TODO some validation
            
            free_socket(temp_s)
            return Message.decode(dg.data)["size"]
    
    def set_upload(self, filename: str):
        if filename not in self.files:
            print(f"Node {self.name} does not have {filename}.")
            return
        
        message = NodeToTracker(self.name, modes.HAVE, filename)
        self.send_datagram(self.rec_s, message, TRACKER_ADDR)
        
        if self.has_started_uploading:
            print(f"Node {self.name} is already in upload mode. Not making "
                  f"a new thread but the file is added to the upload list.")
            return
        else:
            print(f"Node {self.name} is now listening for download requests.")
            self.has_started_uploading = True
        
        # start listening for requests in a thread.
        t = Thread(target=self.start_listening, args=())
        t.setDaemon(True)
        t.start()
    
    def start_listening(self):
        while True:
            data, addr = self.rec_s.recvfrom(BUFFER_SIZE)
            dg: UDPDatagram = crypto_unit.decrypt(data)
            msg = Message.decode(dg.data)
            if "size" in msg.keys() and msg["size"] == -1:
                # meaning someone needs the file size
                self.tell_file_size(dg, msg)
            elif "range" in msg.keys() and msg["data"] is None:
                print(f"Node {self.name} received the start-of-transfer "
                      f"message from Node {msg['src_name']}.")
                self.send_file(msg["filename"], msg["range"], msg["src_name"],
                               dg.src_port)
    
    def tell_file_size(self, dg: UDPDatagram, msg: dict):
        filename = msg["filename"]
        size = os.stat(self.get_full_path(filename)).st_size
        resp_message = SizeInformation(self.name, msg["src_name"],
                                       filename, size)
        # TODO generalize localhost
        temp_s = create_socket(give_port())
        self.send_datagram(temp_s, resp_message, ('localhost', dg.src_port))
        print(f"Sending the {filename}'s size to {msg['src_name']}.")
        free_socket(temp_s)
    
    def send_file(self, filename: str, rng: Tuple[int, int], dest_name: str,
                  dest_port: int):
        path = self.get_full_path(filename)
        parts = split_file(path, rng)
        temp_s = create_socket(give_port())
        for i, part in enumerate(parts):
            msg = FileCommunication(self.name, dest_name, filename, rng, i,
                                    part)
            # TODO generalize localhost
            # TODO print each udp datagram's range
            self.send_datagram(temp_s, msg, ("localhost", dest_port))
        
        # sending the end-of-transfer datagram
        msg = FileCommunication(self.name, dest_name, filename, rng)
        self.send_datagram(temp_s, msg, ("localhost", dest_port))
        print(f"Node {self.name} has sent the end-of-transfer message "
              f"to {dest_name}.")
        
        free_socket(temp_s)
    
    def exit(self):
        print(f"Node {self.name} exited the program.")
        msg = NodeToTracker(self.name, modes.EXIT, '')
        self.send_datagram(self.rec_s, msg, TRACKER_ADDR)
        free_socket(self.rec_s)
        free_socket(self.send_s)


def main(name: str, rec_port: int, send_port: int):
    node = Node(name, rec_port, send_port)
    
    command = input()
    while True:
        if "upload" in command:
            # torrent -setMode upload filename
            filename = command.split(' ')[3]
            node.set_upload(filename)
        elif "download" in command:
            # torrent -setMode download filename
            filename = command.split(' ')[3]
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
