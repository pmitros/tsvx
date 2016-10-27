import yaml

class FileFormatException(Exception):
    pass

class TSVxLine:
    def __init__(self, line_string, parent):
        self.line_string = line_string[:-1].split('\t')
        self.parent = parent

    def __repr__(self):
        return "/".join(self.line_string)

    def __str__(self):
        return "/".join(self.line_string)

    def __unicode__(self):
        return "/".join(self.line_string)

    def __getattr__(self, attr):
        if not attr.isalnum():
            raise AttributeError("TSVx variables must be alphanumeric")
        index = self.parent.variable_index(attr)
        return self.line_string[index]

    def __getitem__(self, attr):
        if isinstance(attr, basestring):
            if not attr.isalnum():
                raise AttributeError("TSVx variables must be alphanumeric")
            index = self.parent.variable_index(attr)
            return self.line_string[index]
        elif isinstance(attr, int):
            return self.line_string[attr]

    def __len__(self):
        return len(self.line_string)

    def __iter__(self):
        for item in self.line_string:
            yield item

    def values(self):
        return self.line_string

    def keys(self):
        return self.parent.line_header['var']

class TSVx:
    def __init__(self, metadata, line_header, generator):
        self.metadata = metadata
        self.line_header = line_header
        self.generator = generator

    def __iter__(self):
        return (TSVxLine(x, self) for x in self.generator)

    def __repr__(self):
        return yaml.dump(self.metadata)+"/"+str(self.line_header)

    def variable_index(self, variable):
        if 'var' not in self.line_header:
            raise "No defined variable names"
        if variable not in self.line_header['var']:
            raise "Variable undefined"
        return self.line_header['var'].index(variable)
