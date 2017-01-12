import MySQLdb
import click
import tsvx


def mysql_connect(arguments):
    '''
    Given arguments from docopt, connect to a database, and return the
    cursor object
    '''
    db = MySQLdb.connect(host=arguments["--host"],
                         port=int(arguments["--port"]),
                         user=arguments["--user"],
                         passwd=arguments["--password"],
                         db=arguments["--database"])
    c = db.cursor()
    return c


def scrape_mysql_table_to_tsvx(filename, cursor, database, table,
                               row_limit, max_step):
    '''
    Scrape a MySQL table, outputting to a TSVx file. This is the
    top-level helper function.

    The way 'rows' is passed around is a bit of a hack.
    '''
    writer = tsvx.writer(open(filename, "w"))

    # Get table headers and information
    rows = write_table_metadata(
        cursor, writer, database, table, row_limit
    )

    # Figure out how to partition the data
    id_range = partition_data(
        cursor, writer, table, rows,
        row_limit, max_step)

    # Now, grab the data itself
    grab_table_data(cursor, writer, table, id_range)


def write_table_metadata(cursor, writer, database, table, row_limit=None):
    '''
    Ask the database about the table. Extract the metadata. Write
    it to a TSVx writer.
    '''
    writer.title("MySQL Export of %s from %s" % (table, database))
    cursor.execute("DESCRIBE " + table)
    headers = [i[0] for i in cursor.description]
    rowdata = list(cursor)

    for key, value in zip(headers, zip(*rowdata)):
        if key == "Field":
            writer.headers(value)
        elif key == "Type":
            writer.python_types(map(mysql_to_python_type, value))
        else:
            writer.line_header("mysql-"+key.lower(), map(str, value))

    cursor.execute('show table status where Name="'+table+'";')
    keys = [t[0] for t in cursor.description]
    values = list(cursor)[0]
    for (key, value) in zip(keys, values):
        if type(value) == long and value == int(value):
            value = int(value)
        if key.lower() == "rows":
            if row_limit:
                value = int(row_limit)
            rows = value
        writer.add_metadata("mysql-"+key.lower(), value)
    return rows


def partition_data(cursor, writer, table, rows, row_limit, max_step):
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
    id_range = []
    if max_step:
        step = int(max_step)
        with click.progressbar(range(0, rows, step), show_pos=True) as steps:
            for offset in steps:
                cursor.execute('select id from ' +
                               table +
                               ' order by id limit 1 offset %s;' % (offset))
                id_range.append(list(cursor)[0][0])
    else:
        cursor.execute('select min(id) from '+table+';')
        id_range.append(list(cursor)[0][0])

    if not row_limit:
        cursor.execute('select max(id) from '+table+';')
    else:
        cursor.execute('select id from ' +
                       table +
                       ' order by id limit 1 offset %s;' % (rows))
    id_range.append(list(cursor)[0][0]+1)
    print "Partitions:", id_range
    writer.write_headers()
    return id_range


def grab_table_data(cursor, writer, table, id_range):
    '''
    Step through a table, in blocks of the partitions, and write out
    the rows to a TSVx file.
    '''
    print "Grabbing data for "+table
    ranges = zip(id_range[:-1], id_range[1:])
    with click.progressbar(ranges) as steps:
        for min_id, max_id in steps:
            sql_command = "select * from {table} where " \
                          "id >= {min_id} and id < {max_id};".format(
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
