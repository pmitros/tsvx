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
    Given an output stream, create a TSVx Writer
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
        key = line.split('\t')[-1][1:-2]
        value = line[:-1].split('\t')[:-1]
        line_headers[key] = value

    return tsv_types.TSVxReader(column_names, metadata, line_headers, generator)
