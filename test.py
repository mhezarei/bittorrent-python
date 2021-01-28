from itertools import groupby
from operator import itemgetter

from cryptography.cryptography_unit import crypto_unit
from datagram import UDPDatagram

u = UDPDatagram(12, 1231, b"asdfasdfasdf")
print(crypto_unit.encrypt(u).__sizeof__())



lst = [
    {'src_name': 'node_B', 'dest_name': 'node_A', 'filename': 'file1', 'range': (445952, 445953), 'idx': 0},
    {'src_name': 'node_C', 'dest_name': 'node_A', 'filename': 'file1', 'range': (222976, 445952), 'idx': 0},
    {'src_name': 'node_B', 'dest_name': 'node_A', 'filename': 'file1', 'range': (0, 222976), 'idx': 2},
    {'src_name': 'node_C', 'dest_name': 'node_A', 'filename': 'file1', 'range': (222976, 445952), 'idx': 1},
    {'src_name': 'node_B', 'dest_name': 'node_A', 'filename': 'file1', 'range': (445952, 445953), 'idx': 54},
    {'src_name': 'node_B', 'dest_name': 'node_A', 'filename': 'file1', 'range': (0, 222976), 'idx': 1},
    {'src_name': 'node_C', 'dest_name': 'node_A', 'filename': 'file1', 'range': (222976, 445952), 'idx': 2},
    {'src_name': 'node_B', 'dest_name': 'node_A', 'filename': 'file1', 'range': (0, 222976), 'idx': 3},
    {'src_name': 'node_B', 'dest_name': 'node_A', 'filename': 'file1', 'range': (0, 222976), 'idx': 0},
    {'src_name': 'node_B', 'dest_name': 'node_A', 'filename': 'file1', 'range': (445952, 445953), 'idx': 2},
    {'src_name': 'node_C', 'dest_name': 'node_A', 'filename': 'file1', 'range': (222976, 445952), 'idx': 3},
]

res = sorted(lst, key=itemgetter('range'))
for d in res:
    print(d)

haha = groupby(res, key=lambda x: x["range"])
for k, v in haha:
    vl = list(v)
    vl_res = sorted(vl, key=itemgetter('idx'))
    for i in vl_res:
        print(k, i)


lst = [
    ('node_C', ('127.0.0.1', 33333), 1),
    ('node_C', ('127.0.0.1', 33332), 2),
    ('node_C', ('127.0.0.1', 33334), 3),
    ('node_B', ('127.0.0.1', 22220), 0),
]

print(sorted(lst, key=lambda x: x[2]))
