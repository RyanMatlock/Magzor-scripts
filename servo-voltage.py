#!/usr/local/bin/python3
"""
servo-voltage.py

2014-06-19

Calculates drop across servo whose ground terminal is connected to the drain of
a IRLZ44 MOSFET and is switch on by an LM311 (check your notes if you've
forgotten what you mean by this).  In any case, I just didn't want to use a
spreadsheet for this.
"""

# gleaned from IRLZ44 datasheet for Tj = 25°C
Vds = 20
# 2-tuple of Vgs (V) and Ids (A)
# because the comparator feeding the gate of the MOSFET is open collector (I
# think), Vgs = Vcc (convenient!)
Vgs_Ids_pairs = [(5,100),
                 (5.5,120),
                 (6,130),
                 (6.5,140)]

# I want to know the voltage drop across the servo for given values of servo
# current (in amps), which have been estimated during testing
step = 0.5
# apparently Python doesn't like float step sizes
#servo_currents = range(0.25, 3.5 + step, step)

# Stack Overflow to the rescue!
def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step
# source: http://stackoverflow.com/questions/477486/python-decimal-range-step-value/20549652

x_servo_currents = drange(0.25, 3.5 + step, step)

# because of the range x_servo_currents is defined, it's not actually a list,
# so if you step through it once, you can't do it again.  as such, I need to
# build a list out of x_servo_currents that I can continually step through
servo_currents = []

for i in x_servo_currents:
    servo_currents.append(i)

with open("servo-voltages.txt","w") as out:
    out.write("955 servos, IRLZ44 MOSFET, Spiderbot/Lazarus 2014-06-19" +
              " estimates\n")
    for pair in Vgs_Ids_pairs:
        Vgs, Ids = pair[0], pair[1]
        # out.write("{}, {}".format(Vgs, Ids))
        Rds = Vgs / Ids
        out.write("Vgs = {:.1f},Rds = {:.5f}:\n".format(Vgs, Rds))
        Vcc = Vgs
        out.write("  I guess (A)\tVservo (V)\tVdrop (mV)\tItotal (A)\t" +
                  "Iservo (A)\n")

        for I in servo_currents:
            Rservo = Vcc / I
            Rtotal = Rservo + Rds
            Itotal = Vcc / Rtotal
            # MOSFET and servo form a voltage divider where R1 = servo,
            # R2 = MOSFET
            Vmosfet = Vcc * (Rds / Rtotal)
            Vservo = Vcc - Vmosfet
            Iservo = Vservo / Rservo
            out.write("  {:.2f}\t\t{:.3f}\t\t{:.0f}\t\t{:.3f}\t\t{:.3f}\n"\
                      .format(I, Vservo, Vmosfet * 1000, Itotal, Iservo))

print("finished writing")
