'''
Simple generic utility functions not specific to TSVx
'''

import dateutil.parser
import itertools

def valid_variable(string):
    '''
    Check whether string is all numbers, letters, and underscores, and does
    not begin with a number.
    '''
    if string[0].isdigit():
        return False
    if len(string) == 0:
        return False
    if not string.replace('_', '').isalnum():
        return False
    return True


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


existing_variables = set()
def variable_from_string(header):
    '''
    Given a header item, create a unique variable name. Such a name
    should be unique, consist of letters, numbers, and underscores.
    >>> variable_from_string("123 This is a string")
    '_123_This_is_a_string'
    >>> variable_from_string("123 This is a string")
    '_123_This_is_a_string0'
    >>> variable_from_string("valid_identifier")
    'valid_identifier'
    '''
    # Make sure variable is numbers, letters, and underscores, and
    # does not begin with a number
    candidate = header.strip().replace(' ', '_')
    candidate = "".join(x for x in candidate if x.isalnum() or x == '_')
    if candidate[0].isdigit():
        candidate = '_' + candidate
    # Make sure variable is unique
    if candidate in existing_variables:
        i = 0
        while candidate+str(i) in existing_variables:
            i = i+1
        candidate = candidate+str(i)
    existing_variables.add(candidate)
    return candidate


def datetime_to_ISO8601(d):
    '''
    Transform a freeform datetime to ISO8601 format
    >>> date_to_ISO8601("10/28/2014")
    '2014-10-28T00:00:00'
    '''
    return dateutil.parser.parse(d).isoformat()


def date_to_ISO8601(d):
    '''
    Transform a freeform date to ISO8601 format
    >>> date_to_ISO8601("10/28/2014")
    '2014-10-28'
    '''
    return datetime_to_ISO8601(d).split('T')[0]


def to_bool(b):
    '''
    Transform flexible types to a boolean
    '''
    if b in [True, False]:
        return b
    if isinstance(b, basestring):
        if b.lower() in ["yes", "y", "true", "t"]:
            return True
        elif b.lower() in ["no", "n", "false", "f"]:
            return False
    raise AttributeError("Not a boolean-looking type: "+str(b))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
