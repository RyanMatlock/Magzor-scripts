"""
rename-electrical.py

Makes file names and folders compliant with naming convention.

How it works:
1) point it at the root directory of your folders
2) it will recursively search through the folders, looking for files ending in
   BASE_EXT
3) upon encountering said files:
   a) the parent directory is renamed if not
	  compliant
4) the files are renamed if not compliant, a ./CAM directory is

* Implementation [0/3]
The script runs in the following manner:
1) [ ] point the program at the root directory of your folders
2) [ ] it recursively searches through the files ending in BASE_EXT
3) [ ] [0/3] when it finds a folder containing a file in BASE_EXT, it
   1. [ ] attempts to determine the project base name either through parsing
      the file/folder name (or through reading a .NAM(e)CON(vention) file?)
   2. [ ] renames files appropriately
   3. [ ] if not present, a .

Ryan Matlock
2014-06-26
"""

import sys
import os
import re

# delete files with these extensions -- you don't need them
CRUFT_EXT = ["s#\d", # schematic auto save files
              "b#\d", # board auto save files
              ]

# Gerber/Excellon file extensions for OSH Park
FAB_EXT = ["GBL", # bottom layer
           "GBO", # bottom silkscreen
           "GBS", # bottom soldermask
           "GKO", # dimension
           "GTL", # top layer
           "GTO", # top silkscreen
           "GTS", # top soldermask
           "XLN", # Excellon drill file
           ]

# probably just the cream layer
MISC_GERBER_EXT = ["CREAM",]

# encountering either of these extension causes the program to treat this as a
# base directory
BASE_EXT = ["sch", # EAGLE schematic
            "brd", # EAGLE board
            ]

MISC_CAM_EXT =  ["ZIP",] # contains Gerber/Execellon files for OSH Park

CAM_DIR = "CAM"

# if not os.path.isdir(directory):
#     os.makedirs(directory)

def has_ext(fname, ext):
    """
    better implementation than endswith() because I can pass in regexs for ext
    """
    p = re.compile(".*\.{ext}$".format(ext))
    m = p.match(fname)

    if m is not None:
        return True
    return False

# def contains_base_ext(fnames):
#     patterns = [re.compile(".*\.{}$".format(ext)) for ext in BASE_EXT]

#     matches = [[pattern.match(fname) for pattern in patterns]
#                 for fname in fnames]

#     for match_set in matches:
#         for match in match_set:
#             if match is not None:
#                 return True
#     return False

# going to refactor contains_base_ext() on account of has_ext
def contains_base_ext(fnames):
    

def is_cruft(fname):
    for ext in CRUFT_EXT:
        if has_ext(fname, ext):
            return True
    return False

def delete_cruft(fname):
    if is_cruft(fname):
        os.remove(fname)
        return
    else:
        return

def test_contains_base_ext():
    fnames = ["foo.bar",
              "bar.baz"]
    fnames2 = ["foo.bling",
               "bar.sch"]

    print(contains_base_ext(fnames))
    print(contains_base_ext(fnames2))

while True:
    root_dir = input("Enter root directory\n(if left blank, {cwd} will be "
                     "used)\n\t: ".format(cwd=os.getcwd()))

    if not root_dir:
        root_dir = os.getcwd()
    elif root_dir.upper() == "Q":
        exit()
    else:
        # os.path.expanduser(<path>) will expand tildes in <path>
        root_dir = os.path.expanduser(root_dir)

        if os.path.isdir(root_dir):
            print(root_dir)
            break
        else:
            print("{root_dir} is an invalid directory. Please try again or "
                  "press \"Q\" to quit.".format(root_dir=root_dir))

os.walk(root_dir)


# if __name__ == "__main__":
    # test_contains_base_ext()
