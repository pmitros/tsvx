'''
The TSVxReader, TSVxWriter, and TSVxLine objects.
'''

import datetime
import sys
import yaml

import parser


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
        if not attr.isalnum():
            raise exceptions.TSVXFileFormatException(
                "TSVx variables must be alphanumeric. " + attr
            )
        index = self.parent.variable_index(attr)
        return self.line[index]

    def __getitem__(self, attr):
        if isinstance(attr, basestring):
            if not attr.isalnum():
                raise exceptions.TSVXFileFormatException(
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
        return self.parent.line_header['var']


class TSVxReaderWriter(object):
    def __repr__(self):
        return yaml.dump(self.metadata)+"/"+str(self.line_header)

    def variable_index(self, variable):
        if 'var' not in self.line_header:
            raise "No defined variable names"
        if variable not in self.line_header['var']:
            raise "Variable undefined"
        return self.line_header['var'].index(variable)


class TSVxReader(TSVxReaderWriter):
    def __init__(self,
                 metadata,
                 line_header,
                 generator):
        '''
        Create a new TS
        '''
        self.metadata = metadata
        self.line_header = line_header
        self.generator = generator

    def get_types(self):
        return self.line_header['types']

    def __iter__(self):
        return (TSVxLine(x, self) for x in self.generator)


class TSVxWriter(TSVxReaderWriter):
    def __init__(self, destination):
        self.destination = destination
        self.metadata = {
            "created-date": datetime.datetime.utcnow().isoformat(),
            "generator": sys.argv[0]
        }
        self.line_header = dict()

    def headers(self, headers):
        self._headers = headers

    def variables(self, variables):
        self._variables = variables

    def types(self, types):
        self._types = list()
        for t in types:
            if isinstance(t, basestring):
                self._types.append(t)
            else:
                self._types.append(t.__name__)

    def title(self, title):
        self.metadata['title'] = title

    def write_headers(self):
        if self.metadata:
            metadata = yaml.dump(self.metadata, default_flow_style=False)
            self.destination.write(metadata)
            self.destination.write("-"*10 + "\n")
        self.destination.write("\t".join(self._headers) + "\n")
        self.destination.write("types:\t" +
                               "\t".join([x for x in self._types]) +
                               "\n")

        self.destination.write("-"*10 + "\n")

    def write(self, *args):
        encoded = [
            parser.encode(item, item_type)
            for item, item_type
            in zip(args, self._types)
        ]
        self.destination.write("\t".join(encoded)+"\n")
