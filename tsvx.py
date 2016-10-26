import itertools
import yaml

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
            print ">>>>", attr
            raise "TSVx variables must be alphanumeric"
        index = self.parent.variable_index(attr)
        return self.line_string[index]

    def __getitem__(self, attr):
        if isinstance(attr, basestring):
            if not attr.isalnum():
                raise "TSVx variables must be alphanumeric"
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

def reader(to_be_parsed):
    if isinstance(to_be_parsed, basestring):
        return _parse_generator(to_be_parsed.split("\n"))
    else:
        return _parse_generator(to_be_parsed)

def peek(generator):
    '''
    Return the first item in the generator. Usage
       (first, generator) = peek(generator)
    '''
    first = generator.next()
    generator = itertools.chain([first], generator)
    return (first, generator)

def read_to_dash(generator):
    '''
    Read a file until a set of dashes is encountered
    '''
    lines = []
    for line in generator:
        if line.startswith('---'):
            break
        lines.append(line)
    return "\n".join(lines)

def _parse_generator(generator):
    (first, generator) = peek(generator)
    if ":" in first:
        metadata = yaml.load(read_to_dash(generator))
    else:
        metadata = {}

    column_names = generator.next()[:-1].split('\t')

    line_headers = dict()

    for line in generator:
        if line.startswith('---'):
            break
        key = line.split(':')[0]
        value = ":".join(line[:-1].split(':')[1:]).split('\t')[1:]
        line_headers[key] = value

    return TSVx(metadata, line_headers, generator)

if __name__ == '__main__':
    t = reader(open("example.tsvx"))
    print t
    for line in t:
        print line
        print line.foodname, line.weight, line.price, line.expiration
        print line.keys()
        for key in line.keys():
            print line[key],
        for i in range(len(line)):
            print line[i],
        print dict(line)
        print list(line)
