'''
UNFINISHED

This script will, once finished, output a Mongo table as a TSVx
file. It's a two-pass process. Pass 1 discovers the schemaless
schema. Pass two exports it with that schema.

It doesn't work very well on edX data; we have values in keys. That's
why it's unfinished

Usage:
  mongo_tsvx.py --host=host --user=user --port=port
                --password=password --database=database
                --collection=collection
                --omits=omits

'''

import docopt
from pymongo import MongoClient
import helpers

arguments = docopt.docopt(__doc__)
host = arguments["--host"]
port = int(arguments["--port"])
password = arguments["--password"]
database = arguments["--database"]
collection = arguments["--collection"]
username = arguments["--user"]

client = MongoClient(host, port)
db = client[database]
db.authenticate(username, password)
fields = helpers.probe_mongo_schema(
    client, database, collection, omits=arguments["--omits"].split(",")
)
