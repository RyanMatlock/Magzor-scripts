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

print("Enter C++ file:", end=" ")

cpp_file = input()

cpp_abs_path = os.path.abspath(cpp_file)

cpp_path, cpp_file_name = os.path.split(cpp_abs_path)

def test_path_operations():
    
