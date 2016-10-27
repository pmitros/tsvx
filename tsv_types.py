import datetime
import sys
import yaml

import parser

class TSVxLine(object):
    def __init__(self, line_string, parent):
        '''
        Create a line based on string of the line. Strip the
        newline. Split on tabs. And parse
        '''
        split_line = line_string[:-1].split('\t')
        self.line = list()
        for item, item_type in zip(split_line, parent.get_types()):
            print item_type
            self.line.append(parser.parse(item, item_type))

        self.parent = parent

    def __repr__(self):
        return "/".join(self.line)

    def __str__(self):
        return "/".join(self.line)

    def __unicode__(self):
        return "/".join(self.line)

    def __getattr__(self, attr):
        if not attr.isalnum():
            raise AttributeError("TSVx variables must be alphanumeric")
        index = self.parent.variable_index(attr)
        return self.line[index]

    def __getitem__(self, attr):
        if isinstance(attr, basestring):
            if not attr.isalnum():
                raise AttributeError("TSVx variables must be alphanumeric")
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
        return self.line_header['python-types']
        
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
        self._types = types

    def title(self, title):
        self.metadata['title'] = title

    def write_headers(self):
        if self.metadata:
            metadata = yaml.dump(self.metadata, default_flow_style = False)
            self.destination.write(metadata)
            self.destination.write("-"*10 + "\n")
        self.destination.write("\t".join(self._headers) + "\n")
        self.destination.write("python-types:\t" + \
                               "\t".join([x.__name__ for x in self._types]) + \
                               "\n")

        self.destination.write("-"*10 + "\n")

    def write(self, *args):
        self.destination.write("\t".join(map(str, args))+"\n")
