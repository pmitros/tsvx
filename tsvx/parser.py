'''
Defines the parsing logic for each of the column types, and how
to map those to type strings in the header.
'''

import datetime
import dateutil.parser
import exceptions
import json
import re


def _encodebool(boolean):
    '''
    Encode a bool with appropriate case
    '''
    if boolean:
        return "true"
    return "false"


def _encodestr(string):
    '''
    Escape a string with standard JSON encoding, omitting
    the quotes
    '''
    return json.dumps(string)[1:-1]


def _parsestr(string):
    '''
    Escape a string with standard JSON encoding, omitting
    the quotes
    '''
    return json.loads('"'+string+'"')


def _parsebool(boolean):
    '''
    Read a boolean
    '''
    if boolean.lower() == "false":
        return False
    if boolean.lower() == "true":
        return True
    raise exceptions.TSVxFileFormatException(
        "Boolean type must be true/false: " + boolean
    )


def _parsedate(datestring):
    '''
    Parse an ISO 8601 format date (without time)
    '''
    return datetime.datetime.strptime(datestring, "%Y-%m-%d").date()


def _encodedate(dateobject):
    '''
    Encode an ISO 8601 format date (without time)
    '''
    return str(dateobject)


def _parsedatetime(datestring):
    '''
    Parse an ISO 8601 format date-time (without time zone)
    '''
    return datetime.datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%S")


def _encodedatetime(dateobject):
    '''
    Encode an ISO 8601 format date-time (without time zone)
    '''
    return str(dateobject)

def _parseunknowndate(datestring):
    '''
    Parse a date, guessing the format. This is *slow*, but
    sometimes helpful.
    '''
    return dateutil.parser.parse(datestring)

def _is_random_date_string(datestring):
    '''
    Check whether something is a date string
    which dateutil can handle
    '''
    try:
        dateutil.parser.parse(datestring)
        return True
    except ValueError:
        return False

# Elements:
#
# * Python type name
# * JSON type name
# * Function to convert from string to data (parser)
# * Function to convert from data to string (encoder)
# * Regular expressions. These are /not/ all-inclusive or helpful for
#   validation. These are helpful for automagical
#   detection. Therefore, "769" will match as int but not as float,
#   even though it is a valid float. These are also not guaranteed
#   to be complete -- some types might not have these, and we will
#   fall back to String types for those.

TYPE_MAP = [
    ["int", "Number", int, str, ["^-?[0-9]+$"]],
    ["float", "Number", float, str, ["^-?[0-9]+\.[0-9]*$", "^-?[0-9]+\.[0-9]*e-?[0-9]+$"]],
    ["bool", "Boolean", _parsebool, _encodebool, ["^true$", "^false$"]],
    ["ISO8601-datetime", "String", _parsedatetime, _encodedatetime, ["^[0-9][0-9][0-9][0-9]-[0-9][0-9]?-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\.?[0-9]*$"]],
    ["ISO8601-date", "String", _parsedate, _encodedate, ["^[0-9][0-9][0-9][0-9]-[0-9][0-9]?-[0-9][0-9]$"]],
    ["unformatted-datetime", "String", _parseunknowndate, _encodedatetime, [_is_random_date_string]],
    ["str", "String", _parsestr, _encodestr, [".*"]]
]


def guess_type(string):
    '''
    Based on a string, guess the type associated with that string. For
    example:

    >>> guess_type("0")
    ('int', 'Number')
    >>> guess_type("2014-05-06")
    ('ISO8601-date', 'String')
    '''
    for python_type_string, json_type, parser, encoder, regexps in TYPE_MAP:
        for regexp in regexps:
            if isinstance(regexp, basestring):
                if re.compile(regexp).match(string):
                    return (python_type_string, json_type)
            elif regexp(string):
                return (python_type_string, json_type)
    return None


def parse(string, python_type):
    '''
    Find appropriate parser for the given type, and parse string to
    Python data type. For example:

    >>> parse("0", "int")
    0
    >>> parse("2014-05-06", "ISO8601-date")
    datetime.date(2014, 5, 6)
    '''
    for python_type_string, json_type, parser, encoder, regexp in TYPE_MAP:
        if python_type_string == python_type:
            return parser(string)
    raise exceptions.TSVxFileFormatException(
        "Unknown type TSVx parsing " + python_type
    )


def encode(string, python_type):
    '''
    Find appropriate encoder for the given type, and encode Python
    data type to string. For example:

    >>> encode(0, "int")
    '0'
    >>> encode(datetime.date(2014, 5, 6), "ISO8601-date")
    '2014-05-06'
    '''
    for python_type_string, json_type, parser, encoder, regexp in TYPE_MAP:
        if python_type_string == python_type:
            return encoder(string)
    raise exceptions.TSVxFileFormatException(
        "Unknown type TSVx encoding " + python_type
    )

if __name__ == "__main__":
    import doctest
    doctest.testmod()
