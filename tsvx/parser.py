'''
Defines the parsing logic for each of the column types, and how
to map those to type strings in the header.

For the most part, we'd like these to be *fast*. Working with large
TSVx files takes time. We standardize formats in part to avoid
heuristics.

We do have several slower heuristic parsers to assist with TSV->TSVx
conversion.

'''

import datetime
import dateutil.parser
import exceptions
import json
import re


def _encodebool(boolean):
    '''
    Encode a bool with appropriate case
    >>> _encodebool(True)
    'true'
    >>> _encodebool(False)
    'false'
    '''
    if not isinstance(boolean, bool):
        raise TypeError("Trying to encode " +
                        repr(boolean) +
                        " of type " +
                        type(boolean) +
                        "as a boolean")

    if boolean:
        return "true"
    return "false"


def _encodestr(string):
    r'''
    Escape a string with standard JSON encoding, omitting
    the quotes
    >>> _encodestr("Hello\t")
    'Hello\\t'
    >>> _encodestr("Hello")
    'Hello'
    '''
    if string is None:
        # TODO: Find a better encoding?
        return '"null"'
    if not isinstance(string, basestring):
        raise TypeError("Trying to encode " +
                        repr(string) +
                        " of type " +
                        type(string).__name__ +
                        " as a string")
    try:
        dump = json.dumps(string)[1:-1]
    except UnicodeDecodeError:
        # TODO: Find a better encoding?
        dump = repr(str)
    return dump


def _parsestr(string):
    r'''
    Escape a string with standard JSON encoding, omitting
    the quotes
    >>> _parsestr("Hello")
    u'Hello'
    >>> _parsestr("Hello\\t")
    u'Hello\t'
    '''
    return json.loads('"'+string+'"')


def _parsebool(boolean):
    '''
    Read a boolean
    >>> _parsebool("true")
    True
    >>> _parsebool("false")
    False
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
    >>> _parsedate("2012-11-21")
    datetime.date(2012, 11, 21)
    '''
    return datetime.datetime.strptime(datestring, "%Y-%m-%d").date()


def _encodedate(dateobject):
    '''
    Encode an ISO 8601 format date (without time)
    >>> _encodedate(datetime.date(2012, 11, 21))
    '2012-11-21'
    '''
    if dateobject is None:
        # TODO: Find a better encoding?
        return '"null"'
    return str(dateobject)


def _parsedatetime(datestring):
    '''
    Parse an ISO 8601 format date-time (without time zone)
    >>> _parsedatetime('2012-11-21T11:58:58')
    datetime.datetime(2012, 11, 21, 11, 58, 58)
    '''
    return datetime.datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%S")


def _encodedatetime(dateobject):
    '''
    Encode an ISO 8601 format date-time (without time zone)
    >>> _encodedatetime(datetime.datetime(2012, 11, 21, 11, 58, 58))
    '2012-11-21T11:58:58'
    '''
    if dateobject is None:
        # TODO: Find a better encoding?
        return '"null"'
    return dateobject.isoformat()


def _parseunknowndate(datestring):
    '''
    Parse a date, guessing the format. This is *slow*, but
    sometimes helpful.
    >>> _parseunknowndate("Oct 18, 2013 4pm")
    datetime.datetime(2013, 10, 18, 16, 0)
    '''
    return dateutil.parser.parse(datestring)


def _is_random_date_string(datestring):
    '''
    Check whether something is a date string
    which dateutil can handle
    >>> _is_random_date_string("Oct 18, 2013 4pm")
    True
    >>> _is_random_date_string("I like salad")
    False
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
    ["int", "Number", int, str,
     ["^-?[0-9]+$"]],
    ["NoneType", "null", lambda x: None, lambda x: "null", ["None", "null"]],
    ["float", "Number", float, str,
     ["^-?[0-9]+\.[0-9]*$", "^-?[0-9]+\.[0-9]*e-?[0-9]+$"]],
    ["bool", "Boolean", _parsebool, _encodebool,
     ["^true$", "^false$"]],
    ["ISO8601-datetime", "String", _parsedatetime, _encodedatetime,
     ["^[0-9][0-9][0-9][0-9]-[0-9][0-9]?-[0-9][0-9]T"
      "[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\.?[0-9]*$"]],
    ["ISO8601-date", "String", _parsedate, _encodedate,
     ["^[0-9][0-9][0-9][0-9]-[0-9][0-9]?-[0-9][0-9]$"]],
    ["unformatted-datetime", "String", _parseunknowndate, _encodedatetime,
     [_is_random_date_string]],
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
