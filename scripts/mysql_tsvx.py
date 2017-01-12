'''Dump a MySQL table to a TSVx file

This is a script which will dump a MySQL table to a TSVx file. In some
modes of operation, it does NOT guarantee consistency. For large MySQL
tables, doing a SELECT * will cause serious performance
issues. Instead, this script will grab table rows in steps of
e.g. 100,000 rows at a time. It will first figure out how to partition
the table (IDs are often not contiguous). Then it will select rows in
ranges. If you do want consistency, don't set a step size, and it will
grab the whole table (but this may be slow).

Note that the progress bar gives an estimate. For large tables, it may
slow down (in MySQL, large offsets sometimes take longer than small
offsets). This very noticable for the partitioning step, and less
significant for the data step itself.

Usage:
  mysql_tsvx.py --host=host --user=user --port=port
                --password=password --database=database
                --table=table  [--output=filename]
                [--overwrite] [--max-step=maximum-step]
                [--row-limit=row-limit]

Options:
  --output=filename     What file to output to. Otherwise, generate.
                        a filename based on database and table name.
  --overwrite           If set, will overwrite file if it exists.
  --max-step=step-size  Maximum number of rows to grab in one query. If
                        you do want consistency, set this to be larger
                        than the database.
  --row-limit=row-limit Only grab the first few rows. Useful for debugging!

'''

import MySQLdb
import click
import docopt
import subprocess
import sys
import tsvx
import os.path

# Configuration: Parse arguments, open database, open file, etc.

arguments = docopt.docopt(__doc__)
db = MySQLdb.connect(host=arguments["--host"],
                     port=int(arguments["--port"]),
                     user=arguments["--user"],
                     passwd=arguments["--password"],
                     db=arguments["--database"])

if not arguments["--output"]:
    filename = arguments["--database"]+"-" + arguments["--table"] + ".tsvx"
else:
    filename = arguments["--output"]

print "Saving to "+filename

if os.path.exists(filename) and not arguments["--overwrite"]:
    print "File %s exists" % (filename)
    sys.exit(-1)

w = tsvx.writer(open(filename, "w"))
c = db.cursor()

# Get table headers and information#

c.execute("DESCRIBE " + arguments["--table"])
headers = [i[0] for i in c.description]
l = list(c)


def mysql_type_to_python_type(type_string):
    '''
    Convert a MySQL type (for instance, 'varchar(80)') to a corresponding
    Python type (in this case, 'str').
    '''
    mysql_type_map = {
        "varchar": str,
        "int": int,
        "tinyint": int,
        "smallint": int,
        "longtext": str,
        "date": "ISO8601-date",
        "datetime": "ISO8601-datetime"
    }
    for t in sorted(mysql_type_map, key=lambda x: -len(x)):
        if type_string.startswith(t):
            return mysql_type_map[t]
    raise ValueError("Cannot convert %s to a Python type. "
                     "Please add it to the mysql_type_map "
                     "in this file" % (type_string))

for key, value in zip(headers, zip(*l)):
    if key == "Field":
        w.headers(value)
    elif key == "Type":
        w.python_types(map(mysql_type_to_python_type, value))
    else:
        w.line_header("mysql-"+key.lower(), map(str, value))

w.title("MySQL Export of %s from %s" % (arguments["--table"],
                                        arguments["--database"]))

c.execute('show table status where Name="'+arguments["--table"]+'";')
keys = [t[0] for t in c.description]
values = list(c)[0]
for (key, value) in zip(keys, values):
    if type(value) == long and value == int(value):
        value = int(value)
    if key.lower() == "rows":
        rows = value
        if arguments["--row-limit"]:
            rows = int(arguments["--row-limit"])
            value = rows
    w.add_metadata("mysql-"+key.lower(), value)

# Figure out how to partition the data

print "Partioning data"
id_range = []
if arguments["--max-step"]:
    step = int(arguments["--max-step"])
    with click.progressbar(range(0, rows, step), show_pos=True) as steps:
        for offset in steps:
            c.execute('select id from ' +
                      arguments["--table"] +
                      ' order by id limit 1 offset %s;' % (offset))
            id_range.append(list(c)[0][0])
else:
    c.execute('select min(id) from '+arguments["--table"]+';')
    id_range.append(list(c)[0][0])

if not arguments["--row-limit"]:
    c.execute('select max(id) from '+arguments["--table"]+';')
else:
    c.execute('select id from ' +
              arguments["--table"] +
              ' order by id limit 1 offset %s;' % (rows))
id_range.append(list(c)[0][0]+1)
print "Partitions:", id_range
w.write_headers()

# Now, grab the data itself

print "Grabbing data"
ranges = zip(id_range[:-1], id_range[1:])
with click.progressbar(ranges) as steps:
    for min_id, max_id in steps:
        sql_command = "select * from {table} where " \
                      "id >= {min_id} and id < {max_id};".format(
                          table=arguments["--table"],
                          min_id=min_id,
                          max_id=max_id
                      )
        c.execute(sql_command)
        for row in c:
            w.write(*row)
w.close()
print "Done!"
