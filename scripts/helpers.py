import MySQLdb
import click
import collections
import gzip
import numbers
import tsvx

mysql_escape = None


def mysql_connect(arguments):
    '''
    Given arguments from docopt, connect to a database, and return the
    cursor object
    '''
    global mysql_escape
    db = MySQLdb.connect(host=arguments["--host"],
                         port=int(arguments["--port"]),
                         user=arguments["--user"],
                         passwd=arguments["--password"],
                         db=arguments["--database"])
    mysql_escape = db.escape_string
    c = db.cursor()
    return c


def scrape_mysql_table_to_tsvx(filename, cursor, database, table,
                               row_limit, max_step, sequential_id=False):
    '''
    Scrape a MySQL table, outputting to a TSVx file. This is the
    top-level helper function.

    The way 'rows' is passed around is a bit of a hack.
    '''
    if filename.endswith(".gz"):
        stream = gzip.open(filename, "w")
    elif filename.endswith("tsvx"):
        stream = open(filename, "w")
    writer = tsvx.writer(stream)

    # Get table headers and information
    write_table_metadata(
        cursor, writer, database, table, row_limit
    )

    if writer.get_metadata('mysql-rows') == "0":
        writer.close()
        return

    # Figure out how to partition the data
    if not sequential_id:
        id_range = partition_data(
            cursor, writer, table,
            row_limit, max_step)
    else:
        id_range = sequential_partition_data(
            cursor, writer, table,
            row_limit, max_step)
    # Now, grab the data itself
    if id_range is not None:
        grab_table_data(cursor, writer, table, id_range)
    else:
        writer.close()


def primary_key(writer):
    '''
    For a TSVx writer with MySQL metadata, return the primary key
    '''
    pri_key_index = writer.line_header("mysql-key").index("PRI")
    pri_key = writer.headers()[pri_key_index]
    return pri_key


def write_table_metadata(cursor, writer, database, table, row_limit=None):
    '''
    Ask the database about the table. Extract the metadata. Write
    it to a TSVx writer.
    '''
    # First, we grab column headers
    writer.title("MySQL Export of %s from %s" % (table, database))
    cursor.execute("DESCRIBE " + table)
    headers = [i[0] for i in cursor.description]
    rowdata = list(cursor)

    # Now we write them into the appropriate fields
    for key, value in zip(headers, zip(*rowdata)):
        if key == "Field":
            writer.headers(value)
        elif key == "Type":
            writer.python_types(map(mysql_to_python_type, value))
        else:
            writer.line_header("mysql-"+key.lower(), map(str, value))

    # Now we grab the metadata for the whole table
    cursor.execute('show table status where Name="'+table+'";')
    keys = [t[0] for t in cursor.description]
    values = list(cursor)[0]
    for (key, value) in zip(keys, values):
        if type(value) == long and value == int(value):
            value = int(value)
        if key.lower() == "rows":
            if row_limit:
                if value > int(row_limit):
                    value = int(row_limit)
        writer.add_metadata("mysql-"+key.lower(), value)
    writer.write_headers()


def sequential_partition_data(cursor, writer, table, row_limit, max_step):
    '''
    We use this to return a set of breakpoints of table IDs so we can
    grab the database in steps. Grabbing a whole table is a bit
    expensive. This takes the shortcut of assuming IDs are numeric and
    sequential.  Fast if they are, breaks if they aren't.
    '''
    print "Partioning data"
    pri_key = primary_key(writer)
    cursor.execute('select min(`{pri}`), max(`{pri}`) from {table};'.format(
            pri=pri_key,
            table=table
        ))
    (min_id, max_id) = (list(cursor)[0])

    print "Data range is: ", min_id, max_id

    if row_limit and max_id-min_id < row_limit:
        r = [min_id, min_id+row_limit+1]
        print "Full range", r
    else:
        r = range(min_id, max_id, int(max_step)) + [max_id + 1]
        print "Partitions", r
    return r


