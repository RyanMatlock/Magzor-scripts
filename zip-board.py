#!/usr/local/bin/python3
"""
zip-board.py

Point it at an EAGLE project folder on which you've just run the CAM processor*,
and zip-board.py will take care of generating the ./CAM folder, putting the
Gerber/Excellon files into there, and zipping them up.  It also makes sure
everything is named properly.

* magzor.cam

Ryan Matlock
2014-07-01
"""

import re
import os

# matches pattern "ME-XXXXX-XL" where X is a number and L is a letter
name_p = re.compile("ME-(\d){5,}-\d+[A-Z]+")

# if name_p.match("ME-00001-1A") is not None and\
#   name_p.match("ME-0000X-1C") is None:
#     print("yippee!")
# else:
#     print("ohno!")

# ignorable file prefixes
IGNORE_PREFIXES = [".",
                 "#",]
    
# delete files with these extensions -- you don't need them
CRUFT_EXT = ["s#\d", # schematic auto save files
              "b#\d", # board auto save files
              ]

# Gerber/Excellon file extensions for OSH Park and stencil making
CAM_EXT = ["GBL", # bottom layer
           "GBO", # bottom silkscreen
           "GBS", # bottom soldermask
           "GKO", # dimension
           "GTL", # top layer
           "GTO", # top silkscreen
           "GTS", # top soldermask
           "XLN", # Excellon drill file
           "TCRM", # top cream layer
           "BCRM", # bottom cream layer
           ]

def has_ext(fname, ext):
    """
    better implementation than endswith() because I can pass in regexs for ext
    """
    p = re.compile(".*\.{ext}$".format(ext))
    m = p.match(fname)

    if m is not None:
        return True
    return False

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

# not very DRY
def is_cam(fname):
    for ext in CAM_EXT:
        if has_ext(fname, ext):
            return True
    return False

while True:
    root_dir = input("Enter root directory of your EAGLE project\n(if left "
                     "blank, {cwd} will be used)\n\t: ".format(cwd=os.getcwd()))

    if not root_dir:
        root_dir = os.getcwd()
    elif root_dir.upper() == "Q":
        exit()
    else:
        # os.path.expanduser(<path>) will expand tildes in <path>
        root_dir = os.path.expanduser(root_dir)

    if os.path.isdir(root_dir):
        print(root_dir)
        if name_p.match(os.path.basename(root_dir)) is not None:
            break
        else:
            while True:
                response = input("{root_dir} does not following naming "
                                 "convention (ask Tom or Matlock if you're "
                                 "unsure).\nDo you wish to proceed "
                                 "(Y) or quit (Q)? ".format(root_dir=\
                           os.path.basename(root_dir)))
                if response.upper() == "Y":
                    break
                elif response.upper() == "Q":
                    exit()
            break
    else:
        print("{root_dir} is an invalid directory. Please try again or "
              "press \"Q\" to quit.".format(root_dir=root_dir))

for element in os.listdir(root_dir):
    if element[0] not in IGNORE_PREFIXES:
        # if os.path.isdir(element):
        #     element += "\n  ^(is a directory)"
        # print(element)
        if not os.path.isdir(element):
            if name_p.match(element) is None:
                print("{element} does not match naming convention (ask Tom or "
                      "Matlock if you're unsure)".format(element=element))
            if is_cruft(element):
                print("{element} will be deleted".format(element=element))
            for ext in CAM_EXT:
                if has_ext(element):
                    print("{element} will be moved to ./CAM".format(element=element))
            
