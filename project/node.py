import os
import sys
from itertools import groupby
from operator import itemgetter
from threading import Thread
from project.datagram import UDPDatagram
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
        self.files = self.set_filenames()
        # {filename: list(msg of that file which contain the parts of data)}
        self.received_files = {}
    
    def set_filenames(self) -> list:
        path = f"node_files/{self.name}"
        ret = []
        if os.path.isdir(path):
            _, _, ret = next(os.walk(path))
        return ret
    
    def send_datagram(self, s, msg, addr):
        dg = UDPDatagram(port_number(s), addr[1], msg.encode())
        self.send_s.sendto(dg.encode(), addr)
        return dg
    
    def self_send_datagram(self, msg: Message, addr: Tuple[str, int]):
        print(f"msg size {msg.encode().__sizeof__()}")
        return self.send_datagram(self.send_s, msg, addr)
    
    def get_full_path(self, filename: str):
        return f"node_files/{self.name}/{filename}"
    
    def start_download(self, filename: str):
        res = self.search(filename)
        owners = res["owners"]
        self.split_owners(filename, owners)
        # split the parts and assign each part to a node
    
    def search(self, filename: str) -> dict:
        message = NodeToTracker(self.name, modes.NEED, filename)
        self.send_datagram(self.send_s, message, TRACKER_ADDR)
        
        while True:
            data, addr = self.send_s.recvfrom(BUFFER_SIZE)
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
        # TODO sort owners based of freq and select the best 3 owners
        owners = [o for o in owners if o[0] != self.name]
        if not owners:
            print(f"Could not find an owner of {filename} for {self.name}.")
            return
        
        # TODO check all the file sizes are equal
        
        # retrieve file's size from one of the owners
        size = self.ask_file_size(filename, owners[0])
        # splitting equally on all the owners
        ranges = self.split_size(size, len(owners))
        # tell each one which parts you want in a thread.
        threads = []
        self.received_files[filename] = []
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
        
        ordered_parts = self.sort_received_files(filename)
        
        whole_file = []
        for section in ordered_parts:
            for part in section:
                whole_file.append(part["data"])
        assemble_file(whole_file, self.get_full_path(filename))
        
        # TODO check if there is a missing range
        
        # TODO add algorithm
    
    def sort_received_files(self, filename: str):
        sort_by_range = sorted(self.received_files[filename],
                               key=itemgetter('range'))
        group_by_range = groupby(sort_by_range, key=lambda x: x["range"])
        res = []
        for k, v in group_by_range:
            vl_srt_by_idx = sorted(list(v), key=itemgetter('idx'))
            res.append(vl_srt_by_idx)
            for i in vl_srt_by_idx:
                print(k, {t: i[t] for t in i.keys() if t != "data"})
        return res
    
    def transfer_file(self, filename: str, rng: Tuple[int, int], owner: tuple):
        # telling the nodes we NEED a file, therefore idx=-1 and data=None.
        msg = FileCommunication(self.name, owner[0], filename, rng)
        temp_s = create_socket(give_port())
        self.send_datagram(temp_s, msg, owner[1])
        
        while True:
            data, addr = temp_s.recvfrom(BUFFER_SIZE)
            dg: UDPDatagram = UDPDatagram.decode(data)
            
            msg = Message.decode(dg.data)
            # msg now contains the actual bytes of the data for that file.
            
            # TODO some validation
            if msg["filename"] != filename:
                print(f"Wanted {filename} but received {msg['range']} range "
                      f"of {msg['filename']}")
                return
            
            if msg["idx"] == -1:
                return
            
            self.received_files[filename].append(msg)
    
    def ask_file_size(self, filename: str, owner: tuple) -> int:
        # size == -1 means asking the size
        message = SizeInformation(self.name, owner[0], filename, -1)
        temp_s = create_socket(give_port())
        self.send_datagram(temp_s, message, owner[1])
        
        while True:
            data, addr = temp_s.recvfrom(BUFFER_SIZE)
            dg: UDPDatagram = UDPDatagram.decode(data)
            
            # TODO some validation
            
            return Message.decode(dg.data)["size"]
    
    def tell_file_size(self, dg: UDPDatagram, msg: dict):
        filename = msg["filename"]
        size = os.stat(self.get_full_path(filename)).st_size
        resp_message = SizeInformation(self.name, msg["src_name"],
                                       filename, size)
        # TODO generalize localhost
        temp_s = create_socket(give_port())
        self.send_datagram(temp_s, resp_message, ('localhost', dg.src_port))
    
    def set_upload(self, filename: str):
        if filename not in self.files:
            print(f"Node {self.name} does not have {filename}.")
            return
        
        message = NodeToTracker(self.name, modes.HAVE, filename)
        self.self_send_datagram(message, TRACKER_ADDR)
        
        # start listening for requests in a thread.
        t = Thread(target=self.start_listening, args=())
        t.setDaemon(True)
        t.start()
    
    def start_listening(self):
        while True:
            data, addr = self.send_s.recvfrom(BUFFER_SIZE)
            dg: UDPDatagram = UDPDatagram.decode(data)
            msg = Message.decode(dg.data)
            if "size" in msg.keys() and msg["size"] == -1:
                # meaning someone needs the file size
                self.tell_file_size(dg, msg)
            elif "range" in msg.keys() and msg["data"] is None:
                self.send_file(msg["filename"], msg["range"], msg["src_name"],
                               dg.src_port)
    
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
