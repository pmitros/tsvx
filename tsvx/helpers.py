'''
Simple generic utility functions not specific to TSVx
'''

import itertools


def peek(generator, item_count = -1):
    '''
    Return the first item in the generator. Usage
       (first, generator) = peek(generator)

    Optionally, provide an item_count to return several items.
       (item_list, generator) = peek(generator, 7)
    '''
    if item_count == -1:
        first = generator.next()
        generator = itertools.chain([first], generator)
        return (first, generator)
    else:
        items = [generator.next() for x in range(item_count)]
        generator = itertools.chain(items, generator)
        return (items, generator)


def read_to_dash(generator):
    '''
    Read a file until a set of dashes is encountered
    '''
    lines = []
    for line in generator:
        if line.startswith('---'):
            break
        lines.append(line)
    return "\n".join(lines)
