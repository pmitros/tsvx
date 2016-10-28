'''
Defines the parsing logic for each of the column types, and how
to map those to type strings in the header.
'''

import datetime
import exceptions
import json


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

# Python type/JSON type/parse
TYPE_MAP = [
    ["int", "Number", int, str],
    ["float", "Number", float, str],
    ["bool", "Boolean", _parsebool, _encodebool],
    ["str", "String", _parsestr, _encodestr],
    ["ISO8601-datetime", "String", _parsedatetime, _encodedatetime],
    ["ISO8601-date", "String", _parsedate, _encodedate]
]


def parse(string, python_type):
    '''
    Find appropriate parser for the given type, and parse string to
    Python data type
    '''
    for python_type_string, json_type, parser, encoder in TYPE_MAP:
        if python_type_string == python_type:
            return parser(string)
    raise exceptions.TSVxFileFormatException(
        "Unknown type TSVx parsing " + python_type
    )


def encode(string, python_type):
    '''
    Find appropriate encoder for the given type, and encode Python
    data type to string
    '''
    for python_type_string, json_type, parser, encoder in TYPE_MAP:
        if python_type_string == python_type:
            return encoder(string)
    raise exceptions.TSVxFileFormatException(
        "Unknown type TSVx encoding " + python_type
    )
