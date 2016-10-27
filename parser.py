import json
import exceptions



def printbool(boolean):
    '''
    Print a bool with appropriate case
    '''
    if boolean:
        return "true"
    return "false"

def printstr(string):
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
