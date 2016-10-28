'''
For now, we have one exception -- if there is an issue in the file
format.
'''


class TSVxFileFormatException(Exception):
    '''
    Generic exception for ill-formed TSVx file
    '''
    pass
