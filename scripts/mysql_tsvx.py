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
                [--row-limit=row-limit] [--seq-id-partition]

Options:
  --output=filename     What file to output to. Otherwise, generate.
                        a filename based on database and table name.
  --overwrite           If set, will overwrite file if it exists.
  --max-step=step-size  Maximum number of rows to grab in one query. If
                        you do want consistency, set this to be larger
                        than the database.
  --row-limit=row-limit Only grab the first few rows. Useful for debugging!
  --seq-id-partition    With a maximum step, just partition based on steps
                        between minimum ID and maximum ID. Much faster for
                        numeric, sequential IDs. Might be very slow with
                        non-sequential IDs. Doesn't work with string IDs.
'''

import docopt
import sys
import os.path

import helpers

arguments = docopt.docopt(__doc__)
cursor = helpers.mysql_connect(arguments)

if not arguments["--output"]:
    filename = arguments["--database"] + \
               "-" + arguments["--table"] + ".tsvx"
else:
    filename = arguments["--output"]

print "Saving to "+filename

if os.path.exists(filename) and not arguments["--overwrite"]:
    print "File %s exists" % (filename)
    sys.exit(-1)

if arguments["--seq-id-partition"] and not arguments["--max-step"]:
    print "Invalid arguments. --seq-id-partition requires a --max-step for the partitioning"
    print "Try adding --max-step=100000"
    sys.exit(1)

helpers.scrape_mysql_table_to_tsvx(
    filename, cursor, arguments["--database"], arguments["--table"],
    arguments["--row-limit"], arguments["--max-step"],
    arguments["--seq-id-partition"]
)
