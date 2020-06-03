'''
This file defines the top-level operations -- the reader and
writer. These are exported at the module level in __init__.py
'''

import sys
import yaml

from . import helpers
from . import tsv_types


def reader(to_be_parsed):
    '''
    TSVx Reader. This can handle both text data and stream
    data. Perhaps break it up in the future?
    '''

    if isinstance(to_be_parsed, str):
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
    # Grab the first line from the generator
    (first, generator) = helpers.peek(generator)

    # If it looks like there's a YAML header, read that. Otherwise, we
    # skip the header. Perhaps we should raise an exception instead?
    if ":" in first:
        metadata = yaml.safe_load(helpers.read_to_dash(generator))
    else:
        metadata = {}

    # Now, we read the column names
    column_names = next(generator)[:-1].split('\t')

    # We read the remaining column headers, which
    # are all the rows until we hit a triple dash
    line_headers = dict()
    for line in generator:
        if line.startswith('---'):
            break
        key = line.split('\t')[-1][1:-2]
        value = line[:-1].split('\t')[:-1]
        line_headers[key] = value

    # Finally, we create a TSVx reader based on the metadata we
    # read
    return tsv_types.TSVxReader(
        column_names,
        metadata,
        line_headers,
        generator
    )
