"""
eagle_bom_reader.py

Just checking to see how easy it is to read a BOM generated by EAGLE CAD's
bom.ulp.
"""

import os
import csv
import logging
import re
import copy
from operator import itemgetter
# import sys
from tabulate import tabulate

# import shlex  # for escaping spaces?

logging.basicConfig(level=logging.INFO)

csv.register_dialect("eagle",
                     delimiter=";",
                     quoting=csv.QUOTE_ALL)

IGNORE_DEVICE_FRAGMENTS = [
    "MOUNT-HOLE",
    "STENCIL-HOLES+GRID",
    "MAGZOR-MOLECULE-LOGO",
    "HOLE-ALIGNMENT",
    ]

# targets.txt file looks like this:
#   DESIGNS=~/gDrive/Magzor Technical/CAD/Electrical/Designs
#   # board, qty
#   ME-00002-1G, 2
#   ME-00024-1C, 1
#   ME-00023-1C, 6
# so figure out how to parse that into folders/files
BOM_EXT = "-BOM.csv"

board_name_pattern = re.compile("^(?P<num>ME-\d{5,}-\d+)(?P<rev>[A-Z]+)$")

with open("targets.txt") as targets:
    bom_files = []  # list of tuples of full file name, quantity
    for line in targets:
        try:
            if line[0] == "#":
                pass
            else:
                if len(line.split('=')) == 2:
                    # make sure you remove that trailing newline char!!!
                    head, designs_folder = [elem.strip() for elem in
                                            line.split('=')]
                    if head != "DESIGNS":
                        logging.warning("Someone's using an improperly "
                                        "formatted targets.txt file.")
                    # using os.path.expandvars here, too, might be useful in
                    # the future if people start doing really tricky things,
                    # but it's probably not necessary yet
                    designs_folder = os.path.expanduser(designs_folder)
                    logging.debug("designs_folder: {}"
                                  "".format(designs_folder))
                elif len(line.split(',')) == 2:
                    # note that the stripping is not totally necessary because
                    # the int function takes care of that
                    #     >>> int(' 2\n')
                    #     2
                    # however, it's probably best to make sure fname_root
                    # doesn't have extra spaces
                    fname_root, qty = [elem.strip() for elem in
                                       line.split(',')]
                    try:
                        qty = int(qty)
                    except ValueError as e:
                        logging.error("Invalid qty '{}' ({})"
                                      "".format(qty, e))
                    m = board_name_pattern.match(fname_root)
                    if m is not None:
                        logging.debug("board: {}, rev: {}"
                                      "".format(m.group("num"),
                                                m.group("rev")))
                        # .../designs/ME-XXXXX-X
                        full_path = os.path.join(designs_folder,
                                                 m.group("num"))
                        # .../designs/ME-XXXXX-X/ME-XXXXX-XY
                        full_path = os.path.join(full_path,
                                                 fname_root)
                        # .../designs/ME-XXXXX-X/ME-XXXXX-XY/ME-XXXXX-XY
                        # (so I'm intentionally repeating myself)
                        full_path = os.path.join(full_path,
                                                 fname_root)
                        # .../designs/ME-XXXXX-X/ME-XXXXX-XY/ME-XXXXX-XY-BOM.csv
                        full_path += BOM_EXT
                        logging.debug("full board path: {}"
                                      "".format(full_path))
                        bom_files.append({"path": full_path,
                                          "qty": qty,
                                          "name": fname_root})
                    else:
                        logging.warning("fname_root '{}' didn't match naming "
                                        "convention pattern"
                                        "".format(fname_root))
                else:
                    logging.warning("Encountered unexpected line in "
                                    "targets.txt")
        except IndexError:
            logging.info("Blank line encountered while processing BOM targets")

logging.debug("bom_files: {}".format(bom_files))


def multiply_bom(bom, multiplier):
    # assume that boms act like a list of dicts and that each dict has a key
    # called "qty" whose value is of integral type
    # also, since I may want to preserve the old bom, I'm going to return a new
    # one
    if not isinstance(multiplier, int):
        multiplier_error_msg = "multiplier '{}' not integral type"\
                               "".format(multiplier)
        logging.error(multiplier_error_msg)
        raise TypeError(multiplier_error_msg)
    new_bom = copy.deepcopy(bom)
    for entry in new_bom:
        try:
            entry["qty"] *= multiplier
        except KeyError as e:
            logging.error(e)
        except TypeError as e:
            logging.error(e)
    return new_bom


