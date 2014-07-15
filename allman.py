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
