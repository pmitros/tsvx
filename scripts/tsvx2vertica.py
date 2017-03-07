'''Upload a TSVx file to Vertica

This is a script which will slowly upload a TSVx file to Vertica. It
has two modes of operation:

* Line-by-line (thanks, Uber library!), so slower than necessary, but
  gets the job done, eventually.
* Bulk transfers. No promises on escaping strings correctly (thanks,
  HP!)

Usage:
  tsvx2vertica.py --table=table --file=tsvxfile
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

cur = connection.cursor()

table_types = {
    'int': 'bigint',
    'str': 'varchar(64)',
    'float': 'float',
    'bool': 'boolean',
    'ISO8601-datetime': 'DATETIME'
    }

fp = gzip.open(arguments['--file'])
input_tsvx = tsvx.reader(fp)
vsql_types = [table_types[t] for t in input_tsvx.types()]
fields = ",\n    ".join(["{name} {type}".format(name=name, type=vsql_type)
                         for (name, vsql_type)
                         in zip(input_tsvx.variables(), vsql_types)])
create_command = "CREATE TABLE {table_name} ({fields});".format(
    table_name=arguments["--table"],
    fields=fields
)

if arguments['--drop']:
    cur.execute("DROP TABLE {table};".format(table=arguments["--table"]))
if arguments['--create']:
    cur.execute(create_command)

columns = ",".join(input_tsvx.variables())


def format(x):
    if isinstance(x, int) or isinstance(x, float):
        return str(x)
    elif isinstance(x, str) or isinstance(x, unicode):
        return "'"+x+"'"
    else:
        raise Exception(str(type(x)))

# Line-by-line insert
# Slow, but robust
if False:
    for line in input_tsvx:
        cur.execute("insert into {table} values ({values});".format(
            table=arguments["--table"],
            values=",".join([format(x) for x in line])
        ))
    connection.commit()

# CSV-style insert. Fast, but not well-vetted
if True:
    cur.copy("COPY {table} FROM stdin DELIMITER E'\t' NULL 'None';".format(
        tablex=arguments["--table"]), fp)