MINIMAL_PART_FIELDS = set([
    "value",
    "device",
    "package",
    ])


def is_same_part(entry1, entry2):
    # assume entry1 and entry2 behave like dicts with value, device, and
    # package fields (at least)
    # do this by checking against the keys after building them in the usual
    # manner (which is actually the manner first done below in add_boms()
    #
    # also, at some point you might want to account for the fact that, say, a
    # JST 1x02 vertical PCB connector with the value "power" is the same as one
    # with the value "FSR0", yet an 0805 resistor with the value "10k" is
    # different than an 0805 resistor with the value "4k7"---that's what's
    # great about this function: you can resolve this later
    keys = set(list(entry1.keys()) + list(entry2.keys()))
    if not MINIMAL_PART_FIELDS.issubset(keys):
        minimal_key_set_error_msg = "{} and {} don't contain minimal keys "\
                                    "for comparison"\
                                    "".format(entry1, entry2)
        logging.error(minimal_key_set_error_msg)
        raise ValueError(minimal_key_set_error_msg)
    is_same = False
    logging.debug("entry1['device']: {dev1}; "
                  "entry2['device']: {dev2}; "
                  "entry1['package']: {pkg1}; "
                  "entry2['package']: {pkg2}; "
                  "entry1['value']: {val1}; "
                  "entry2['value']: {val2}"
                  "".format(dev1=entry1["device"],
                            dev2=entry2["device"],
                            pkg1=entry1["package"],
                            pkg2=entry2["package"],
                            val1=entry1["value"],
                            val2=entry2["value"]))
    if entry1["device"] == entry2["device"] and\
       entry1["package"] == entry2["package"] and\
       entry1["value"] == entry2["value"]:
        is_same = True
    return is_same


def reduce_bom(bom):
    # this searches for duplicate entries and then adds the quantities and
    # removes the duplicate (it assumes the bom is a list of dicts, each of
    # which has at the following keys: qty, value, device, package
    for i, i_entry in enumerate(bom):
        logging.debug("reduce_bom i = {}".format(i))
        # this is now O(N^2), which is dumb, but this at least works; for some
        # reason, doing something like
        #     for j, j_entry in enumerate(bom[i:]):
        # doesn't work, even though you'd be O(NlogN) (I think)
        # ok, I just checked
        #     for j, j_entry in enumerate(bom[i-1:]):
        # and even that didn't work (although bom[i:] and bom[i-1:] worked on a
        # simple test case in reduce_dicts.py
        for j, j_entry in enumerate(bom):
            logging.debug("reduce_bom i = {}, j = {}".format(i, j))
            if is_same_part(i_entry, j_entry) and i != j:
                try:
                    i_entry["qty"] += j_entry["qty"]
                    logging.debug("entry {} is the same as entry {}"
                                  "".format(i, j))
                    del bom[j]  # deletes jth element of bom
                except KeyError as e:
                    logging.error("Couldn't get quantities ({})"
                                  "".format(e))
                    raise e
                except TypeError as e:
                    logging.error("Couldn't add quantities '{}' and '{}'"
                                  "({})"
                                  "".format(i_entry["qty"],
                                            j_entry["qty"],
                                            e))
                    raise e
    return


