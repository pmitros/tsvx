import sys

import tsvx

t = tsvx.reader(open("../data/example.tsvx"))
for line in t:
    print "repr of the line:", line
    print "We can index by variable. This is nice, since permuting columns"
    print "no longer breaks code:",
    print line.foodname, line.weight, line.price, line.expiration
    print "Basic introspection: ", line.keys()
    print "Printing by get instead of getattr, but by name: "
    for key in line.keys():
        print line[key],
    print
    print "And by position:"
    for i in range(len(line)):
        print line[i],
    print
    print "We can also cast to dict", dict(line)
    print "Or to list", list(line)

names = ["sam", "joe", "alex"]
ages = [34, 45, 12]
locations = ["left", "middle", "right"]
votes = [True, False, False]

print
print "This is an example of how to write out a file. The"
print "writer has a convenient w.close() operation too."

w = tsvx.writer(sys.stdout)
w.headers(["Name", "Age", "Location", "Vote"])
w.variables(["name", "age", "location", "vote"])
w.python_types([str, int, str, bool])
w.title("Sample file")

w.write_headers()

for name, age, location, vote in zip(names, ages, locations, votes):
    w.write(name, age, location, vote)

print "The library can guess types for existing TSV to TSVx conversion:", 
print tsvx.parser.guess_type("0")
