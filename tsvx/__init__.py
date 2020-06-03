'''
This is a library for working with TSVx files. It is designed to
help us design the TSVx file format. TSVx is intended to standardize
TSV files with regards to headers, metadata, and escaping, while
maintaining their human-readability and ease of processing.
'''

from .tsvx import reader, writer
