#!/usr/local/bin/python3
"""
allman.py

Quick and dirty converter to Allman style that probably doesn't take care of
corner cases very nicely.

Idea: grab the opening white space (to get the proper indentation level --
hopefully it's just spaces, but Emacs untabify can take care of that), find the
curly brace at the end, delete any whitespace before the curly brace, and print
the new line with the opening whitespace + the opening curly brace.
"""

import re
import sys
import os

# p = re.compile(r"^(?P<ws>foo)(?P<body>bar)$")
# test = "foobar"

p = re.compile(r"^(?P<ws>\s*)(?P<body>.+)\s+\{$")
test = "    h2 {"

## cool, the test works
# if p.match(test) is not None:
#     m = p.match(test)
#     print("openining whitespace: '" + m.group("ws") + "'")
#     print("body: '" + m.group("body") + "'")
#     print("next line: '" +  m.group("ws") + "{'")
# else:
#     print("no match")

if len(sys.argv) > 1:
    fname = sys.argv[1]
else:
    while True:
        fname = input("Enter filename to process: ")
        if fname:
            break

fname = os.path.expanduser(fname)

lines = []

with open(fname) as f:
    # don't call readlines -- just iterate over file instead
    # see: http://stupidpythonideas.blogspot.com/2013/06/readlines-considered-silly.html
    for line in f:
        m = p.match(line)
        if m is not None:
            lines.append(m.group("ws") + m.group("body") + "\n")
            lines.append(m.group("ws") + "{\n")
        else:
            lines.append(line)

# grab the filename without the extension + the extension
out_dir = os.path.dirname(fname)
out_fname, ext = os.path.splitext(os.path.basename(fname))
out_fname += "-allman" + ext

with open(os.path.join(out_dir, out_fname), "w") as out:
    for line in lines:
        out.write(line)

print(out_fname + " successfully written to ." + out_dir)
