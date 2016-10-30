# TSVx: Enhanced TSV Format

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

* We standardize escaping. We use JSON-style escaping.
* We standardize column types to be JSON variables. We support
  more types encoded as such
* We standardize on headers which can provide column names and type
  metadata. Columns may have types, units, and similar

This is repository includes (at the time of this writing, the start
of) a parser for such tab-separated files. 

Status
======

This is intended as a **request for comments**. We have early
prototype functionality, but we'd like to see what communities think
about this before building this out further.

Example
=======

Example file:

    title: Food inventory
    description: A sample TSVx file
    created-date: '2016-10-29T15:25:29.449640'
    generator: test.py
    ---------------------
    Food Name   Weight   Price       Expiration Date
    foodname    weight   price       expiration      (variables)
    str         int      float       ISO8601-date    (types)
    null        kg       dollars/kg  null            (units)
    String      Number   Number      String          (json)
    VARCHAR(80) SMALLINT DOUBLE      VARCHAR(20)     (mysql-types)
    ---------------------
    Tuna        300      5.13        2017-10-12
    Salmon      150      7.18        2018-10-12
    Swordfish   250      9.41        2016-11-13

Structure
=========

The file has three sections:

* Metadata (optional)
* Headers (required)
* Data (required)

Sections are seperated by a line of all dashes, containing at least
three dashes.

Metadata
========

The metadata is a YAML dictionary. The first line must contain a
colon. Fields defined are:

* `title` -- A single line title/description
* `description` -- A multiline description
* `authors` -- JSON list of authors
* `created-date` -- ISO8601 date and time of when the file was created
* `modified-date` -- ISO8601 date and time of last modification
* `generator` -- Some identifier of the program or source the data came
  from

Headers
=======

First line of the headers are human-readable column headers. Following
lines define additional information about each column. Required are
types and json-types, which say how the data ought to be
interpreted. Currently defined types are:

* `int` -- Integer
* `float` -- Floating point number, either containing a space or otherwise
* `bool -- Boolean. `true` or `false`
* `ISO8601-datetime` -- Date and time as `2014-12-30T11:59:00.01`
* `ISO8601-date` -- Date as `2014-12-30`
* `str` -- JSON-encoded string (quotes omitted)

As a fallback, all lines should also be defined as one of three JSON types:

* `String` -- Most other data types fall into this category
* `Number` -- Integer or floating point
* `Boolean` -- `true` or `false`

In addition, there may be headers for

* Variable names. These should be letters, numbers, and underscores,
  but may not begin with a number. This is convenient for automatic
  parsers.
* Types for specific programs. For example, a MySQL export should be
  importable without losing the field size for strings, and a
  spreadsheet export should be able to keep formatting on re-import.
* Units. 