#!/usr/local/bin/python3
"""
cpp-allman.py

Crude attempt at enforcing Allman style (braces in line with function
definitions, loops, conditionals, etc. and a default indentation of 4 spaces
(converting all instances of <TAB> to 4 spaces--we'll see about enforcing the
4 space default later).
"""

import os
import sys
import re

"""
Actually, I don't know if I really like what you're doing here.  Instead, I
think you ought to use sys.argv so then you can maybe do all .cpp and .h files
at once.  That would be way cooler, and then we could apply this script
efficiently.
"""


# print("Enter C++ file:", end=" ")
# cpp_file = input()
# cpp_abs_path = os.path.abspath(cpp_file)
# cpp_path, cpp_filename = os.path.split(cpp_abs_path)


def test_command_line_operations():
    pass

def test_path_operations():
    test_path = "/foo/bar"
    test_filename = "baz.cpp"
    path_and_filename = os.path.join(test_path, test_filename)
    cpp_path, cpp_filename = os.path.split(path_and_filename)

    assert test_path == cpp_path
    assert test_filename == cpp_filename



if len(sys.argv) != 2:
    print ("Program not that advanced yet.  Sorry!")

cpp_file = sys.argv[1]

while True:
    cpp_abs_path = os.path.abspath(cpp_file)
    cpp_path, cpp_filename = os.path.split(cpp_abs_path)
    try:
        assert(len(cpp_filename.split(".")) == 2)
        break
    except AssertionError:
        print(("=" * 30) +
              "\n"
              "Your filename is dumb.  "
              "It should only have one period, period."
              "\n\n"
              "I'm giving you an opportunity to try again."
              "\n"
              "Enter cpp file:", end=" ")
        cpp_file = input()

cpp_filename, cpp_ext = cpp_filename.split(".")





# print(sys.argv[1])
# print(cpp_abs_path)
# print(cpp_path)
# print(cpp_filename)


TAB_REPLACEMENT = " " * 4

# states for line parser
INDENT = "INDENT"
CODE = "CODE"


## opening braces and closing braces should be on their own lines
# captures opening brace and any subsequent comments
# also, you need to consider that there might be spaces within <code>, because
# I think the dot doesn't gobble spaces
# apparently you can split regexes across multiple lines like this:
opening_brace = re.compile(
    (r"^(\s+)?(?P<code>((.+(\s+)?)+)?)" # everything before the brace
     "(?P<brace_etc>\{.*\s*)$" # brace, spaces, comments, etc.
    ))

## let's see how quickly pytest runs without this test
def test_opening_brace_regex():
    # this test suite was a bit contrived -- actual examples are now included
    tests = ["{\n",
             "\t\tint func(std::I2Cdriver int &x, bool status) { // comment",
             (" " * 4) + "for(int i = 0; i++; i < limit) {\n",
             ## end of contrived examples ##
             "I2C_Adapter_RPI::I2C_Adapter_RPI(){",
             "	for (int i = 0; i < 128; i++) {",
             "I2C_Adapter_RPI* I2C_Adapter_RPI::getInstance(){ ",
             "foo"]

    """
    test_matches = [opening_brace.match(test) for test in tests]

    for i in range(len(test_matches)):
        print("{}: {!r}".format(i,tests[i]))
        assert test_matches[i] is not None
    """
    failures = [test for test in tests if not opening_brace.match(test)]
    assert len(failures) == 0, failures


def main():
    with open(cpp_abs_path) as cpp:
        with open(os.path.join(cpp_path, cpp_filename + "-allman" + "." +
                               cpp_ext),"w") as new_cpp:
            line_no = 0
            for line in cpp:
                #print("line {}: {!r}".format(line_no, line))
                line_no += 1
                indentation_level = 0
                state = INDENT
                for element in line:
                    if state == INDENT and element == "\t":
                        indentation_level += 1
                    else:
                        state = CODE
                new_line = TAB_REPLACEMENT * indentation_level


                opening_brace_match = opening_brace.match(line)
                if opening_brace_match is not None:
                    new_line += opening_brace_match.group("code")
                    # next lines just add the brace and technically create two
                    # lines
                    new_line += "\n"
                    print("line {}: {!r}".format(line_no, new_line))
                    #print("{!r}".format(new_line))
                    new_line += TAB_REPLACEMENT * indentation_level
                    new_line += opening_brace_match.group("brace_etc")
                    new_line += "\n"
                    print("line {}: {!r}".format(line_no, new_line))
                    #print("{!r}".format(new_line))
                else:
                    new_line += line[indentation_level:]


                #new_line += line[indentation_level:]

                new_cpp.write(new_line)
    cpp.close()
    new_cpp.close()

if __name__ == "__main__":
    main()
