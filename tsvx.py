import itertools
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

def writer(vars = None):
    pass

def _parse_generator(generator):
    (first, generator) = helpers.peek(generator)
    if ":" in first:
        metadata = yaml.load(helpers.read_to_dash(generator))
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

    return tsv_types.TSVx(metadata, line_headers, generator)

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
