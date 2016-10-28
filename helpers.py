'''
Simple generic utility functions not specific to TSVx
'''

import itertools


def peek(generator):
    '''
    Return the first item in the generator. Usage
       (first, generator) = peek(generator)
    '''
    first = generator.next()
    generator = itertools.chain([first], generator)
    return (first, generator)


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
