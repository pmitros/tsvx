'''Grab a query from Vertica.

This is a script which will dump a VSQL query to a TSVx file.

Usage:
  tsvx2vertica.py --query=query --file=tsvxfile
                  [--host=host] [--user=user] [--port=port]
                  [--password=password] [--database=database]
                  [--prefix=prefix]
                  [--drop] [--create]

One must specify either host, user, port, database, and password, or
prefix. If prefix is specified, said information will be taken
from environment variables
'''

import docopt
import gzip
import itertools
import os
import os.path
import sys
import tsvx
import vertica_python

import tsvx.helpers

arguments = docopt.docopt(__doc__)

def argument(x):
    if "--"+x in arguments and arguments["--"+x]:
        return arguments["--"+x]
    elif "--prefix" in arguments and \
         arguments['--prefix']+"_"+x.upper() in os.environ:
        return os.environ[arguments["--prefix"]+"_"+x.upper()]
    else:
        raise Exception("Missing parameter " + x)

connection = vertica_python.connect(
    host=argument('host'),
    port=int(argument('port')),
    user=argument('user'),
    password=argument('password'),
    database=argument('database')
)

cur = connection.cursor('dict')
cur.execute(arguments['--query'])
first, rest = tsvx.helpers.peek(cur.iterate())

python_types = []
headers = []
variables = []
for key in first:
    t = type(first[key])
    # Typically, vertica_python uses future.types.newstr.newstr
    # We'd prefer 'unicode'
    if isinstance(first[key], basestring):
        t = str
    python_types.append(t)
    headers.append(key)
    variables.append(tsvx.helpers.variable_from_string(key))

filename  = arguments['--file']
if filename.lower().endswith(".gz"):
    fp = gzip.open(filename, "w")
else:
    fp = open(filename, "w")
w = tsvx.writer(fp)

w.python_types(python_types)
w.headers(headers)
w.variables(variables)
w.write_headers()

for line in rest:
    items = [line[key] for key in line]
    w.write(*items)

w.close()