def add_boms(bom1=[{}], bom2=[{}]):
    # boms are set to be a list of a single empty dictionary, which is the
    # bom-equivalent of null/None, except that I can actually get the list of
    # keys and stuff like that
    #
    # anyway, this will just work as a naive addition of boms that will then
    # call a reduction function that will take care of duplicate entries by
    # adding the quanties together
    #
    # there's also an assumption that bomX[0]...bomX[N] all have the same keys,
    # but given that all boms that make it to this function should have been
    # constructed such that the assumption is true, it's probably not an issue
    new_bom = []
    try:
        # note that the set takes care of repeats in the keys
        new_keys = set(list(bom1[0].keys()) + list(bom2[0].keys()))
        # actually, you don't need to filter, you just need to skip empty lines
        # logging.debug("new_keys (pre-filtering): {}".format(new_keys))
        # # filter out the None elements that result if one of the boms is empty
        # # filter(lambda x: x is not None, new_keys)
        # filter('', new_keys)
        # logging.debug("new_keys (post-filtering): {}".format(new_keys))
    except IndexError as e:  # calling bomX[0]
        logging.error(e)
        raise e
    except AttributeError as e:  # calling .keys() error
        logging.error(e)
        raise e

    for entry in (bom1 + bom2):
        # check that entry is nonempty, otherwise it adds a bunch of Nones to
        # your bom, which is annoying
        if entry:
            new_entry = {}
            for key in new_keys:
                try:
                    new_entry[key] = entry[key]
                # this is expected at least some of the time
                except KeyError as e:
                    logging.debug("{} does not have key '{}'"
                                  "".format(entry, key))
                    new_entry[key] = ""  # was None, but "" looks better
            new_bom.append(new_entry)
    reduce_bom(new_bom)
    return new_bom


def print_bom(bom):
    # sort the bom by package, then device
    # see
    # http://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-values-of-the-dictionary-in-python
    bom.sort(key=itemgetter("package", "device"))  # this way
    # bom.sort(key=itemgetter("device", "package"))  # not this way
    if "part#" in bom[0].keys():
        headings = ['qty', 'value', 'device', 'package', 'part#']
        tabulate_headers = {"qty": "Qty",
                            "value": "Value",
                            "part#": "Part #",
                            "device": "Device",
                            "package": "Package"}
        # header = "Qty\tValue\tDevice\tPackage\tPart #"
        # print()
        # print(header)
        # print('=' * len(header))
        # for br in bom:
        #     print("{qty}\t{value}\t{device}\t{package}\t{part_num}"
        #           "".format(qty=br["qty"],
        #                     value=br["value"],
        #                     device=br["device"],
        #                     package=br["package"],
        #                     part_num=br["part#"] if br["part#"] is not None
        #                         else ''))
    else:
        headings = ['qty', 'value', 'device', 'package']
        tabulate_headers = {"qty": "Qty",
                            "value": "Value",
                            "device": "Device",
                            "package": "Package"}
        # header = "Qty\tValue\tDevice\tPackage"
        # print()
        # print(header)
        # print('=' * len(header))
        # for br in bom:
        #     print("{qty}\t{value}\t{device}\t{package}"
        #           "".format(qty=br["qty"],
        #                     value=br["value"],
        #                     device=br["device"],
        #                     package=br["package"]))

    # this is better for an actual csv output
    with open("test-csv-output.csv", "w") as csv_out:
        writer = csv.DictWriter(csv_out, headings, dialect="eagle")

        writer.writerow(dict(zip(headings, headings)))  # include heading on top
        for row in bom:
            row_to_write = {}
            for heading in headings:
                row_to_write[heading] = row[heading]
            writer.writerow(row_to_write)

    # I was using a list of dicts before, which tabulate can handle, but the
    # problem is that dicts aren't ordered
    bom_table = []
    for row in bom:
        bom_table_row = []
        for heading in headings:
            bom_table_row.append(row[heading])
        bom_table.append(bom_table_row)

    print(tabulate(bom_table, headers=headings))
    return


# # print(glob.glob("*.csv"))
# csv_files = glob.glob("*.csv")

# boms = []
# for csv_file in csv_files:
#     with open(csv_file) as csvf:
#         bom = []
#         ordered_bom_keys = []
#         # using csv.DictReader actually seems nontrivial for files whose
#         # fieldnames are not constant (the # of attributes may be different),
#         # so it's probably just easier to roll your own dictionary based off of
#         # the headers in the first line
#         reader = csv.reader(csvf, "eagle")
#         for i, row in enumerate(reader):
#             if i == 0:
#                 for elem in row:
#                     ordered_bom_keys.append(elem.lower())
#             else:
#                 bom_row = {}
#                 for i, elem in enumerate(row):
#                     # turn quantities into ints so you can add them
#                     if ordered_bom_keys[i] == "qty":
#                         try:
#                             bom_row[ordered_bom_keys[i]] = int(elem)
#                         except ValueError as e:
#                             logging.error("Had issue int-ifying {elem} ({e})"
#                                           "".format(elem=elem, e=e))
#                             bom_row[ordered_bom_keys[i]] = elem
#                     else:
#                         bom_row[ordered_bom_keys[i]] = elem
#                 valid_part = True
#                 for ignore_frag in IGNORE_DEVICE_FRAGMENTS:
#                     if ignore_frag in bom_row["device"]:
#                         valid_part = False
#                 if valid_part:
#                     bom.append(bom_row)
#         boms.append(bom)


