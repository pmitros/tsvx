# Related Formats

W3C Recommendation: Model for Tabular Data and Metadata on the Web
==================================================================

The W3C formed the **CSV on the Web Working Group**. This group issued
a recommendation to [standardize
metadata](https://www.w3.org/TR/2015/REC-tabular-data-model-20151217/)
about CSV/TSV files for use on the web. The W3C recommendation is
descriptive, not prescriptive. It does not specify how TSV/CSV files
themselves ought to be formatted, but rather has a standard for
describing what is inside of such files. This is a complementary
effort to tsvx -- the W3C language could be used to describe the data
inside of a tsvx file if such a file were to be used externally in a
way which was compatible with linked data and the semantic web.

To understand the core difference, having the W3C recommended metadata
about a tabular file is **very** helpful if you are building a web
spider which wants to understand and index existing tabular data on
the web. It is helpful to add if you want to publish a dataset for
public consumption. It does not solve the problems encountered in
internal day-to-day analytics or data flows. Indeed, if all internal,
intermediate tabular files were required to have such metadata, the
process of doing analytics would be much more cumbersome.

To see the difference, consider that free-form tabular files+W3C
metadata:

* Can use any delimiter (comma, tab, etc.)
* Can use any format. The metadata specifies what it is
* Can use any string escaping
* Such files can even use formats like HTML tables and Excel
* Etc.

tsvx standardizes all of this. This has several advantages for
analytics and application compatibility:

* **Engineering Speed** A tsvx parser can be written in a
  weekend. Writing a parser which can handle the full span of CSV+W3C
  metadata files is a massive effort. tsvx files may be processed with
  traditional command line tools, such as `cut`.
* **Parse Speed** The complexity of free-form CSVs limits performance
  in analytics pipelines. example, in tsvx, columns are always split
  by tabs. Splitting into columns is fast. In CSV+W3C metadata, you
  may have columns split by commas, but also commas inside of string
  columns enclosed in quotes. String columns themselves may have
  escaped quotes. This requires a more complex parser.
* **Human-readability** If you `cat` a tsvx file in a terminal, with
  tabs set appropriately, the rendering is very pretty. It's easy to
  edit and work with. Columns line up. The JSON metadata in the W3C
  recommendation is quite cumbersome to work with non-programmatically.
* **Workflow** With tsvx, there are individual, self-contained
  files. The W3C recommendation lives outside of the tabular data
  file. Something like an export from Google Docs would require two
  files. Even generating the W3C metadata is a manually intensive
  process. tsvx metadata may be generated automatically, or with
  minimal manual overhead (2-3 lines of code).

W3C metadata is helpful for major projects which publish data
externally. tsvx is designed as a lightweight standard to allow basic
interoperability when processing data, especially in internal
settings. We have Python scripts which process edX data which we rerun
regularly. On import into a spreadsheet, we have a big chunk of manual
work, from selecting options in the importer, to manually reformatting
columns. We have pipelines composed of dozens of scripts, with
intermediate TSV files between each pair of steps, where a change in
one script can break downstream scripts. The overhead of the W3C
recommendation is much greater than the benefit when scripts are
dozens of lines each.

JSON-seq
========

[JSON-seq](https://tools.ietf.org/html/rfc7464) is a nice format, and
indeed, how we store out event logs. It has a number of issues in a BI
pipeline. The ones which disqualify it are:

* Parse speed for large files (several times slower than tsvx)
* Spreadsheet compatibility (for small files)
* You don't know what's coming

IETF CSV
========

The IETF has [standardized CSV
files](https://tools.ietf.org/html/rfc4180).  This is a nice standard
as well. It is a standard for unstructured CSV files. We're precisely
trying to add structure to allow strong typing and rapid stream
processing.

Tabular Data Package/SDF
========================

There is a [very nice little
spec](http://specs.frictionlessdata.io/tabular-data-package/) for
tabular data as part of a larger spec for data packages. This is
actually closest to what we're looking for. It still requires split
files (one CSV, and one description file), which makes sense in that
context -- a data package is a large collection of files -- but not in
isolation. It's also not broadly adopted/supported. It also has a
[CSV dialect description
format](http://specs.frictionlessdata.io/csv-dialect/), which is
precisely what we're trying to standardize.