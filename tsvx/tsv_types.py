'''
The TSVxReader, TSVxWriter, and TSVxLine objects.
'''

import datetime
import sys
import yaml

import helpers
import parser
import exceptions


class TSVxLine(object):
    '''
    Represents a single line in the reader object. Lets you work
    with the attributes as a dict-like object, a list-like object,
    or as attributes.

    That might be overkill, but we'd like to see what's most useful.
    '''
    def __init__(self, line_string, parent):
        '''
        Create a line based on string of the line. Strip the
        newline. Split on tabs. And parse
        '''
        split_line = line_string[:-1].split('\t')
        self.line = list()
        for item, item_type in zip(split_line, parent.get_types()):
            self.line.append(parser.parse(item, item_type))

        self.parent = parent

    def __repr__(self):
        return "/".join(repr(item) for item in self.line)

    def __str__(self):
        return "/".join(str(item) for item in self.line)

    def __unicode__(self):
        return "/".join(unicode(item) for item in self.line)

    def __getattr__(self, attr):
        if not helpers.valid_variable(attr):
            raise exceptions.TSVxFileFormatException(
                "TSVx variables must be alphanumeric. " + attr
            )
            if attr.beginswith('_'):
                raise exceptions.TSVxSuscpiciousOperation(
                    "Strange attribute " + attr +
                    ". Use get instead of attribute referencing")
        index = self.parent.variable_index(attr)
        return self.line[index]

    def __getitem__(self, attr):
        if isinstance(attr, basestring):
            if not helpers.valid_variable(attr):
                raise exceptions.TSVxFileFormatException(
                    "TSVx variables must be alphanumeric. " + attr
                )
            index = self.parent.variable_index(attr)
            return self.line[index]
        elif isinstance(attr, int):
            return self.line[attr]

    def __len__(self):
        return len(self.line)

    def __iter__(self):
        for item in self.line:
            yield item

    def values(self):
        return self.line

    def keys(self):
        return self.parent._line_header['variables']


class TSVxReaderWriter(object):
    def __repr__(self):
        return yaml.dump(self.metadata)+"/"+str(self._line_header)

    def variable_index(self, variable):
        if 'variables' not in self._line_header:
            raise exceptions.TSVxFileFormatException(
                "No defined variable names: " + variable)
        if variable not in self._line_header['variables']:
            raise exceptions.TSVxFileFormatException(
                "Variable undefined: " + variable)
        return self._line_header['variables'].index(variable)


class TSVxReader(TSVxReaderWriter):
    def __init__(self,
                 metadata,
                 line_header,
                 generator):
        '''
        Create a new TS
        '''
        self.metadata = metadata
        self._line_header = line_header
        self.generator = generator

    def get_types(self):
        return self._line_header['types']

    def __iter__(self):
        return (TSVxLine(x, self) for x in self.generator)


class TSVxWriter(TSVxReaderWriter):
    def __init__(self, destination):
        self.destination = destination
        self.metadata = {
            "created-date": datetime.datetime.utcnow().isoformat(),
            "generator": sys.argv[0]
        }
        self._line_header = dict()
        self._variables = None

    def headers(self, headers=None):
        if headers:
            self._headers = headers
        else:
            return self._headers

    def variables(self, variables):
        self._variables = variables

    def line_header(self, headername, values=None):
        if values:
            self._line_header[headername] = values
        else:
            return self._line_header[headername]

    def python_types(self, types):
        '''
        Takes a list of Python types, or strings. A Python type
        might be int, float, or similar. A string might be
        "ISO8601-date."

        Populates the type information based on this.
        '''
        self._types = list()
        for t in types:
            if isinstance(t, basestring):
                self._types.append(t)
            else:
                self._types.append(t.__name__)

    def title(self, title):
        self.metadata['title'] = title

    def description(self, description):
        self.metadata['description'] = description

    def add_metadata(self, key, value):
        self.metadata[key] = value

    def get_metadata(self, key):
        return self.metadata[key]

    def write_headers(self):
        if not self._variables:
            self._variables = [
                helpers.variable_from_string(header)
                for header
                in self._headers]

        if self.metadata:
            metadata = yaml.dump(self.metadata, default_flow_style=False)
            self.destination.write(metadata)
            self.destination.write("-"*10 + "\n")
        self.destination.write("\t".join(self._headers) + "\n")
        self.destination.write("\t".join([x for x in self._types]) +
                               "\t(types)\n")
        self.destination.write("\t".join([x for x in self._variables]) +
                               "\t(variables)\n")
        for key in sorted(self._line_header):
            values = self._line_header[key]
            self.destination.write("\t".join([x for x in values]) +
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
        Convenience function so we don't need to keep file pointers
        around. This closes the stream associated with the writer.
        '''
        self.destination.close()
