'''
This script is unfinished. It will dump a MySQL database to a series of
mysqldump files, one per table. If specific files time out, it will 
dump those tables to tsvx files instead, by sets of rows. 

Dumping big databases often times out. This method doesn't give
transactional-style coherency, but does give a reliable dump.

This script is kind of useable, but you need to read it to use it, and
comment lines in/out. Step 1: Comment in mysqldump lines. Step 2: 
Comment them out and comment in TSVX lines.

Usage:
  mysql_fulldb.py --host=host --user=user --port=port
                  --password=password --database=database
                  [--output=directory]
                  [--max-step=maximum-step] [--row-limit=row-limit]
                  [--dry-run]
'''

import MySQLdb
import docopt
import random
import subprocess
import sys
import os
import os.path
import subprocess

import helpers

arguments = docopt.docopt(__doc__)
cursor = helpers.mysql_connect(arguments)
database = arguments["--database"]

if not arguments["--output"]:
    directory = database+"-tsvx-dump"
else:
    directory = arguments["--output"]

print "Saving to " + directory

if not os.path.exists(directory) and not arguments["--dry-run"]:
    os.mkdir(directory)

dry_run_tsvx = set()
dry_run_needed = set()
dry_run_mysql = set()

cursor.execute("show tables;")
ordered_cursor = list(cursor)
random.shuffle(ordered_cursor)
for table in ordered_cursor:
    filename=directory+"/"+table[0]

    if arguments["--dry-run"]:
        if os.path.exists(filename+".0.gz"):
            dry_run_mysql.add(table[0])
        elif os.path.exists(filename+".tsvx.gz"):
            dry_run_tsvx.add(table[0])
        else:
            dry_run_needed.add(table[0])

    if os.path.exists(filename+".0.gz") or os.path.exists(filename+".0.tsvx.gz"):
        print "Skipping", filename
        continue
    
    print "Dumping", table, "to", filename
    if arguments["--dry-run"]:
        continue

    # output = subprocess.call(
    #     ["mysqldump",
    #      "--single-transaction",
    #      "-u",
    #      arguments["--user"],
    #      "-h",
    #      "127.0.0.1",
    #      "-P",
    #      arguments["--port"],
    #      "-p"+arguments["--password"],
    #      "--result-file="+filename,
    #      arguments["--database"],
    #      table[0]]
    # )
    output = subprocess.call(
        ["python", "mysql_tsvx.py",
         "--user="+arguments["--user"],
         "--host=127.0.0.1",
         "--port="+arguments["--port"],
         "--password="+arguments["--password"],
         "--output="+filename+".tsvx.gz",
         "--database="+arguments["--database"],
         "--table="+table[0], "--max-step=100000", "--seq-id-partition"]
    )
    # newfilename = filename+"."+str(output)

    # newfilename = filename+"."+str(output)
    # print "Moving", filename, "to", newfilename
    # os.rename(filename, newfilename)
    os.rename(filename+".tsvx.gz", filename+"."+str(output)+".tsvx.gz")
    
    if output == 0:
        #subprocess.call(["gzip", newfilename])
        
        print "Success!"
    else:
        print "Failure :("

    # table = table[0]
    # filename = os.path.join(directory, table + ".tsvx.gz")
    # if os.path.exists(filename):
    #     print "Skipping", filename
    # else:
    #     print filename
    #     helpers.scrape_mysql_table_to_tsvx(
    #         filename, cursor, arguments["--database"], table,
    #         arguments["--row-limit"], arguments["--max-step"]
    #     )

if arguments["--dry-run"]:
    print "SQL Dump:", " ".join(sorted(dry_run_mysql))
    print "TSVX Dump:", " ".join(sorted(dry_run_tsvx))
    print "Needed:", " ".join(sorted(dry_run_needed))
