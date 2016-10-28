'''
This file defines the top-level operations -- the reader and
writer. These are exported at the module level in __init__.py
'''

import sys
import yaml

import helpers
import tsv_types


def reader(to_be_parsed):
    '''
    TSVx Reader. This can handle both text data and stream
    data. Perhaps break it up in the future?
    '''

    if isinstance(to_be_parsed, basestring):
        return _parse_generator(to_be_parsed.split("\n"))
    else:
        return _parse_generator(to_be_parsed)


def writer(destination):
    '''
    TSVx Writer
    '''
    return tsv_types.TSVxWriter(destination)


def _parse_generator(generator):
    '''
    From a stream, pick out the headers and metadata, and create
    a new TSVxReader based on those. Return the TSVxReader object.
    '''
    (first, generator) = helpers.peek(generator)
    if ":" in first:
        metadata = yaml.safe_load(helpers.read_to_dash(generator))
    else:
        metadata = {}

    column_names = generator.next()[:-1].split('\t')

    line_headers = dict()

    for line in generator:
        if line.startswith('---'):
            break
        key = line.split(':')[0]
        value = ":".join(line[:-1].split(':')[1:]).split('\t')[1:]
        line_headers[key] = value

    return tsv_types.TSVxReader(metadata, line_headers, generator)

if __name__ == '__main__':
    t = reader(open("example.tsvx"))
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

    w = writer(sys.stdout)
    w.headers(["Name", "Age", "Location", "Vote"])
    w.variables(["name", "age", "location", "vote"])
    w.types([str, int, str, bool])
    w.title("Sample file")

    print

    w.write_headers()

    for name, age, location, vote in zip(names, ages, locations, votes):
        w.write(name, age, location, vote)
