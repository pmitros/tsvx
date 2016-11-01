# tsvx: Enhanced TSV Format

TSV is a nice format. It's human-readable, very fast to parse, and
concise. It's possible to process as a streaming format.

It's also painfully hard to work with due to lack of
standardization. Each file requires a different set of heuristics to
load. In addition, the columns must be parsed in a different way for
every file.

If this proposal is successful, ideally, e.g. a spreadsheet would be
able to open a MySQL export without prompting the user for help, and
pandas would be able to work with both.

This is a prototype for working with an enhanced TSV format. tsvx
files are a tab-seprated format, with several extensions:

* Columns are statically typed, and we standardize string escaping,
  dates, and formatting of other standard data types.
* We standardize on headers which provide column names and type
  metadata. Columns may have types, units, program-specific metadata,
  and otherwise.
* We standardize overall file metadata, which can provide a description
  of the content, providence, creation time, authors, and otherwise.

This is repository includes (at the time of this writing, the start
of) a simple parser for such files, so we can experiment with this
concept.

What it looks like
==================

    title: Food inventory
    created-date: 2016-10-29T15:25:29.449640
    ---------------------
    Food Name   Weight   Price       Expiration Date
    foodname    weight   netprice    exp             (variables)
    str         int      float       ISO8601-date    (types)
    String      Number   Number      String          (json)
    ---------------------
    Tuna        300      5.13        2017-10-12
    Salmon      150      7.18        2018-10-12
    Swordfish   250      9.41        2016-11-13
    ...

Why?
====

We have nice standards for documents (XML, as well as other markup
languages). We have nice standards for objects and configuration data
(YAML and JSON). We don't have any nice standards for tabular or
numerical dataa.

Numerical and tabular data is becoming increasingly important. It's
also increasingly being used across tools. We often see organizations
which have terabytes of data in systems like Hadoop and Vertica,
gigabytes in databases and flat files, and kilobytes of hand-curated
data in spreadsheets. Integration of data between such systems is
increasingly important.

Our design goals are:

* **Human-readability**
* **Basic interchange** between Excel, Google Docs, Hadoop,
  LibreOffice, MySQL, PostgreSQL, Python, R, Vertica, and others
  without extensive scripting. This doesn't need to be optimal (e.g. a
  fixed-sized string field might go to a variable-sized string), but
  it should be workable
* **Simplification of parsing code**, making processing scripts much
  simpler and less brittle. With tsvx, adding a column or changing
  column order doesn't break scripts.
* **Better reuse**. We have many TSV files sitting around, often years
  old, and often no great idea what's in them, or how to regenerate
  them on current data. We want to add such documentation in-line.
* Some **backwards-compatibility**. A tsvx file will open reasonably
  in a spreadsheet unaware of tsvx
* **Fast, single-pass processing**. I can reasonably work with
  tsvx files up to a few gigabytes
* **Extensibility**. Programs should be able to include enough
  metadata for meaningful import/export. If it becomes popular, tools
  like mysqldump should be able to build on top of this

Status
======

We will have a **request-for-comments period**, which we will probably
close off late 2016 or early 2017. Once we decide if this is a good
way to do this, I'll make this more production-ready, and perhaps
draft an IETF RFC or similar standard.

File Structure
==============

The file has three sections:

* **File metadata** (optional) -- Information about the file itself.
* **Column headings** (required) -- Metadata about the names and types
  in the columns
* **Data** (required) -- What one might traditionally find in a TSV
  file.

Sections are seperated by a line of all dashes, containing at least
three dashes. If the first section is omitted, the file should start
with a line of dashes.

File Metadata
=============

The metadata is a YAML dictionary. The first line must contain a
colon, but we recommend having all lines in this format. Stadard
fields include:

* `authors` -- JSON list of authors
* `created-date` -- ISO8601 date and time of when the file was created
* `description` -- A multiline description
* `generator` -- Some identifier of the program or source which created
  the file
* `modified-date` -- ISO8601 date and time of last modification
* `title` -- A single line title/description

Headers/Column Metadata
=======================

First line of the headers are human-readable column headers
(required). Following lines define additional information about each
column. Required is `types`, which says how the data ought to be
interpreted. Currently defined types are:

* `ISO8601-date` -- Date as `2014-12-30`
* `ISO8601-datetime` -- Date and time as `2014-12-30T11:59:00.01`
* `bool -- Boolean. `true` or `false`
* `float` -- Floating point number, either containing a space or otherwise
* `int` -- Integer
* `str` -- JSON-encoded string (quotes omitted)

As a fallback, we strongly recommend a json section. All columns
shouldbe defined as one of three JSON types:

* `Boolean` -- `true` or `false`
* `Number` -- Integer or floating point
* `String` -- Most other data types fall into this category

If this is missing, parsers should treat unrecognized types as strings.

`variables` is also strongly recommended. `variables` gives useful
variable names to assign in a program. These should be letters,
numbers, and underscores, but may not begin with a number. This is
convenient for automatic parsers and parser generators.

In addition, there may be headers for other metadata, such as units,
or vendor extensions.  

Vendor Extensions
=================

Vendors may add arbitray extensions to both metadata and headers. The
keys should begin with a program name and a dash. For example, `mysql`
could add rows called `mysql-types` and `mysql-keys` to the headers,
which would allow imports/exports to maintain both type informations,
and which columns are unique. `mysql` could also place global column
metadata (such as multi-column constraints or storage engine) in the
file-wide metadata with keys such as `mysql-constraints` and
`mysql-engine`, or just in its own YAML section. 

Such extensions should pay close attention to human readability.

Getting started
===============

This is a before-and-after example of the same code, with a TSV file
in Python, versus with a tsvx file and the library:

After:

    for line in tsvx.reader(open("file.tsvx"))
       do_some_stuff(line.foodname,
                     line.weight,
                     line.price,
                     line.expiration)

Before:

    f = open("file.tsv")
    # Skip headers
    f.next()
    # Break on tabs
    split_lines = (l[:-1].split('\t') for l in f)
    # Parse to types
    parsed_lines = (
       [l[0], int(l[1]), float(l[2]), dateutil.parser.parse(l[3])]
       for l in split_lines
    )

    for foodname, weight, price, expiration in parsed_lines:
       do_some_stuff(foodname, weight, price, expiration)

There is a also a small file in the repo, `example/example.py`, which
shows how the prototype reference library works. Note that both the
API and file format are still mutable -- we are actively soliciting
feedback.

A More Complex File
====================

And a more complex example, to show how extension fit in:

    title: Food inventory
    description: A sample tsvx file
    created-date: 2016-10-29T15:25:29.449640
    generator: myoffice.py
    myoffice-version: 2.7
    ---------------------
    Food Name   Weight     Price       Expiration Date
    foodname    weight     price       expiration      (variables)
    str         int        float       ISO8601-date    (types)
                kg         dollars/kg                  (units)
    String      Number     Number      String          (json)
    VARCHAR(80) SMALLINT   DOUBLE      VARCHAR(20)     (mysql-types)
    primary                                            (mysql-keys)
    inventory   shipweight gross       exp             (myoffice-schema)
    %s          %i         %.2f        YYYY-MM-DD      (myoffice-format-strings)
    ---------------------
    Tuna        300        5.13        2017-10-12
    Salmon      150        7.18        2018-10-24
    Swordfish   250        9.41        2016-11-13