"""This is a simple utility to convert a TSV file to TSVx format. We
really would prefer a complex utility, which can do everything
automagically, but for now, simple will do.

Usage: 
  tsv2tsvx <input> <output>
  tsv2tsvx -h | --help

Options:
  -h --help        Show this screen.

TODO: 
  [--title=<title>] [--types=<types>]  [--vars=<vars>]
  --title=<title>  Add a title to the file
  --types=<types>  A comma-seperated list of types for the columns
  --vars=<vars>    A comma-seperated list of variable names
"""

import docopt
import os
import os.path
import sys

import tsvx

import tsvx.helpers

arguments = docopt.docopt(__doc__)

inputfile = arguments["<input>"]
outputfile = arguments["<output>"]

if os.path.exists(outputfile):
    print "Error: Output file already exists. Please erase it first."
    sys.exit(-1)

if not os.path.exists(inputfile):
    print "Error: Input file doesn't exist."
    sys.exit(-1)

ifp = open(inputfile, "r")
ofp = open(outputfile, "w")

(headers, ifp) = tsvx.helpers.peek(ifp, 2)

ofp.close()
