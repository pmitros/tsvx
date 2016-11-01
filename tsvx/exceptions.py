
'''
For now, we have one exception -- if there is an issue in the file
format.
'''


class TSVxFileFormatException(Exception):
    '''
    Generic exception for ill-formed TSVx file
    '''
    pass

class TSVxSuscpiciousOperation(Exception):
    '''
    Exception for things that may raise security flags. For example,
    having something like a variable named `__init__` in a TSVx file
    mapping to a Python identifier may not be strictly incorrect as
    per the format specification, but we don't want programs using
    such things blindly. Something like `line.__init__` or even
    using `getattr` and `hasattr` would be a bad idea. 
    line.get('__init__') would be okay.
    '''
    pass
    
