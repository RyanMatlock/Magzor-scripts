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
import shutil
import zipfile

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
OSH_PARK_EXT = ["GBL", # bottom layer
                "GBO", # bottom silkscreen
                "GBS", # bottom soldermask
                "GKO", # dimension
                "GTL", # top layer
                "GTO", # top silkscreen
                "GTS", # top soldermask
                "XLN", # Excellon drill file
                ]

STENCIL_EXT = ["TCRM", # top cream layer
               "BCRM", # bottom cream layer
               ]
MISC_CAM_EXT = ["dri", # drill file verification
                "gpi", # Gerber file verification?
                ]
CAM_EXT = OSH_PARK_EXT + STENCIL_EXT + MISC_CAM_EXT
CAM_EXT.sort()

def has_ext(fname, ext):
    """
    better implementation than endswith() because I can pass in regexs for ext
    """
    p = re.compile(".*\.{ext}$".format(ext=ext))

    if p.match(fname) is not None:
        return True
    return False

# this doesn't seem to be working for some reason -- investigate later
# print("locals before:")
# print(locals())
# def is_type_generator(name, extension_list):
#     exec("""def is_{name}(fname):
#     for ext in {extension_list}:
#         if has_ext(fname, ext):
#             return True
#     return False""".format(name=name, extension_list=extension_list))

# # this is maybe slightly gross because I need to pass the test_str of the (list)
# # object instead of the object itself
# is_type_generator("cruft", "CRUFT_EXT")
# is_type_generator("cam", "CAM_EXT")
# print()
# print("locals after:")
# print(locals())
# print()

# def is_cruft(fname):
#     for ext in CRUFT_EXT:
#         if has_ext(fname, ext):
#             return True
#     return False

# def delete_cruft(fname):
#     if is_cruft(fname):
#         os.remove(fname)
#         return
#     else:
#         return

# # not very DRY
# def is_cam(fname):
#     for ext in CAM_EXT:
#         if has_ext(fname, ext):
#             return True
#     return False

def has_ext_in_list(fname, ext_list):
    for ext in ext_list:
        if has_ext(fname, ext):
            return True
    return False

# these next few aren't great, but it's better
def is_cruft(fname):
    return has_ext_in_list(fname, CRUFT_EXT)

def is_cam(fname):
    return has_ext_in_list(fname, CAM_EXT)

def is_stencil(fname):
    return has_ext_in_list(fname, STENCIL_EXT)

def is_in_osh_zip(fname):
    return has_ext_in_list(fname, OSH_PARK_EXT)

def delete_cruft(fname):
    if is_cruft(fname):
        os.remove(fname)
        return
    else:
        return


# some_cruft = "bar.s#1"
# some_cam = "foo.TCRM"

# def check_has_ext(test_str, ext):
#     print("{}: {}".format(test_str, has_ext(test_str, ext)))

# check_has_ext(some_cruft, CRUFT_EXT[0])
# check_has_ext(some_cam, "TCRM")
# ugh, just spent too long tracking down a stupid bug.  .format(ext=ext) is what
# I should have written, but what I had was .format(ext) in my definitin of
# has_ext()

while True:
    root_dir = input("Enter root directory of your EAGLE project\n(if left "
                     "blank, {cwd} will be used):\n".format(cwd=os.getcwd()))

    if not root_dir:
        root_dir = os.getcwd()
    elif root_dir.upper() == "Q":
        exit()
    else:
        # os.path.expanduser(<path>) will expand tildes in <path>
        root_dir = os.path.expanduser(root_dir)

    if os.path.isdir(root_dir):
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

BASE_CAM_DIR = "CAM"
BASE_STENCIL_DIR = "Stencil"
BASE_OSH_PARK_DIR = "OSH-Park"

CAM_DIR = os.path.join(root_dir, BASE_CAM_DIR)
STENCIL_DIR = os.path.join(CAM_DIR, BASE_STENCIL_DIR)
OSH_PARK_DIR = os.path.join(CAM_DIR, BASE_OSH_PARK_DIR)

if not os.path.isdir(CAM_DIR):
    os.makedirs(STENCIL_DIR)
    os.makedirs(OSH_PARK_DIR)
    print("./CAM directories successfully created.")
elif not os.path.isdir(STENCIL_DIR):            
    os.makedirs(STENCIL_DIR)
    print("./CAM/Stencil directory successfully created.")
elif not os.path.isdir(OSH_PARK_DIR):
    os.makedirs(OSH_PARK_DIR)
    print("./CAM/OSH-Park directory successfully created.")
else:
    print("./CAM + subdirectories  already exist, and that's ok!")


base_name = os.path.basename(root_dir)
zf_name = base_name + ".zip"

while True:
    if os.path.isfile(os.path.join(OSH_PARK_DIR, zf_name)):
        response = input("Target zipfile already exists. Delete (Y) or quit "
                         "(Q)? ")
        if response.upper() == "Y":
            os.remove(os.path.join(OSH_PARK_DIR, zf_name))
            break
        elif response.upper() == "Q":
            exit()
    else:
        break
    
zf = zipfile.ZipFile(zf_name, "w")
            
naming_convention_mismatch = []
for element in os.listdir(root_dir):
    if element[0] not in IGNORE_PREFIXES:
        # if os.path.isdir(element):
        #     element += "\n  ^(is a directory)"
        # print(element)
        if not os.path.isdir(element):
            delete_cruft(element)
            if name_p.match(element) is None:
                naming_convention_mismatch.append(element)
            if is_in_osh_zip(element):
                zf.write(element)
                shutil.move(os.path.join(root_dir, element), OSH_PARK_DIR)
            elif is_stencil(element):
                shutil.move(os.path.join(root_dir, element), STENCIL_DIR)
            elif is_cam(element):
                shutil.move(os.path.join(root_dir, element), CAM_DIR)
            else:
                pass

zf.close()
shutil.move(os.path.join(root_dir, zf_name), OSH_PARK_DIR)
print("OSH Park-ready zip file successfully written.")

print("The following files did not comply with the naming convention:\n"
      "(if you want to know more, ask Tom or Matlock)")
for entry in naming_convention_mismatch:
    print("  " + entry)

print("Program successfully terminated.")
