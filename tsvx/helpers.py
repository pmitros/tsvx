'''
Simple generic utility functions not specific to TSVx
'''
import itertools

import dateutil.parser


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


def peek(generator, item_count=-1):
    '''
    Return the first item in the generator. Usage
       (first, generator) = peek(generator)

    Optionally, provide an item_count to return several items.
       (item_list, generator) = peek(generator, 7)

    For example:
    >>> (first, generator) = peek(iter(range(3)))
    >>> first
    0
    >>> list(generator)
    [0, 1, 2]
    >>> (start, generator) = peek(iter(range(5)), 2)
    >>> start
    [0, 1]
    >>> list(generator)
    [0, 1, 2, 3, 4]
    '''
    if item_count == -1:
        first = next(generator)
        generator = itertools.chain([first], generator)
        return (first, generator)
    # Else, if item_count != -1
    items = [next(generator) for x in range(item_count)]
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


EXISTING_VARIABLES = set()


def variable_from_string(header):
    '''
    Given a string, create a unique variable name. Such a name should
    be unique, consist of letters, numbers, and underscores. This is
    mostly intended to automagically create the `variables` line
    from things like TSV headers.

    >>> variable_from_string("123 This is a string")
    '_123_This_is_a_string'
    >>> variable_from_string("123 This is a string")
    '_123_This_is_a_string0'
    >>> variable_from_string("valid_identifier")
    'valid_identifier'

    Should we do this globally? Once per writer? Should we maintain a
    dictionary of mappings?
    '''
    # Make sure variable is numbers, letters, and underscores, and
    # does not begin with a number
    candidate = header.strip().replace(' ', '_')
    candidate = "".join(x for x in candidate if x.isalnum() or x == '_')
    if candidate[0].isdigit():
        candidate = '_' + candidate
    # Make sure variable is unique
    if candidate in EXISTING_VARIABLES:
        i = 0
        while candidate+str(i) in EXISTING_VARIABLES:
            i = i+1
        candidate = candidate+str(i)
    EXISTING_VARIABLES.add(candidate)
    return candidate


def datetime_to_ISO8601(datetime_string):
    '''
    Transform a freeform datetime to ISO8601 format
    >>> datetime_to_ISO8601("10/28/2014 00:00:00")
    '2014-10-28T00:00:00'
    '''
    return dateutil.parser.parse(datetime_string).isoformat()


def date_to_ISO8601(date_string):
    '''
    Transform a freeform date to ISO8601 format
    >>> date_to_ISO8601("10/28/2014")
    '2014-10-28'
    '''
    return datetime_to_ISO8601(date_string).split('T')[0]


def to_bool(boolean_string):
    '''
    Transform flexible types to a boolean
    >>> to_bool(True)
    True
    >>> to_bool(False)
    False
    >>> to_bool("yEs")
    True
    >>> to_bool("NO")
    False
    '''
    if boolean_string in [True, False]:
        return boolean_string
    if isinstance(boolean_string, str):
        if boolean_string.lower() in ["yes", "y", "true", "t"]:
            return True
        if boolean_string.lower() in ["no", "n", "false", "f"]:
            return False
    raise AttributeError("Not a boolean-looking type: "+str(boolean_string))


def to_python_type(type_info):
    '''
    Normalizes either a Python `type` object or a Python `str` object to be
    a Python type. We can use this to map headers back to type lists.

    >>> to_python_type('ISO-8851')  # Non-Python type string. Unchanged.
    'ISO-8851'
    >>> to_python_type('str')       # Python type string ==> Python type
    <class 'str'>
    >>> to_python_type(str)         # Python type. Unchanged.
    <class 'str'>
    '''
    python_types = [ int, float, str, bool ]
    python_type_names = [object.__name__ for object in python_types]

    if isinstance(type_info, type):
        return type_info  # Python type
    if isinstance(type_info, str):
        if type_info in python_type_names:  # String correspond to Python type
            return python_types[python_type_names.index(type_info)]
        return type_info  # String for non-Python type
    raise AttributeError("Expected str or type object: " + repr(type_info))



if __name__ == "__main__":
    import doctest
    doctest.testmod()
