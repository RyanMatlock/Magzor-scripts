#!/usr/bin/python3
"""
cpp-allman.py

Crude attempt at enforcing Allman style (braces in line with function
definitions, loops, conditionals, etc. and a default indentation of 4 spaces
(converting all instances of <TAB> to 4 spaces--we'll see about enforcing the
4 space default later).
"""

import os
import sys

"""
Actually, I don't know if I really like what you're doing here.  Instead, I
think you ought to use sys.argv so then you can maybe do all .cpp and .h files
at once.  That would be way cooler, and then we could apply this script
efficiently.
"""

"""
print("Enter C++ file:", end=" ")

cpp_file = input()

cpp_abs_path = os.path.abspath(cpp_file)

cpp_path, cpp_filename = os.path.split(cpp_abs_path)
"""

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

cpp_abs_path = os.path.abspath(cpp_file)
cpp_path, cpp_filename = os.path.split(cpp_abs_path)

"""
print(sys.argv[1])
print(cpp_abs_path)
print(cpp_path)
print(cpp_filename)
"""

