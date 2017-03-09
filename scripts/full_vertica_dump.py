'''
Dump a full Vertica database into a directory.

Usage:
  full_vertica_dump.py --output=output_directory
                       [--host=host] [--user=user] [--port=port]
                       [--password=password] [--database=database]
                       [--prefix=prefix]

One must specify either host, user, port, database, and password, or
prefix. If prefix is specified, said information will be taken
from environment variables
'''

import docopt
import gzip
import os
import sys
import vertica_python
import vertica_python.errors

import tsvx

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
    database=argument('database'),
    unicode_error='replace'
)

cur = connection.cursor('dict')
cur.execute("select * from ALL_TABLES;");
for item in list(cur.iterate()):
    query = "select * from {schema_name}.{table_name};".format(
        schema_name=item['schema_name'],
        table_name=item['table_name']
    )
    title = str(item['remarks'])
    if title is None:
        title = "Vertica dump"
    description = "Vertica dump from query: " + query
    filename = "{schema_name}.{table_name}.tsvx.gz".format(
        schema_name=item['schema_name'],
        table_name=item['table_name']
    )
    pathname = os.path.join(arguments['--output'], filename)
    print pathname
    print title
    print description
    print query
    if os.path.exists(pathname):
        print "Already exists"+pathname
        continue
    fp = gzip.open(pathname, "w")
    tsvx_writer = tsvx.writer(fp)
    tsvx_writer.title(title)
    tsvx_writer.description(description)
    try:
        helpers.query_vertica_to_tsvx(
            cur,
            query,
            tsvx_writer
        )
    except vertica_python.errors.PermissionDenied:
        fp.write("Permission denied")
        fp.close()
        print "Permission denied on "+pathname
    except StopIteration:
        fp.write("Empty table")
        fp.close()
        print "Empty Table "+pathname
    except:
        tsvx_writer.close()
        os.unlink(pathname)
        raise
    print
    tsvx_writer.close()
