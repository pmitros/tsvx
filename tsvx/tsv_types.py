'''
The TSVxReader, TSVxWriter, and TSVxLine objects.
'''

import datetime
import sys
import yaml

from . import helpers
from . import parser
from . import exceptions


class TSVxLine:
    '''
    Represents a single line in the reader object. Lets you work
    with the attributes as a dict-like object, a list-like object,
    or as attributes.

    If the first column has header `id`, all of these are okay:
    `line[0]`, `line.id`, `line['id']`

    We should offer a sanitized / safe version which disables
    `line.id`
    '''
    def __init__(self, line_string, parent):
        '''
        Create a line based on string of the line. Strip the
        newline. Split on tabs. And parse
        '''
        split_line = line_string[:-1].split('\t')
        self.line = list()
        try:
            for item, item_type in zip(split_line, parent.types):
                self.line.append(parser.parse(item, item_type))
        except:
            print("Error parsing", line_string)
            raise

        self.parent = parent

    def __repr__(self):
        '''
        The `repr` of the line is a combination of the `repr`s of
        the objects there-in.
        '''
        return "/".join(repr(item) for item in self.line)

    def __str__(self):
        '''
        The `str` of the line is a combination of the `str`s of
        the objects there-in.
        '''
        return "/".join(str(item) for item in self.line)

# Not needed in Python 3?
#    def __unicode__(self):
#        return "/".join(str(item) for item in self.line)

    def __getattr__(self, attr):
        '''
        We can retrieve items in a line with dot notation.

        Note that this can introduce security issues for untrusted
        content. We should provide safe / unsafe modes in the library.
        TSVX is mostly used internally, where this is okay, but for
        external data sources, we would want to omit this.
        '''
        if not helpers.valid_variable(attr):
            raise exceptions.TSVxFileFormatException(
                "TSVx variables must be alphanumeric. " + attr
            )
        if attr.startswith('_'):
            raise exceptions.TSVxSuscpiciousOperation(
                "Strange attribute " + attr +
                ". Use get instead of attribute referencing")
        index = self.parent.variable_index(attr)
        return self.line[index]

    def __getitem__(self, attr):
        '''
        We can reference by []. Passing an `int` will get the nth item in
        a line, while a `str` will get an item by name.
        '''
        if isinstance(attr, str):
            if not helpers.valid_variable(attr):
                raise exceptions.TSVxFileFormatException(
                    "TSVx variables must be alphanumeric. " + attr
                )
            index = self.parent.variable_index(attr)
            return self.line[index]
        if isinstance(attr, int):
            return self.line[attr]
        raise AttributeError("Can't index with {repr} of type {type}".format(
            repr=repr(attr),
            type=type(attr)
        ))

    def __len__(self):
        '''
        Number of items in the line
        '''
        return len(self.line)

    def __iter__(self):
        '''
        As with a dictionary, we can step through the keys.

        TODO: Should we return keys? Values? Or both?
        '''
        for item in self.parent.header['variables']:
            yield item

    def values(self):
        '''
        List of values in the line.
        '''
        return self.line

    def keys(self):
        '''
        Return the column names.
        '''
        return self.parent.header['variables']


class TSVxReaderWriter():
    '''
    Upper-level class for managing TSV-related metadata.
    '''
    def __init__(self):
        '''
        This is mostly for readability and to avoid pylint errors. This is
        initialized in subclasses.
        '''
        self._metadata = dict()
        self.extra_headers = dict()

    def __repr__(self):
        '''
        For now, we join the YAML representation with the line header. This
        may be too verbose, so we'll probably cut back to just the title
        and maybe line header.
        '''
        return yaml.dump(self._metadata)+"/"+str(self.extra_headers)

    def variable_index(self, variable):
        '''
        For a column name (encoded as a variable), return the column number
        '''
        if 'variables' not in self.extra_headers:
            raise exceptions.TSVxFileFormatException(
                "No defined variable names: " + variable + ". Defined: \n" + \
                "".join(self.extra_headers))
        if variable not in self.extra_headers['variables']:
            raise exceptions.TSVxFileFormatException(
                "Variable undefined: " + variable)
        return self.extra_headers['variables'].index(variable)

    @property
    def title(self):
        '''
        Typically the first line of the YAML, summarizing what the file is.
        '''
        return self._metadata['title']

    @title.setter
    def title(self, title):
        self._metadata['title'] = title

    @property
    def description(self):
        '''
        Typically, a longer multi-line description of the file.
        '''
        return self._metadata['description']

    @description.setter
    def description(self, description):
        self._metadata['description'] = description

    @property
    def metadata(self):
        return self._metadata