def partition_data(cursor, writer, table, row_limit, max_step):
    '''
    We use this to return a set of breakpoints of table IDs so we can
    grab the database in steps. Grabbing a whole table is a bit
    expensive. This will step through the IDs, and return the ID at
    every max_step, and finally the maximum ID plus one.

    If max_step isn't set, it will return (min, max+1)

    If row_limit is set, it will only do that many rows in the table
    (useful for debugging).
    '''
    print "Partioning data"
    rows = writer.get_metadata('mysql-rows')
    id_range = []
    pri_key = primary_key(writer)
    if max_step:
        step = int(max_step)
        with click.progressbar(range(0, rows, step), show_pos=True) as steps:
            for offset in steps:
                cursor.execute(
                    'select `{pri}` from {table} order by `{pri}` '
                    'limit 1 offset {offset};'.format(
                        table=table,
                        pri=pri_key,
                        offset=offset)
                )
                offset_list = list(cursor)
                if len(offset_list) > 0:
                    id_range.append(offset_list[0][0])
                else:
                    continue
    else:
        cursor.execute('select min(`{pri}`) from {table};'.format(
            pri=pri_key,
            table=table
        ))
        id_range.append(list(cursor)[0][0])

    # This is a little complex so we can handle the case where there are fewer
    # rows than the limit
    row_max = None
    if row_limit:
        cursor.execute(
            'select `{pri}` from {table} order by `{pri}` '
            'limit 1 offset {rows};'.format(
                pri=pri_key,
                table=table,
                rows=rows))
        offset_list = list(cursor)
        if len(offset_list) > 0:
            row_max = offset_list[0][0]

    if row_max is None:
        cursor.execute('select max(`{pri}`) from {table};'.format(
            pri=pri_key,
            table=table
        ))

        max_id_list = list(cursor)
        if len(max_id_list) > 0 and max_id_list[0][0] is not None:
            last_row = max_id_list[0][0]
            if isinstance(last_row, numbers.Number):
                row_max = last_row + 1
            elif isinstance(last_row, basestring):
                row_max = last_row + 'Z'
        else:
            return None

    id_range.append(row_max)

    if isinstance(id_range[0], basestring):
        id_range = ['"{id}"'.format(id=mysql_escape(id)) for id in id_range]

    print "Partitions:", id_range
    return id_range


def grab_table_data(cursor, writer, table, id_range):
    '''
    Step through a table, in blocks of the partitions, and write out
    the rows to a TSVx file.
    '''
    print "Grabbing data for "+table
    ranges = zip(id_range[:-1], id_range[1:])
    pri_key = primary_key(writer)
    with click.progressbar(ranges) as steps:
        for min_id, max_id in steps:
            sql_command = "select * from {table} where " \
                          '`{pri}` >= {min_id} and `{pri}` < {max_id};'.format(
                              pri=pri_key,
                              table=table,
                              min_id=min_id,
                              max_id=max_id
                          )
            cursor.execute(sql_command)
            for row in cursor:
                writer.write(*row)
    writer.close()
    print "Done!"


def mysql_to_python_type(type_string):
    '''
    Convert a MySQL type (for instance, 'varchar(80)') to a corresponding
    Python type (in this case, 'str').
    '''
    mysql_type_map = {
        "varchar": str,
        "int": int,
        "tinyint": int,
        "smallint": int,
        "bigint": int,
        "longtext": str,
        "decimal": float,
        "single": float,
        "double": float,
        "char": str,
        "date": "ISO8601-date",
        "datetime": "ISO8601-datetime"
    }
    for t in sorted(mysql_type_map, key=lambda x: -len(x)):
        if type_string.startswith(t):
            return mysql_type_map[t]
    raise ValueError("Cannot convert %s to a Python type. "
                     "Please add it to the mysql_type_map "
                     "in this file" % (type_string))


def probe_mongo_schema(mongoclient, database, collection, omits=None):
    '''
    Create a dictionary of all the field names in a Mongo database,
    and their associated types. Takes a MongoClient, a database name,
    and a collection name. Returns a dictionary mapping field names
    (e.g. "top_level.mid_level.bottom_level") to lists of types which
    occur under that name.
    '''
    def flatson(fields, json, prefix=""):
	'''
        Helper script to recursively crawl JSON dictionary, extract types,
        and convert to dot format.
        '''
        for key in json:
            if key in omits:
                fields[prefix+key].add(type(json[key]).__name__)
            elif isinstance(json[key], dict):
                flatson(fields, json[key], prefix+key+".")
            else:
                fields[prefix+key].add(type(json[key]).__name__)
        return fields

    cursor = mongoclient[database][collection].find()
    fields = collections.defaultdict(lambda: set())
    for item in cursor:
        flatson(fields, item)
    return dict(fields)
