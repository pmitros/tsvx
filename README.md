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

Example file:

    title: Food inventory
    subtitle: A sample TSVx file
    ---------------------
    Food Name	Weight	Price	Expiration Date
    types:	str	int	float	str
    units:	None	kg	dollars/kg	ISO8601-date
    mysql-type:	VARCHAR(80)	SMALLINT	DOUBLE
    libreoffice-type:	string	%i	%.2f	datetime
    ---------------------
    Tuna	300	5.13	2017-10-12
    Salmon	150	7.13	2018-10-12

The file has three sections:

* Metadata (optional)
* Headers (required)
* Data (required)

Sections are seperated by a line of all dashes, containing at least
three dashes.

The metadata is a YAML dictionary. The first line must contain a
colon. Fields defined are:

* title
* description
* authors
* created-date
* modified-date