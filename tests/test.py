'''
Quick and dirty demo of how the library works, and a little test
to make sure it works correctly as developing.

`python setup.py develop`
`watch python test.py`
'''

import hashlib
import random

import tsvx

w = tsvx.writer(open("test.tsvx", "w"))
w.title = "Test file"
w.description = "Just testing"
w.headers = ["ID", "UID", "Price"]

ids = range(10)
random.seed(10)
uids = [hashlib.md5(str(i).encode('utf-8')).hexdigest() for i in ids]
prices = [random.uniform(0, 100) for i in ids]

w.types = [int, str, float]

w.write_headers()

for item_id, uid, price in zip(ids, uids, prices):
    w.write(item_id, uid, price)

w.close()

r = tsvx.reader(open("test.tsvx"))

for line in r:
    print(line)

print(w.types)
print(r.types)
print("Column names", r.column_names)
print("Metadata", r.metadata)
print("Header", r.extra_headers)
print("Vars", r.variables)
