'''Grab a query from Vertica.

This is a script which will dump a VSQL query to a TSVx file.

Usage:
  tsvx2vertica.py --query=query --file=tsvxfile
                  [--host=host] [--user=user] [--port=port]
                  [--password=password] [--database=database]
                  [--prefix=prefix]
                  [--drop] [--create]
                  [--title=title]
                  [--description=description]

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

import helpers

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

filename = arguments['--file']
if filename.lower().endswith(".gz"):
    fp = gzip.open(filename, "w")
else:
    fp = open(filename, "w")
tsvx_writer = tsvx.writer(fp)

if arguments["--title"]:
    tsvx_writer.title(arguments["--title"])
else:
    tsvx_writer.title("Vertica query export")

if arguments["--description"]:
    tsvx_writer.description(arguments["--description"])
else:
    tsvx_writer.description("Vertica query export: {query}".format(
        query=arguments['--query']
    ))

helpers.query_vertica_to_tsvx(
    cur,
    arguments['--query'],
    tsvx_writer
)
