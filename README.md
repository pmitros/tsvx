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

* We standardize string escaping. We use JSON-style escaping.
* We standardize column types to be JSON variables. We support
  more data types encoded as such
* We standardize on headers which can provide column names and type
  metadata. Columns may have types, units, program-specific metadata,
  and otherwise.

This is repository includes (at the time of this writing, the start
of) a parser for such tab-separated files, so we can experiment with
this concept.

Status
======

This is intended as a **request for comments**. We have early
prototype functionality, but we'd like to see what communities think
about this before building this out further. We will have a
request-for-comments period, which we will probably close off late
2016 or early 2017.

Example
=======

A basic example:

    title: Food inventory
    created-date: 2016-10-29T15:25:29.449640
    ---------------------
    Food Name   Weight   Price       Expiration Date
    str         int      float       ISO8601-date    (types)
    String      Number   Number      String          (json)
    ---------------------
    Tuna        300      5.13        2017-10-12
    Salmon      150      7.18        2018-10-12
    Swordfish   250      9.41        2016-11-13

And a more complex example:

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
    inventory   shipweight gross       exp             (myoffice-schema)
    %s          %i         %.2f        YYYY-MM-DD      (myoffice-format-strings)
    ---------------------
    Tuna        300        5.13        2017-10-12
    Salmon      150        7.18        2018-10-24
    Swordfish   250        9.41        2016-11-13

File Structure
==============

The file has three sections:

* **File metadata** (optional) -- Information about the file itself
* **Column headings** (required) -- Metadata about the names and types
  in the columns
* **Data** (required) -- What one might traditionally find in a TSV
  file.

Sections are seperated by a line of all dashes, containing at least
three dashes.

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

First line of the headers are human-readable column headers. Following
lines define additional information about each column. Required are
`types` and `json`, which say how the data ought to be
interpreted. `json` is a fallback in case the application cannot
interpret a given type. Currently defined types are:

* `ISO8601-date` -- Date as `2014-12-30`
* `ISO8601-datetime` -- Date and time as `2014-12-30T11:59:00.01`
* `bool -- Boolean. `true` or `false`
* `float` -- Floating point number, either containing a space or otherwise
* `int` -- Integer
* `str` -- JSON-encoded string (quotes omitted)

As a fallback, all lines should also be defined as one of three JSON types:

* `Boolean` -- `true` or `false`
* `Number` -- Integer or floating point
* `String` -- Most other data types fall into this category

If this is missing, parsers should treat unrecognized types as strings.

In addition, there may be headers for:

* `variables` gives useful variable names to assign in a program. These
  should be letters, numbers, and underscores, but may not begin with
  a number. This is convenient for automatic parsers and parser
  generators. This is strongly recommended.
* Metadata for specific programs. These should begin with a program
  name and a dash, as in `mysql-types`.
* Units.

Design goals
============

* Human-readability
* Compatibility between apps. It should be possible to go between
  Excel, Google Docs, Hadoop, LibreOffice, MySQL, PostgreSQL, Python,
  R, Vertica, and others without extensive scripting. This doesn't
  need to be optimal (e.g. a fixed-sized string field might go to a
  variable-sized string), but it should be workable.
* Spreadsheet compatibility (so file will open reasonably in a
  spreadsheet not aware of tsvx)
* Fast, single-pass streaming processing (I can reasonably work with
  tsvx files up to a few gigabytes, and I don't want to lose that)
* Extensibility. Programs should be able to include enough metadata
  for meaningful import/export
* Enough metadata that, a year later, an analyst looking at a file can
  tell what's in that file, where it came from, and hopefully how to
  regenerate it with current data

Getting started
===============

There is a small file, `example/example.py`, which shows how the
prototype reference library works. Note that both the API and file
format are still mutable -- we are actively soliciting feedback.

Why?
====

I work for a small ed-tech not-for-profit. In that role, We look at
lots of data. As it turns out, there isn't a clear small data/big data
split. We have educational researchers at universities, big data
pipeline, business intelligence analysts, and all sorts of other folks
all generating and working with data with different tools. Those often
need to be combined. Even within one pipeline, data gets successively
smaller. In my normal workflow, We'll usually start with terabytes of
data, and end up with a graph. That usually starts with Hadoop which
take TB down to GB, goes into Python scripts which take GB down to
thousands or hundreds of lines, and the final steps are sometimes done
in a spreadsheet. We often need to do `JOIN`s on such data -- for
example, we have hand-curated lists (in spreadsheets) of metadata on
courses, which we'd like to use in our big data pipelines.

Each time we do this, we rewrite similar code, essentially casting
strings of integers to integers, or parsing dates. Reuse of data files
is also limited since looking at such files, it's not always clear
what's in them, or how they were made. We do have documentation
out-of-band (README files and similar), but looking through dozens of
directories, in practice, that makes it several times slower to find
an intermediate result from some analytics pipeline.

Talking to people, I don't think we're alone. I'm tossing this up to
get people's thoughts. The code and proposal are rough, but I thought
I'd toss them up to solicit comments and discussion. Once we decide if
this is a good way to do this, I'll make this more production-ready,
and perhaps draft an IETF RFC or similar standard.