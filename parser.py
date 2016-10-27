import json
import exceptions

def encodebool(boolean):
    '''
    Encode a bool with appropriate case
    '''
    if boolean:
        return "true"
    return "false"

def encodestr(string):
    '''
    Escape a string with standard JSON encoding, omitting
    the quotes
    '''
    json.dumps(string)[1:-1]

def parsestr(string):
    '''
    Escape a string with standard JSON encoding, omitting
    the quotes
    '''
    json.dumps("'"+string+"'")

def parsebool(boolean):
    '''
    Read a boolean
    '''
    if boolean.lower() == "false":
        return False
    if boolean.lower() == "true":
        return True
    raise exceptions.TSVXFileFormatException(
        "Boolean type must be true/false: " + boolean
    )


# Python type/JSON type/parse
type_map = [
    ["int", "Number", int, str],
    ["float", "Number", int, str], 
    ["bool", "Boolean", parsebool, encodebool],
    ["str", "String", parsestr, encodestr]
]

def parse(string, python_type):
    
    return string

def encode(string, python_type):
    return string
