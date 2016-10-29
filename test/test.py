import sys

import tsvx

t = tsvx.reader(open("../data/example.tsvx"))
print t
for line in t:
    print line
    print line.foodname, line.weight, line.price, line.expiration
    print line.keys()
    for key in line.keys():
        print line[key],
    for i in range(len(line)):
        print line[i],
    print dict(line)
    print list(line)

names = ["sam", "joe", "alex"]
ages = [34, 45, 12]
locations = ["left", "middle", "right"]
votes = [True, False, False]

w = tsvx.writer(sys.stdout)
w.headers(["Name", "Age", "Location", "Vote"])
w.variables(["name", "age", "location", "vote"])
w.types([str, int, str, bool])
w.title("Sample file")

print

w.write_headers()

for name, age, location, vote in zip(names, ages, locations, votes):
    w.write(name, age, location, vote)

print tsvx.parser.guess_type("0")
print tsvx.parser.guess_type("1.4")
print tsvx.parser.guess_type("Hello")
print tsvx.parser.guess_type("2014-05-06")
print tsvx.parser.guess_type("2014-05-06T05:12:12")
