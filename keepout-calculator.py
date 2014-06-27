"""
keepout-calculator.py

takes in a target keepout size (and, optionally, starting inner radius once I
get around to that)  and returns appropriate width and radius values

when the minimum inner radius is zero, the width is simply half the diameter
and the radius is a quarter the diameter (draw it out and it'll make sense if
you're confused)
"""

while(True):
    try:
        keepout_diameter = float(input("enter keepout diameter: "))
        keepout_min_radius = float(input("enter minimum radius: "))
        break
    except ValueError:
        pass