class TSVxReader(TSVxReaderWriter):
    def __init__(self,
                 column_names,
                 metadata,
                 line_header,
                 generator):
        '''
        Create a new TSVx Reader. This shouldn't be called directly. We
        would generally use `tsvx.reader(file_pointer)`. 
        '''
        super().__init__()
        self._column_names = column_names
        self._metadata = metadata
        self.extra_headers = line_header
        self.generator = generator

    @property
    def types(self):
        '''
        Python / string-style type names for each column
        '''
        return list(map(helpers.to_python_type, self.extra_headers['types']))

    @property
    def column_names(self):
        '''
        Names of each column, as per original TSVx
        '''
        return self._column_names

    @property
    def variables(self):
        '''
        Python-friendly variable names for each header
        '''
        return self.extra_headers['variables']

    def __iter__(self):
        '''
        This is the basic way of stepping through a TSV: We iterate
        through the rows in the TSVx file. 
        '''
        return (TSVxLine(x, self) for x in self.generator)


class TSVxWriter(TSVxReaderWriter):
    '''
    Class to stream TSVs to a file.
    '''
    def __init__(self, destination):
        '''
        We pass a file-pointer-like-object to create a writer. We then
        configure it by setting `headers`, etc.

        This shouldn't be called directly. We would generally use
        `tsvx.writer(file_pointer)`.
        '''
        super().__init__()
        self.destination = destination
        self._metadata = {
            "created-date": datetime.datetime.utcnow().isoformat(),
            "generator": sys.argv[0]
        }
        self._headers = {}
        self._variables = None
        self.written = False
        self._types = []

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, headers=None):
        self._headers = headers
        return headers

    @property
    def variables(self):
        return self._variables

    @variables.setter
    def variables(self, variables):
        self._variables = variables
        return variables

    def line_header(self, headername, values=None):
        '''
        Get or set line header
        '''
        if values:
            self.extra_headers[headername] = values
        return self.extra_headers[headername]

    @property
    def types(self):
        return self._types

    @types.setter
    def types(self, types):
        '''
        Takes a list of Python `type`s, or `str`'s. A Python type
        might be int, float, or similar. A string might be
        "ISO8601-date."
        '''
        self._types = []
        for python_type in types:
            if isinstance(python_type, str):
                self._types.append(python_type)  # e.g. `ISO8601-date`
            else:
                self._types.append(python_type.__name__)  # e.g. `int`

    def add_metadata(self, key, value):
        '''
        Add an arbitrary key-value pair to the header
        '''
        self._metadata[key] = value

    def get_metadata(self, key):
        '''
        Read an arbitrary key-value pair from the header
        '''
        return self._metadata[key]

    def write_headers(self):
        '''
        When we've finished populating the headers, write them out with
        this call.
        '''
        if not self._variables:
            self._variables = [
                helpers.variable_from_string(header)
                for header
                in self._headers]

        if self._metadata:
            metadata = yaml.dump(self._metadata, default_flow_style=False)
            self.destination.write(metadata)
            self.destination.write("-"*10 + "\n")
        self.destination.write("\t".join(self._headers) + "\n")
        self.destination.write("\t".join(self._types) +
                               "\t(types)\n")
        self.destination.write("\t".join(self._variables) +
                               "\t(variables)\n")
        for key in sorted(self.extra_headers):
            values = self.extra_headers[key]
            self.destination.write("\t".join(values) +
                                   "\t("+key+")\n")

        self.destination.write("-"*10 + "\n")

    def write(self, *args):
        '''
        Write a row into the TSV file. Takes items to write as
        arguments in their native types. Passes all items in the array
        through an encoder to convert them into the correct strings,
        adds tabs, and writes them.
        '''
        if len(args) != len(self._types):
            raise ValueError(
                "Length of row items {rows} does not match "
                "number of rows {types}: {arg}".format(
                    rows=len(args),
                    types=len(self._types),
                    arg=repr(args)
                )
            )
        encoded = [
            parser.encode(item, item_type)
            for item, item_type
            in zip(args, self._types)
        ]
        self.destination.write("\t".join(encoded)+"\n")

    def close(self):
        '''
        This closes the stream associated with the writer.
        '''
        self.destination.close()