raw_boms = []
for csv_file in bom_files:
    named_bom = {}
    try:
        with open(csv_file["path"]) as csvf:
            bom = []
            ordered_bom_keys = []
            # using csv.DictReader actually seems nontrivial for files whose
            # fieldnames are not constant (the # of attributes may be
            # different), so it's probably just easier to roll your own
            # dictionary based off of the headers in the first line
            reader = csv.reader(csvf, "eagle")
            for i, row in enumerate(reader):
                if i == 0:
                    for elem in row:
                        ordered_bom_keys.append(elem.lower())
                else:
                    bom_row = {}
                    for i, elem in enumerate(row):
                        # turn quantities into ints so you can add them
                        if ordered_bom_keys[i] == "qty":
                            try:
                                bom_row[ordered_bom_keys[i]] = int(elem)
                            except ValueError as e:
                                logging.error("Had issue int-ifying {elem} "
                                              "({e})"
                                              "".format(elem=elem, e=e))
                                bom_row[ordered_bom_keys[i]] = elem
                        else:
                            bom_row[ordered_bom_keys[i]] = elem
                    valid_part = True
                    for ignore_frag in IGNORE_DEVICE_FRAGMENTS:
                        try:
                            if ignore_frag in bom_row["device"]:
                                valid_part = False
                        except KeyError as e:
                            logging.error("bom_row '{}' should have a key "
                                          "'device' ({})"
                                          "".format(bom_row, e))
                    if valid_part:
                        bom.append(bom_row)
        named_bom["bom"] = bom
        named_bom["name"] = csv_file["name"]
        named_bom["qty"] = csv_file["qty"]
        raw_boms.append(named_bom)
    except FileNotFoundError as e:
        logging.error("Can't find file at {} ({}); moving on..."
                      "".format(csv_file["path"], e))

# print(raw_boms)
# print(type(raw_boms))
# print(type(raw_boms[0]))
# print(raw_boms[0])
# print_bom(raw_boms[0]["bom"])
# print_bom(multiply_bom(raw_boms[0]["bom"], raw_boms[0]["qty"]))
# print_bom(add_boms(multiply_bom(raw_boms[0]["bom"], raw_boms[0]["qty"]),
#                    multiply_bom(raw_boms[0]["bom"], raw_boms[0]["qty"] * 3)))
# EMPTY_BOM = [{}]
# collector_bom = EMPTY_BOM  # initialize

# full_boms = []
for i, raw_bom in enumerate(raw_boms):
    logging.debug("raw_bom: {}".format(raw_bom))
    if i == 0:
        collector_bom = multiply_bom(raw_bom["bom"], raw_bom["qty"])
    else:
        collector_bom = add_boms(multiply_bom(raw_bom["bom"], raw_bom["qty"]),
                                 collector_bom)

    # full_boms.append(
#     add_boms(multiply_bom(raw_bom["bom"], raw_bom["qty"]),
#              collector_bom)
print_bom(collector_bom)

# for full_bom in full_boms:
#     print_bom(full_bom)

# print_bom(add_boms(full_boms[0], full_boms[1]))
# print("collector_bom: {}, collector_bom[0]: {}, collector_bom[0].keys(): {}"
#       "".format(collector_bom,
#                 collector_bom[0],
#                 collector_bom[0].keys()))
# print_bom(add_boms(collector_bom, full_bom[0]))


# these are all obsolete calls
# # print_bom(multiply_bom(raw_boms[0], 6))
# # print_bom(add_boms(raw_boms[0]))  # should just be itself
# # print_bom(add_boms(raw_boms[0], raw_boms[0]))  # should be doubled
